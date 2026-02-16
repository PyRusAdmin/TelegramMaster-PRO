# -*- coding: utf-8 -*-
import asyncio
import random
import sys
import time
from datetime import datetime  # Импортируем класс datetime

import flet as ft
from loguru import logger
from telethon import events, TelegramClient
from telethon.errors import (
    ChannelPrivateError, ChatAdminRequiredError, ChatWriteForbiddenError, FloodWaitError, PeerFloodError,
    SlowModeWaitError, UserBannedInChannelError, UserIdInvalidError, UsernameInvalidError, UsernameNotOccupiedError,
    UserNotMutualContactError, ForbiddenError
)
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import CheckChatInviteRequest

from src.core.configs import (
    BUTTON_HEIGHT, WIDTH_WIDE_BUTTON, path_folder_with_messages
)
from src.core.database.account import getting_account, get_account_list
from src.core.database.database import (
    select_records_with_limit, write_group_send_message_table, get_links_table_group_send_messages,
    update_group_send_messages_table
)
from src.core.utils import Utils
from src.features.account.connect import TGConnect
from src.features.account.subscribe import Subscribe
from src.gui.gui import list_view, AppLogger
from src.gui.gui_elements import GUIProgram
from src.locales.translations_loader import translations


class SendTelegramMessages:
    """
    Отправка (текстовых) сообщений в личку Telegram пользователям из базы данных.
    """

    def __init__(self, page: ft.Page):
        """
        Инициализация класса для отправки сообщений в Telegram.

        :param page: Страница интерфейса Flet для отображения элементов управления
        """
        self.page = page
        self.connect = TGConnect(page=page)
        self.file_extension = "json"
        self.app_logger = AppLogger(page=page)
        self.utils = Utils(page=page)
        self.gui_program = GUIProgram(page=page)
        self.session_string = getting_account()  # Получаем строку сессии из файла базы данных
        self.subscribe = Subscribe(page=page)  # Инициализация экземпляра класса Subscribe (Подписка)
        self.account_data = get_account_list()  # Получаем список аккаунтов из базы данных
        self.tb_time_from = ft.TextField(
            label="Время сна от",
            expand=True,  # Полноразмерное расширение (при изменении размера окна, подстраивается под размер)
            hint_text="Введите время",
        )
        self.tb_time_to = ft.TextField(
            label="Время сна до",
            expand=True,  # Полноразмерное расширение
            hint_text="Введите время",
        )
        # Поле для формирования списка чатов
        self.chat_list_field = ft.TextField(
            label="Формирование списка чатов",
            expand=True,  # Полноразмерное расширение (при изменении размера окна, подстраивается под размер)
            multiline=True,
            min_lines=5,  # Минимальное количество строк
            max_lines=5,  # Максимальное количество строк
        )
        # Поле для текста автоответчика
        self.auto_reply_text_field = ft.TextField(
            label="Автоответчик: текст ответа",  # Заголовок поля
            expand=True,  # Полноразмерное расширение (при изменении размера окна, подстраивается под размер)
            multiline=True,  # Многострочное поле
            min_lines=5,  # Минимальное количество строк
            max_lines=5,  # Максимальное количество строк
            hint_text="Введите сообщение для автоответа...",  # Подсказка
        )
        # Поле для ввода лимита на сообщения
        self.limits = ft.TextField(
            label="Введите лимит на сообщения",
            expand=True,  # Полноразмерное расширение (при изменении размера окна, подстраивается под размер)
        )
        # Кнопки-переключатели
        self.send_message_personal_switch = ft.CupertinoSwitch(
            label="Рассылка сообщений в личку",
            value=False,
            disabled=True
        )
        self.send_message_group_switch = ft.CupertinoSwitch(
            label="Рассылка сообщений по чатам",
            value=False,
            disabled=True
        )

    """Рассылка сообщений по чатам"""

    async def sending_messages_files_via_chats(self) -> None:
        """
        Отображает интерфейс для рассылки сообщений и файлов по чатам Telegram.

        :return: None
        """
        list_view.controls.clear()  # ✅ Очистка логов перед новым запуском
        account_drop_down_list = self.gui_program.create_account_dropdown(self.account_data)

        async def performing_operation(chat_list_fields: list, min_seconds, max_seconds) -> None:
            """
            Выполняет рассылку сообщений по чатам или работу с автоответчиком.

            :param chat_list_fields: Список ссылок на группы для рассылки
            :param min_seconds: минимальная задержка между действиям
            :param max_seconds: максимально возможной случайной временной интервале
            :return: None
            """
            logger.warning(f"Выбранный аккаунт: {account_drop_down_list.value}")
            # Определяем, какие сессии использовать

            # === РЕЖИМ АВТООТВЕТЧИКА ===
            try:
                # Пользователь должен сам выбрать аккаунт
                # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
                start = await self.app_logger.start_time()
                client: TelegramClient = await self.connect.client_connect_string_session(
                    session_name=account_drop_down_list.value)

                @client.on(events.NewMessage(incoming=True))  # Обработчик личных сообщений
                async def handle_private_messages(event):
                    """Обрабатывает входящие личные сообщения"""
                    if event.is_private:  # Проверяем, является ли сообщение личным
                        await self.app_logger.log_and_display(message=f"📩 Входящее сообщение: {event.message.message}")
                        reply_text = self.auto_reply_text_field.value or "Спасибо за сообщение! Мы ответим позже."
                        await event.respond(reply_text)
                        await self.app_logger.log_and_display(f"🤖 Ответ отправлен: {reply_text}")

                # Получаем список чатов, которым нужно отправить сообщение
                await self.app_logger.log_and_display(message=f"Всего групп: {len(chat_list_fields)}")
                for group_link in chat_list_fields:
                    try:
                        # Подписываемся на группы
                        await self.subscribe.subscribe_to_group_or_channel(client=client, groups=group_link)
                        # Находит все файлы в папке с сообщениями и папке с файлами для отправки.
                        messages, files = await self.all_find_and_all_files()
                        # Отправляем сообщения и файлы в группу
                        await send_content(
                            client=client,
                            target=group_link,
                            messages=messages,
                            files=files
                        )
                    except ChannelPrivateError:
                        await self.app_logger.log_and_display(
                            message=f"🔒 Группа {group_link} приватная или недоступна.")
                    except PeerFloodError:
                        break  # Прерываем работу и меняем аккаунт
                    except FloodWaitError as e:
                        await self.app_logger.log_and_display(
                            message=f"{translations['ru']['errors']['flood_wait']}{e}",
                            level="error"
                        )
                        await asyncio.sleep(e.seconds)
                    except UserBannedInChannelError:
                        await self.app_logger.log_and_display(
                            message=f"❌ Запрещено отправлять сообщения в супергруппы/каналы."
                        )
                    except ChatAdminRequiredError:  # TODO проверить функцию и добавить удаление группы по списка
                        await self.app_logger.log_and_display(
                            message=translations["ru"]["errors"]["admin_rights_required"])
                    except ChatWriteForbiddenError:
                        await self.app_logger.log_and_display(
                            message=translations["ru"]["errors"]["chat_write_forbidden"])
                        break  # Прерываем работу и меняем аккаунт
                    except SlowModeWaitError as e:
                        await self.app_logger.log_and_display(
                            message=f"{translations["ru"]["errors"]["slow_mode_wait"]}{e}")
                        await asyncio.sleep(e.seconds)
                    except ValueError:
                        await self.app_logger.log_and_display(
                            message=f"❌ Ошибка рассылки, проверьте ссылку: {group_link}"
                        )
                        await self.app_logger.log_and_display(
                            message=translations["ru"]["errors"]["sending_error_check_link"])
                    except (TypeError, UnboundLocalError):
                        continue  # Записываем ошибку в software_database.db и продолжаем работу
                    except Exception as error:
                        logger.exception(error)
                    finally:
                        await self.utils.random_dream(
                            min_seconds=min_seconds,
                            max_seconds=max_seconds
                        )  # Прерываем работу и меняем аккаунт

                # await client.run_until_disconnected()  # Запускаем программу и ждем отключения клиента

                await self.app_logger.log_and_display(message="🔚 Конец отправки сообщений + файлов по чатам")
                await self.app_logger.end_time(start)

            except Exception as error:
                logger.exception(error)

        async def send_content(client, target, messages, files):
            """
            Отправляет сообщения и файлы в указанную цель (личку или группу).

            :param client: Экземпляр клиента Telegram
            :param target: Ссылка на группу или личку
            :param messages: Список сообщений для отправки
            :param files: Список файлов для отправки
            :return: None
            """
            await self.app_logger.log_and_display(f"Отправляем сообщение: {target}")
            if not messages:
                for file in files:
                    await client.send_file(target, f"user_data/files_to_send/{file}")
                    await self.app_logger.log_and_display(f"Файл {file} отправлен в {target}.")
            else:
                message = await self.select_and_read_random_file(messages, folder="message")
                if not files:
                    try:
                        await client.send_message(entity=target, message=message)
                    except AttributeError:
                        logger.warning("Не валидный аккаунт, выполните проверку аккаунтов")
                    except ForbiddenError as e:
                        if "ALLOW_PAYMENT_REQUIRED" in str(e):
                            await self.app_logger.log_and_display(
                                f"❌ Невозможно отправить сообщение: пользователь закрыл личку от незнакомцев.",
                                level="warning"
                            )
                    except UsernameInvalidError:
                        await self.app_logger.log_and_display(
                            message=translations["ru"]["errors"]["invalid_username"]
                        )
                else:
                    for file in files:
                        await client.send_file(target, f"user_data/files_to_send/{file}", caption=message)
                        await self.app_logger.log_and_display(f"Сообщение и файл отправлены: {target}")

            # await self.utils.random_dream(
            #     min_seconds=min_seconds,
            #     max_seconds=max_seconds
            # )  # Прерываем работу и меняем аккаунт

        async def checking_links_group(_):
            """Проверка ссылок пользователя для рассылки с детальной информацией"""
            logger.info("Проверяю ссылки")
            logger.warning(f"Выбранный аккаунт: {account_drop_down_list.value}")

            client: TelegramClient = await self.connect.client_connect_string_session(
                session_name=account_drop_down_list.value
            )

            writing_group_links = get_links_table_group_send_messages()

            for raw_link in writing_group_links:
                link = raw_link.strip()
                logger.info(f"Обрабатываю ссылку: '{link}'")

                try:
                    entity = None
                    full_entity = None

                    # Обработка приглашений (ссылки вида https://t.me/+hash)
                    if '/+' in link or link.startswith('https://t.me/+'):
                        hash_part = link.split('+')[-1].strip()
                        invite = await client(CheckChatInviteRequest(hash_part))
                        if hasattr(invite, 'chat') and invite.chat:
                            entity = invite.chat
                            full_entity = await client(GetFullChannelRequest(entity))
                            logger.info(f"✅ Приглашение обработано: {entity.title}")
                        else:
                            logger.warning(f"⚠️ Не удалось обработать приглашение: {link}")
                            continue

                    # Обычная публичная ссылка
                    elif link.startswith(('https://t.me/', 'http://t.me/')):
                        # Извлекаем username: удаляем домен и часть с сообщением
                        username = link.split('t.me/')[-1].split('?')[0].split('/')[0].strip()

                        if not username or username.startswith('+'):
                            logger.warning(f"⚠️ Пропускаю некорректную ссылку: {link}")
                            continue

                        # Получаем entity
                        entity = await client.get_entity(username)
                        full_entity = await client(GetFullChannelRequest(channel=entity))

                    else:
                        # Прямой username без https
                        entity = await client.get_entity(link)
                        full_entity = await client(GetFullChannelRequest(channel=entity))

                    # Если получили данные - обрабатываем
                    if entity and full_entity:

                        # Извлекаем права доступа
                        banned_rights = getattr(entity, 'default_banned_rights', None)

                        # Собираем базовую информацию в словарь
                        channel_info = {
                            'id': getattr(full_entity.full_chat, 'id', entity.id),
                            'title': getattr(entity, 'title', 'Без названия'),
                            'username': getattr(entity, 'username', None),
                            'about': getattr(full_entity.full_chat, 'about', None),
                            'participants_count': getattr(full_entity.full_chat, 'participants_count', None),
                            'participants_hidden': getattr(full_entity.full_chat, 'participants_hidden', False),
                            'is_broadcast': getattr(entity, 'broadcast', False),
                            'is_megagroup': getattr(entity, 'megagroup', False),
                            'level': getattr(entity, 'level', None),
                            'slowmode_seconds': getattr(full_entity.full_chat, 'slowmode_seconds', 0),
                            'pinned_msg_id': getattr(full_entity.full_chat, 'pinned_msg_id', None),
                            'can_view_participants': getattr(full_entity.full_chat, 'can_view_participants', False),
                            'reactions_limit': getattr(full_entity.full_chat, 'reactions_limit', None),
                            'can_set_username': getattr(full_entity.full_chat, 'can_set_username', False),
                            'can_view_stats': getattr(full_entity.full_chat, 'can_view_stats', False),
                            'paid_media_allowed': getattr(full_entity.full_chat, 'paid_media_allowed', False),
                            'paid_reactions_available': getattr(full_entity.full_chat, 'paid_reactions_available',
                                                                False),
                            'paid_messages_available': getattr(full_entity.full_chat, 'paid_messages_available', False),
                            'stargifts_available': getattr(full_entity.full_chat, 'stargifts_available', False),
                            'stargifts_count': getattr(full_entity.full_chat, 'stargifts_count', 0),
                            'antispam': getattr(full_entity.full_chat, 'antispam', False),
                            'translations_disabled': getattr(full_entity.full_chat, 'translations_disabled', True),
                            'linked_chat_id': getattr(full_entity.full_chat, 'linked_chat_id', None),
                            'default_banned_rights': banned_rights,
                            'available_reactions': getattr(full_entity.full_chat, 'available_reactions', None),
                        }

                        # Обрезаем описание до 200 символов с многоточием
                        about_text = channel_info['about']
                        if about_text and len(about_text) > 200:
                            about_text = about_text[:200] + '...'

                        # Определяем права на отправку контента из banned_rights
                        can_send_messages = not (banned_rights.send_messages if banned_rights else False)
                        can_send_media = not (banned_rights.send_media if banned_rights else False)
                        can_send_photos = not (banned_rights.send_photos if banned_rights else False)
                        can_send_videos = not (banned_rights.send_videos if banned_rights else False)
                        can_send_docs = not (banned_rights.send_docs if banned_rights else False)
                        can_send_audios = not (banned_rights.send_audios if banned_rights else False)
                        can_send_voices = not (banned_rights.send_voices if banned_rights else False)
                        can_send_roundvideos = not (banned_rights.send_roundvideos if banned_rights else False)
                        can_send_stickers = not (banned_rights.send_stickers if banned_rights else False)
                        can_send_gifs = not (banned_rights.send_gifs if banned_rights else False)
                        can_send_polls = not (banned_rights.send_polls if banned_rights else False)
                        can_embed_links = not (banned_rights.embed_links if banned_rights else False)
                        can_invite_users = not (banned_rights.invite_users if banned_rights else False)

                        chat_type_display = (
                            "📢 Канал" if channel_info['is_broadcast']
                            else "👥 Супергруппа" if channel_info['is_megagroup']
                            else "👥 Группа"
                        )

                        update_group_send_messages_table(
                            link=link,
                            telegram_id=channel_info['id'],
                            title=channel_info['title'],
                            username=channel_info['username'] if channel_info['username'] else 'отсутствует',
                            about=about_text,
                            participants_count=channel_info['participants_count'],
                            participants_hidden=channel_info['participants_hidden'],
                            type_display=chat_type_display,
                            level=channel_info['level'],
                            slowmode_seconds=channel_info['slowmode_seconds'],
                            can_send_messages=can_send_messages,
                            can_send_media=can_send_media,
                            can_send_photos=can_send_photos,
                            can_send_videos=can_send_videos,
                            can_send_docs=can_send_docs,
                            can_send_audios=can_send_audios,
                            can_send_voices=can_send_voices,
                            can_send_roundvideos=can_send_roundvideos,
                            can_send_stickers=can_send_stickers,
                            can_send_gifs=can_send_gifs,
                            can_send_polls=can_send_polls,
                            can_embed_links=can_embed_links,
                            can_invite_users=can_invite_users,
                            reactions_limit=channel_info['reactions_limit'],
                            available_reactions=str(channel_info['available_reactions']) if channel_info[
                                'available_reactions'] else None,
                            paid_media_allowed=channel_info['paid_media_allowed'],
                            paid_reactions_available=channel_info['paid_reactions_available'],
                            paid_messages_available=channel_info['paid_messages_available'],
                            stargifts_available=channel_info['stargifts_available'],
                            stargifts_count=channel_info['stargifts_count'],
                            antispam=channel_info['antispam'],
                            translations_disabled=channel_info['translations_disabled'],
                            linked_chat_id=channel_info['linked_chat_id'],
                            last_checked=datetime.now(),  # ← Текущее время
                            is_active=True  # ← Группа активна (проверена сейчас)
                        )

                        # Детальный вывод в логи с расшифровкой
                        # logger.info(
                        #     f"✅ Канал '{channel_info['title']}' (участников: {channel_info['participants_count']})")
                        # logger.info(
                        #     f"ID: {channel_info['id']}, Username: @{channel_info['username'] if channel_info['username'] else 'отсутствует'}, Тип: {'📢 Broadcast канал' if channel_info['is_broadcast'] else '👥 Мегагруппа' if channel_info['is_megagroup'] else '👥 Обычная группа'}")
                        # if channel_info['about']:
                        #     logger.info(
                        #         f"Описание: {channel_info['about'][:200]}{'...' if len(channel_info['about']) > 200 else ''}")
                        # if channel_info['participants_count']:
                        #     logger.info(f"Участников: {channel_info['participants_count']:,}")
                        # else:
                        #     logger.info(f"Участников: скрыто")

                        # Slowmode - детальная расшифровка
                        # logger.info(f"\n⏱️  SLOWMODE (ЗАДЕРЖКА МЕЖДУ СООБЩЕНИЯМИ):")
                        # if channel_info['slowmode_seconds']:
                        #     seconds = channel_info['slowmode_seconds']
                        #     hours = seconds // 3600
                        #     minutes = (seconds % 3600) // 60
                        #     secs = seconds % 60
                        #     time_parts = []
                        #     if hours > 0:
                        #         time_parts.append(f"{hours} ч")
                        #     if minutes > 0:
                        #         time_parts.append(f"{minutes} мин")
                        #     if secs > 0:
                        #         time_parts.append(f"{secs} сек")
                        #     time_str = " ".join(time_parts)
                        #     logger.info(f"⚠️  АКТИВЕН: {seconds} секунд ({time_str})")
                        #     logger.info(f"❌ МОЖНО ПИСАТЬ РАЗ В {time_str.upper()}")
                        # else:
                        #     logger.info(f"✅ ОТСУТСТВУЕТ - можно писать без задержки")
                        # Права на отправку сообщений
                        # logger.info(f"\n🔐 ПРАВА НА ОТПРАВКУ СООБЩЕНИЙ:")
                        # if channel_info['default_banned_rights']:
                        #     rights = channel_info['default_banned_rights']
                        #     logger.info(
                        #         f"{'✅ ОТПРАВКА ТЕКСТОВЫХ СООБЩЕНИЙ: разрешена' if rights.send_messages else '❌ ОТПРАВКА ТЕКСТОВЫХ СООБЩЕНИЙ: ЗАПРЕЩЕНА'}")
                        #     Медиа
                        # if rights.send_media:
                        #     logger.info(f"❌ ОТПРАВКА МЕДИА (фото/видео/файлы): ЗАПРЕЩЕНА")
                        # else:
                        #     logger.info(f"✅ ОТПРАВКА МЕДИА: разрешена")
                        # Детализация медиа
                        # media_restrictions = []
                        # if rights.send_photos:
                        #     media_restrictions.append("❌ Фото: запрещены")
                        # if rights.send_videos:
                        #     media_restrictions.append("❌ Видео: запрещены")
                        # if rights.send_docs:
                        #     media_restrictions.append("❌ Документы: запрещены")
                        # if rights.send_audios:
                        #     media_restrictions.append("❌ Аудио: запрещены")
                        # if rights.send_voices:
                        #     media_restrictions.append("❌ Голосовые: запрещены")
                        # if rights.send_roundvideos:
                        #     media_restrictions.append("❌ Кружки: запрещены")
                        # if media_restrictions:
                        #     for r in media_restrictions:
                        #         logger.info(f"      {r}")

                        # logger.info(f"{'✅ СТИКЕРЫ: разрешены' if rights.send_stickers else '❌ СТИКЕРЫ: запрещены'}")
                        # logger.info(f"{'✅ GIF: разрешены' if rights.send_gifs else '❌ GIF: запрещены'}")
                        # logger.info(
                        #     f"{'✅ ВСТАВКА ССЫЛОК: разрешена' if rights.embed_links else '❌ ВСТАВКА ССЫЛОК: запрещена'}")
                        # logger.info(f"{'✅ ОПРОСЫ: разрешены' if rights.send_polls else '❌ ОПРОСЫ: запрещены'}")
                        # logger.info(
                        #     f"{'✅ ПРИГЛАШЕНИЕ ПОЛЬЗОВАТЕЛЕЙ: разрешено' if rights.invite_users else '❌ ПРИГЛАШЕНИЕ ПОЛЬЗОВАТЕЛЕЙ: запрещено'}")
                        # if rights.change_info:
                        #     logger.info(f"❌ ИЗМЕНЕНИЕ ИНФОРМАЦИИ: запрещено")
                        # if rights.pin_messages:
                        #     logger.info(f"❌ ЗАКРЕПЛЕНИЕ СООБЩЕНИЙ: запрещено")
                        # else:
                        #     logger.info(f"✅ ВСЕ ПРАВА: разрешены (нет ограничений)")
                        # Видимость и приватность
                        # logger.info(f"\n👁️ВИДИМОСТЬ И ПРИВАТНОСТЬ:")
                        # if channel_info['can_view_participants']:
                        #     logger.info(f"✅ СПИСОК УЧАСТНИКОВ: можно просматривать")
                        # else:
                        #     logger.info(f"❌ СПИСОК УЧАСТНИКОВ: скрыт")
                        # if channel_info['participants_hidden']:
                        #     logger.info(f"🔒 УЧАСТНИКИ СКРЫТЫ: от публичного просмотра")
                        # Реакции
                        # logger.info(f"\n❤️РЕАКЦИИ:")
                        # if channel_info['reactions_limit']:
                        #     logger.info(f"Лимит: {channel_info['reactions_limit']} реакций на сообщение")
                        #     if channel_info['available_reactions']:
                        #         if hasattr(channel_info['available_reactions'], 'reactions'):
                        #             emojis = [r.emoticon for r in channel_info['available_reactions'].reactions if
                        #                       hasattr(r, 'emoticon')]
                        #             if emojis:
                        #                 logger.info(f"Доступные: {' '.join(emojis)}")
                        #         elif hasattr(channel_info['available_reactions'], 'allow_custom'):
                        #             logger.info(f"✅ Разрешены кастомные реакции")
                        # else:
                        #     logger.info(f"   Реакции отключены")
                        # Платные функции
                        # logger.info(f"\n💰 ПЛАТНЫЕ ФУНКЦИИ:")
                        # paid_features = []
                        # if channel_info['paid_media_allowed']:
                        #     paid_features.append("✅ Платные медиа: разрешены")
                        # if channel_info['paid_reactions_available']:
                        #     paid_features.append("✅ Платные реакции: доступны")
                        # if channel_info['paid_messages_available']:
                        #     paid_features.append("✅ Платные сообщения: доступны")
                        # if channel_info['stargifts_available']:
                        #     paid_features.append("✅ Звездные подарки: доступны")
                        # if paid_features:
                        #     for f in paid_features:
                        #         logger.info(f"{f}")
                        # else:
                        #     logger.info(f"❌ Платные функции недоступны")
                        # Дополнительные функции
                        # logger.info(f"\n⚙️  ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ:")
                        # features = []
                        # if channel_info['antispam']:
                        #     features.append("🛡️ Антиспам включен")
                        # if not channel_info['translations_disabled']:
                        #     features.append("🌐 Автоперевод включен")
                        # else:
                        #     features.append("❌ Автоперевод отключен")
                        # if channel_info['can_set_username']:
                        #     features.append("✏️ Можно изменять username")
                        # if channel_info['can_view_stats']:
                        #     features.append("📈 Доступна статистика")
                        # if channel_info['linked_chat_id']:
                        #     features.append(f"🔗 Есть связанный чат (ID: {channel_info['linked_chat_id']})")
                        # if features:
                        #     for f in features:
                        #         logger.info(f"{f}")
                        # else:
                        #     logger.info(f"Стандартные настройки")
                        # Боты (если есть)
                        # if hasattr(full_entity, 'users') and full_entity.users:
                        #     bots = [u for u in full_entity.users if u.bot]
                        #     if bots:
                        #         logger.info(f"\n🤖 БОТЫ В ГРУППЕ ({len(bots)}):")
                        #         for bot in bots[:5]:  # Показываем первые 5
                        #
                        #             bot_name = f"@{bot.username}" if bot.username else bot.first_name
                        #             logger.info(f"{bot_name}")
                        #
                        #             if hasattr(bot, 'bot_active_users') and bot.bot_active_users:
                        #                 logger.info(f"Активных пользователей: {bot.bot_active_users:,}")
                        # if len(bots) > 5:
                        #     logger.info(f"   ... и ещё {len(bots) - 5} ботов")
                        # logger.info(f"{'=' * 100}\n")
                except ValueError as e:
                    logger.error(f"❌ Не найдена сущность для '{link}': {e}")
                except Exception as e:
                    logger.error(f"❌ Ошибка обработки '{link}': {str(e)[:100]}")

        """Рассылка сообщений в личку"""

        async def send_files_to_personal_chats() -> None:
            """
            Отображает интерфейс для отправки файлов в личные сообщения пользователей Telegram.

            :return: None
            """

            # Группа полей ввода для времени сна

            async def button_clicked(_):
                """Обработчик кнопки "Готово" """
                try:
                    min_seconds, max_seconds = await self.utils.verifies_time_range_entered_correctly(
                        min_seconds=self.tb_time_from.value,
                        max_seconds=self.tb_time_to.value
                    )
                    start = await self.app_logger.start_time()
                    # Просим пользователя ввести расширение сообщения
                    for session_name in self.session_string:  # Перебор всех сессий
                        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
                        client: TelegramClient = await self.connect.client_connect_string_session(
                            session_name=session_name
                        )
                        try:
                            for username in await select_records_with_limit(limit=int(self.limits.value),
                                                                            app_logger=self.app_logger):
                                logger.info(f"Отправляем сообщение в личку {username}")
                                await self.app_logger.log_and_display(message=f"[!] Отправляем сообщение: {username}")
                                try:
                                    user_to_add = await client.get_input_entity(username)
                                    messages, files = await self.all_find_and_all_files()
                                    await self.send_content(
                                        client=client,
                                        target=user_to_add,
                                        messages=messages,
                                        files=files,
                                        TIME_1=self.tb_time_from.value,
                                        TIME_2=self.tb_time_to.value
                                    )
                                    await self.app_logger.log_and_display(
                                        message=f"Отправляем сообщение в личку {username}. Файл {files} отправлен пользователю {username}.")
                                    await self.utils.record_inviting_results(
                                        time_range_1=min_seconds,
                                        time_range_2=max_seconds,
                                        username=username
                                    )
                                    await self.app_logger.log_and_display(message=f"Смена аккаунта, ожидайте 8 секунд")
                                    time.sleep(8)
                                except FloodWaitError as e:
                                    await self.app_logger.log_and_display(
                                        message=f"{translations["ru"]["errors"]["flood_wait"]}{e}",
                                        level="error")
                                    # await self.utils.random_dream(
                                    #     min_seconds=min_seconds,
                                    #     max_seconds=max_seconds
                                    # )
                                    break  # Прерываем работу и меняем аккаунт
                                except PeerFloodError:
                                    await self.utils.random_dream(
                                        min_seconds=min_seconds,
                                        max_seconds=max_seconds
                                    )
                                    break  # Прерываем работу и меняем аккаунт
                                except UserNotMutualContactError:
                                    await self.app_logger.log_and_display(
                                        message=translations["ru"]["errors"]["user_not_mutual_contact"])
                                except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                                    await self.app_logger.log_and_display(
                                        message=translations["ru"]["errors"]["invalid_username"])
                                except ChatWriteForbiddenError:
                                    await self.app_logger.log_and_display(
                                        message=translations["ru"]["errors"]["chat_write_forbidden"])
                                    await self.utils.random_dream(
                                        min_seconds=min_seconds,
                                        max_seconds=max_seconds
                                    )
                                    break  # Прерываем работу и меняем аккаунт
                                except (TypeError, UnboundLocalError):
                                    continue  # Записываем ошибку в software_database.db и продолжаем работу
                        except KeyError:
                            sys.exit(1)
                        await self.app_logger.end_time(start=start)
                        await self.gui_program.show_notification(  # ✅ Показываем уведомление пользователю
                            message="🔚 Конец рассылки сообщений"
                        )
                except ValueError as e:
                    await self.gui_program.show_notification(  # ✅ Показываем уведомление пользователю
                        message=f"❌ Ошибка валидации времени: {e}"
                    )
                except Exception as error:
                    logger.exception(error)
                self.page.update()

            # Разделение интерфейса на верхнюю и нижнюю части
            # self.page.views.append(
            #     ft.View(
            #         route="/sending_messages_via_chats_menu",
            #         appbar=await self.gui_program.key_app_bar(),  # Кнопка назад
            #         controls=[
            #             await self.gui_program.create_gradient_text(
            #                 text="Отправка сообщений в личку"
            #             ),
            #             list_view,  # Отображение логов 📝
            #             ft.Row(
            #                 controls=[
            #                     self.tb_time_from,
            #                     self.tb_time_to
            #                 ],
            #                 spacing=20,
            #             ),
            #             self.limits,
            #             ft.Column(  # Верхняя часть: контрольные элементы
            #                 controls=[
            #                     ft.Button(
            #                         content=translations["ru"]["buttons"]["done"],
            #                         width=WIDTH_WIDE_BUTTON,
            #                         height=BUTTON_HEIGHT,
            #                         on_click=button_clicked
            #                     )
            #                 ]
            #             )
            #         ]
            #     )
            # )

        async def button_clicked(_):
            """
            Обработчик кнопки "Готово"
            """
            write_group_send_message_table(self.chat_list_field.value)

            writing_group_links = get_links_table_group_send_messages()

            # chat_list_fields = await self.utils.get_chat_list(self.chat_list_field.value)

            if not writing_group_links:
                await self.gui_program.show_notification(
                    message="❌ Нет чатов для рассылки. Укажите ссылки или сохраните группы в настройках.")
                return

            try:
                min_seconds, max_seconds = await self.utils.verifies_time_range_entered_correctly(
                    min_seconds=self.tb_time_from.value,
                    max_seconds=self.tb_time_to.value
                )
                await performing_operation(
                    chat_list_fields=writing_group_links,
                    min_seconds=min_seconds,
                    max_seconds=max_seconds
                )
            except ValueError as e:
                await self.gui_program.show_notification(  # ✅ Показываем уведомление пользователю
                    message=f"❌ Ошибка валидации времени: {e}"
                )

        # Разделение интерфейса на верхнюю и нижнюю части
        self.page.views.append(
            ft.View(
                route="/sending_messages_via_chats_menu",
                appbar=await self.gui_program.key_app_bar(),  # Кнопка назад
                controls=[
                    await self.gui_program.create_gradient_text(
                        text=f"{translations["ru"]["message_sending_menu"]["sending_messages_files_via_chats"]} и Отправка сообщений в личку"
                    ),
                    list_view,  # Отображение логов 📝
                    account_drop_down_list,  # Выпадающий список с аккаунтами

                    ft.Row(
                        controls=[
                            self.send_message_personal_switch,  # Рассылка сообщений в личку
                            self.send_message_group_switch,  # Рассылка сообщений по чатам
                        ]
                    ),

                    self.limits,  # Ввод лимита на аккаунт при рассылках в личку

                    ft.Row(
                        controls=[
                            self.tb_time_from,
                            self.tb_time_to
                        ],
                        spacing=20,
                    ),
                    # t,
                    ft.Row(
                        controls=[
                            self.auto_reply_text_field,  # Поле для текста автоответчика
                            self.chat_list_field,  # Поле для ввода ссылок на группы
                        ],
                    ),
                    ft.Column(  # Верхняя часть: контрольные элементы
                        controls=[

                            ft.Button(
                                content="Проверка ссылок для рассылки",
                                width=WIDTH_WIDE_BUTTON,
                                height=BUTTON_HEIGHT,
                                on_click=checking_links_group
                            ),

                            ft.Button(
                                content=translations["ru"]["buttons"]["done"],
                                width=WIDTH_WIDE_BUTTON,
                                height=BUTTON_HEIGHT,
                                on_click=button_clicked
                            ),
                        ],
                    ),
                ],
            )
        )

    async def all_find_and_all_files(self):
        """
        Находит все файлы в папках с сообщениями и файлами для отправки.

        :return: Кортеж с двумя списками - сообщениями и файлами
        """
        return (await self.utils.find_files(directory_path=path_folder_with_messages, extension=self.file_extension),
                await self.utils.all_find_files(directory_path="user_data/files_to_send"))

    async def select_and_read_random_file(self, entities, folder):
        """
        Выбирает случайный файл и читает из него данные.

        :param entities: Список имён файлов (без расширения) для чтения
        :param folder: Подпапка внутри user_data (например, "message" или "answering_machine")
        :return: Содержимое JSON-файла или None при ошибке
        """
        try:
            if not entities:
                await self.app_logger.log_and_display(f"📁 Папка 'user_data/{folder}' пуста. Нет файлов для выбора.")
                return None

            random_file = random.choice(entities)
            filename = f"user_data/{folder}/{random_file[0]}.json"
            logger.info(f"Выбран файл для чтения: {filename}")
            await self.app_logger.log_and_display(f"Выбран файл для чтения: {random_file[0]}.json")
            return await self.utils.read_json_file(filename=filename)

        except Exception as error:
            await self.app_logger.log_and_display(f"⚠️ Ошибка при чтении файла из папки {folder}: {error}",
                                                  level="error")
            logger.exception(error)
            return None

# 446
