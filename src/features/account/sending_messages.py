# -*- coding: utf-8 -*-
"""
ИЗМЕНЕНИЯ:
1. performing_operation: рассылка и автоответчик работают параллельно через asyncio.gather
2. Рассылка крутится в while-цикле, автоответчик слушает входящие одновременно
3. Кнопка «Остановить» корректно прерывает оба процесса и отключает клиент
4. self._active_client хранит ссылку на клиент, чтобы stop-кнопка могла его разорвать
"""

import asyncio
import random
import sys
from datetime import datetime

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
    BUTTON_HEIGHT, path_folder_with_messages
)
from src.core.database.account import getting_account, get_account_list
from src.core.database.database import (
    write_group_send_message_table, get_links_table_group_send_messages, update_group_send_messages_table
)
from src.core.utils import Utils
from src.features.account.connect import TGConnect
from src.features.account.inviting import get_limit, load_and_validate_users
from src.features.account.subscribe import Subscribe
from src.features.account.switch_controller import ToggleController
from src.gui.gui import list_view, AppLogger
from src.gui.gui_elements import GUIProgram
from src.locales.translations_loader import translations


class SendTelegramMessages:
    """Отправка сообщений в личку и по чатам Telegram."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.connect = TGConnect(page=page)
        self.file_extension = "json"
        self.app_logger = AppLogger(page=page)
        self.utils = Utils(page=page)
        self.gui_program = GUIProgram(page=page)
        self.session_string = getting_account()
        self.subscribe = Subscribe(page=page)
        self.account_data = get_account_list()

        self.tb_time_from = ft.TextField(label="Время сна от", expand=True, hint_text="Введите время")
        self.tb_time_to = ft.TextField(label="Время сна до", expand=True, hint_text="Введите время")
        self.chat_list_field = ft.TextField(
            label="Формирование списка чатов", expand=True,
            multiline=True, min_lines=5, max_lines=5,
        )
        self.auto_reply_text_field = ft.TextField(
            label="Автоответчик: текст ответа", expand=True,
            multiline=True, min_lines=5, max_lines=5,
            hint_text="Введите сообщение для автоответа...",
        )
        self.limits = ft.TextField(
            label="Введите лимит на сообщения", expand=True,
            hint_text="Введите лимит на сообщения",
        )
        self.send_message_personal_switch = ft.CupertinoSwitch(
            label="Рассылка сообщений в личку", value=False, disabled=True
        )
        self.send_message_group_switch = ft.CupertinoSwitch(
            label="Рассылка сообщений по чатам", value=False, disabled=True
        )

        self.is_sending = False  # флаг работы рассылки
        self._active_client = None  # ← ссылка на клиент для остановки извне
        self._mailing_task = None  # ← asyncio-задача рассылки

    # ─────────────────────────────────────────────────────────
    # ГЛАВНЫЙ МЕТОД: параллельный запуск рассылки + автоответчик
    # ─────────────────────────────────────────────────────────

    async def sending_messages_files_via_chats(self) -> None:
        list_view.controls.clear()
        account_drop_down_list = self.gui_program.create_account_dropdown(self.account_data)

        # ── helpers ──────────────────────────────────────────

        async def send_content(client, target, messages, files):
            """Отправляет сообщения / файлы в цель."""
            await self.app_logger.log_and_display(f"Отправляем сообщение: {target}")
            if not messages:
                for file in files:
                    await client.send_file(target, f"user_data/files_to_send/{file}")
                    await self.app_logger.log_and_display(f"Файл {file} отправлен в {target}.")
            else:
                message = await self.select_and_read_random_file(entities=messages, folder="message")
                if not files:
                    try:
                        await client.send_message(entity=target, message=message)
                    except AttributeError:
                        logger.warning("Не валидный аккаунт, выполните проверку аккаунтов")
                    except ForbiddenError as e:
                        if "ALLOW_PAYMENT_REQUIRED" in str(e):
                            await self.app_logger.log_and_display(
                                "❌ Невозможно отправить сообщение: пользователь закрыл личку.", level="warning"
                            )
                    except UsernameInvalidError:
                        await self.app_logger.log_and_display(
                            translations["ru"]["errors"]["invalid_username"]
                        )
                else:
                    for file in files:
                        await client.send_file(target, f"user_data/files_to_send/{file}", caption=message)
                        await self.app_logger.log_and_display(f"Сообщение и файл отправлены: {target}")

        # ── цикл рассылки (запускается как asyncio-задача) ───

        async def mailing_loop(client: TelegramClient, chat_list_fields: list, min_sec, max_sec):
            """
            Бесконечный цикл рассылки по чатам.
            Работает параллельно с обработчиком автоответчика.
            """
            await self.app_logger.log_and_display(f"Всего групп: {len(chat_list_fields)}")

            while self.is_sending:
                await self.app_logger.log_and_display("🔄 Новый цикл рассылки...")

                for group_link in chat_list_fields:
                    if not self.is_sending:
                        break
                    try:
                        await self.subscribe.subscribe_to_group_or_channel(client=client, groups=group_link)
                        messages, files = await self.all_find_and_all_files()
                        await send_content(client=client, target=group_link, messages=messages, files=files)

                    except ChannelPrivateError:
                        await self.app_logger.log_and_display(f"🔒 Группа {group_link} приватная.")
                    except PeerFloodError:
                        await self.app_logger.log_and_display("⚠️ PeerFloodError — останавливаем рассылку.")
                        self.is_sending = False
                        break
                    except FloodWaitError as e:
                        await self.app_logger.log_and_display(
                            f"{translations['ru']['errors']['flood_wait']}{e}", level="error"
                        )
                        # Ждём, но проверяем флаг каждую секунду
                        for _ in range(e.seconds):
                            if not self.is_sending:
                                break
                            await asyncio.sleep(1)
                    except UserBannedInChannelError:
                        await self.app_logger.log_and_display("❌ Запрещено отправлять сообщения в супергруппы.")
                    except ChatAdminRequiredError:
                        await self.app_logger.log_and_display(
                            translations["ru"]["errors"]["admin_rights_required"]
                        )
                    except ChatWriteForbiddenError:
                        await self.app_logger.log_and_display(
                            translations["ru"]["errors"]["chat_write_forbidden"]
                        )
                        self.is_sending = False
                        break
                    except SlowModeWaitError as e:
                        await self.app_logger.log_and_display(
                            f"{translations['ru']['errors']['slow_mode_wait']}{e}"
                        )
                        for _ in range(e.seconds):
                            if not self.is_sending:
                                break
                            await asyncio.sleep(1)
                    except ValueError:
                        await self.app_logger.log_and_display(
                            f"❌ Ошибка рассылки, проверьте ссылку: {group_link}"
                        )
                    except (TypeError, UnboundLocalError):
                        continue
                    except Exception as error:
                        logger.exception(error)
                    finally:
                        # Задержка между отправками (прерываемая)
                        delay = random.randint(int(min_sec), int(max_sec))
                        for _ in range(delay):
                            if not self.is_sending:
                                break
                            await asyncio.sleep(1)

            await self.app_logger.log_and_display("🔚 Цикл рассылки завершён.")

        # ── основной обработчик запуска рассылки по чатам ────

        async def performing_operation(chat_list_fields: list, min_seconds, max_seconds) -> None:
            """
            Запускает автоответчик + рассылку параллельно.

            Автоответчик: обработчик events.NewMessage работает
            автоматически в фоне Telethon (через asyncio event loop).
            Рассылка: запускается как asyncio.Task, чтобы обе корутины
            могли выполняться одновременно.
            """
            logger.warning(f"Выбранный аккаунт: {account_drop_down_list.value}")

            try:
                start = await self.app_logger.start_time()
                client: TelegramClient = await self.connect.client_connect_string_session(
                    session_name=account_drop_down_list.value
                )
                self._active_client = client  # сохраняем для кнопки «Стоп»

                # ── Автоответчик ──────────────────────────────
                @client.on(events.NewMessage(incoming=True))
                async def handle_private_messages(event):
                    if event.is_private:
                        await self.app_logger.log_and_display(
                            f"📩 Входящее: {event.message.message}"
                        )
                        reply_text = (
                                self.auto_reply_text_field.value
                                or "Спасибо за сообщение! Мы ответим позже."
                        )
                        await event.respond(reply_text)
                        await self.app_logger.log_and_display(f"🤖 Ответ: {reply_text}")

                # ── Запускаем рассылку как задачу ─────────────
                # asyncio.create_task позволяет Telethon обрабатывать
                # входящие события (автоответчик) пока идёт рассылка
                self._mailing_task = asyncio.create_task(
                    mailing_loop(client, chat_list_fields, min_seconds, max_seconds)
                )

                # Ждём завершения задачи (по флагу или ошибке)
                await self._mailing_task

                await client.disconnect()
                self._active_client = None
                await self.app_logger.log_and_display("🔌 Клиент отключён")
                await self.app_logger.end_time(start)

            except asyncio.CancelledError:
                # Задача отменена кнопкой «Стоп»
                await self.app_logger.log_and_display("⛔ Рассылка отменена пользователем.")
            except Exception as error:
                logger.exception(error)

        # ── проверка ссылок ──────────────────────────────────

        async def checking_links_group(_):
            """Проверка ссылок пользователя с детальной информацией."""
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

                    if '/+' in link or link.startswith('https://t.me/+'):
                        hash_part = link.split('+')[-1].strip()
                        invite = await client(CheckChatInviteRequest(hash_part))
                        if hasattr(invite, 'chat') and invite.chat:
                            entity = invite.chat
                            full_entity = await client(GetFullChannelRequest(entity))
                        else:
                            logger.warning(f"⚠️ Не удалось обработать приглашение: {link}")
                            continue
                    elif link.startswith(('https://t.me/', 'http://t.me/')):
                        username = link.split('t.me/')[-1].split('?')[0].split('/')[0].strip()
                        if not username or username.startswith('+'):
                            continue
                        entity = await client.get_entity(username)
                        full_entity = await client(GetFullChannelRequest(channel=entity))
                    else:
                        entity = await client.get_entity(link)
                        full_entity = await client(GetFullChannelRequest(channel=entity))

                    if entity and full_entity:
                        banned_rights = getattr(entity, 'default_banned_rights', None)
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

                        about_text = channel_info['about']
                        if about_text and len(about_text) > 200:
                            about_text = about_text[:200] + '...'

                        def _can(attr):
                            return not (getattr(banned_rights, attr) if banned_rights else False)

                        chat_type_display = (
                            "📢 Канал" if channel_info['is_broadcast']
                            else "👥 Супергруппа" if channel_info['is_megagroup']
                            else "👥 Группа"
                        )

                        update_group_send_messages_table(
                            link=link,
                            telegram_id=channel_info['id'],
                            title=channel_info['title'],
                            username=channel_info['username'] or 'отсутствует',
                            about=about_text,
                            participants_count=channel_info['participants_count'],
                            participants_hidden=channel_info['participants_hidden'],
                            type_display=chat_type_display,
                            level=channel_info['level'],
                            slowmode_seconds=channel_info['slowmode_seconds'],
                            can_send_messages=_can('send_messages'),
                            can_send_media=_can('send_media'),
                            can_send_photos=_can('send_photos'),
                            can_send_videos=_can('send_videos'),
                            can_send_docs=_can('send_docs'),
                            can_send_audios=_can('send_audios'),
                            can_send_voices=_can('send_voices'),
                            can_send_roundvideos=_can('send_roundvideos'),
                            can_send_stickers=_can('send_stickers'),
                            can_send_gifs=_can('send_gifs'),
                            can_send_polls=_can('send_polls'),
                            can_embed_links=_can('embed_links'),
                            can_invite_users=_can('invite_users'),
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
                            last_checked=datetime.now(),
                            is_active=True,
                        )
                except ValueError as e:
                    logger.error(f"❌ Не найдена сущность для '{link}': {e}")
                except Exception as e:
                    logger.error(f"❌ Ошибка обработки '{link}': {str(e)[:100]}")

        # ── рассылка в личку ─────────────────────────────────

        async def send_files_to_personal_chats(min_seconds, max_seconds):
            try:
                start = await self.app_logger.start_time()
                self.page.update()
                limit = get_limit(self.limits)
                all_usernames = await load_and_validate_users(
                    app_logger=self.app_logger, gui_program=self.gui_program, page=self.page, limit=limit,
                    session_string=self.session_string, page_go="/sending_messages_files_via_chats",
                    action_text="Рассылки сообщений"
                )
                current_user_index = 0
                for account_number, session_name in enumerate(self.session_string, 1):
                    if not self.is_sending:
                        break
                    if current_user_index >= len(all_usernames):
                        await self.app_logger.log_and_display("✅ Все пользователи обработаны")
                        break

                    client: TelegramClient = await self.connect.client_connect_string_session(
                        session_name=session_name
                    )
                    self._active_client = client

                    if client is None:
                        await self.app_logger.log_and_display(f"⚠️ Пропускаем {session_name}.")
                        continue

                    if limit:
                        users_for_this_account = all_usernames[current_user_index:current_user_index + limit]
                        current_user_index += limit
                    else:
                        remaining_accounts = len(self.session_string) - account_number + 1
                        remaining_users = len(all_usernames) - current_user_index
                        users_per_account = remaining_users // remaining_accounts
                        users_for_this_account = all_usernames[
                            current_user_index:current_user_index + users_per_account]
                        current_user_index += users_per_account

                    if not users_for_this_account:
                        await self.app_logger.log_and_display(f"⚠️ Для {session_name} нет пользователей")
                        continue

                    await self.app_logger.log_and_display(
                        f"🔹 Аккаунт #{account_number}: {session_name}\n"
                        f"   Пользователей: {len(users_for_this_account)}"
                    )

                    try:
                        for username in users_for_this_account:
                            if not self.is_sending:
                                break
                            try:
                                user_to_add = await client.get_entity(username)
                                messages, files = await self.all_find_and_all_files()
                                await send_content(client=client, target=user_to_add, messages=messages, files=files)
                                await self.utils.record_inviting_results(
                                    time_range_1=min_seconds, time_range_2=max_seconds, username=username
                                )
                                # Задержка (прерываемая)
                                delay = random.randint(int(min_seconds), int(max_seconds))
                                for _ in range(delay):
                                    if not self.is_sending:
                                        break
                                    await asyncio.sleep(1)
                            except FloodWaitError as e:
                                await self.app_logger.log_and_display(
                                    f"{translations['ru']['errors']['flood_wait']}{e}", level="error"
                                )
                                break
                            except PeerFloodError:
                                await self.utils.random_dream(min_seconds=min_seconds, max_seconds=max_seconds)
                                break
                            except (UserNotMutualContactError, UserIdInvalidError,
                                    UsernameNotOccupiedError, UsernameInvalidError, ValueError) as e:
                                await self.app_logger.log_and_display(
                                    translations["ru"]["errors"]["invalid_username"]
                                )
                                logger.error(e)
                            except ChatWriteForbiddenError:
                                await self.app_logger.log_and_display(
                                    translations["ru"]["errors"]["chat_write_forbidden"]
                                )
                                break
                            except (TypeError, UnboundLocalError):
                                continue
                    except KeyError:
                        sys.exit(1)

                    await self.app_logger.end_time(start=start)
                    await self.gui_program.show_notification(message="🔚 Конец рассылки сообщений")
                    self._active_client = None

            except ValueError as e:
                await self.gui_program.show_notification(message=f"❌ Ошибка валидации времени: {e}")
            except Exception as error:
                logger.exception(error)
            self.page.update()

        # ── кнопка «Готово» ──────────────────────────────────

        async def launching_action(_=None):
            """Запускает рассылку в личку или по чатам."""
            self.is_sending = True
            try:
                if self.send_message_personal_switch.value:
                    min_seconds, max_seconds = await self.utils.verifies_time_range_entered_correctly(
                        min_seconds=self.tb_time_from.value, max_seconds=self.tb_time_to.value
                    )
                    await send_files_to_personal_chats(min_seconds=min_seconds, max_seconds=max_seconds)

                if self.send_message_group_switch.value:
                    write_group_send_message_table(self.chat_list_field.value)
                    writing_group_links = get_links_table_group_send_messages()
                    if not writing_group_links:
                        await self.gui_program.show_notification(
                            message="❌ Нет чатов для рассылки. Укажите ссылки."
                        )
                        return
                    min_seconds, max_seconds = await self.utils.verifies_time_range_entered_correctly(
                        min_seconds=self.tb_time_from.value, max_seconds=self.tb_time_to.value
                    )
                    await performing_operation(
                        chat_list_fields=writing_group_links,
                        min_seconds=min_seconds,
                        max_seconds=max_seconds,
                    )
            except ValueError as e:
                await self.gui_program.show_notification(message=f"❌ Ошибка валидации времени: {e}")
            except Exception as e:
                logger.exception(e)

        # ── кнопка «Остановить» ──────────────────────────────

        async def stop_sending(_=None):
            """
            Корректная остановка рассылки:
            1. Сбрасываем флаг → циклы прекратят итерации
            2. Отменяем asyncio-задачу (mailing_loop)
            3. Отключаем клиент (прерывает любые ожидающие сетевые вызовы)
            """
            self.is_sending = False
            await self.app_logger.log_and_display("⛔ Остановка рассылки...")

            if self._mailing_task and not self._mailing_task.done():
                self._mailing_task.cancel()
                try:
                    await self._mailing_task
                except asyncio.CancelledError:
                    pass

            if self._active_client and self._active_client.is_connected():
                await self._active_client.disconnect()
                self._active_client = None

            await self.app_logger.log_and_display("✅ Рассылка остановлена.")

        # ── UI ───────────────────────────────────────────────

        self.send_message_personal_switch.disabled = False
        self.send_message_group_switch.disabled = False
        self.send_message_personal_switch.expand = True
        self.send_message_group_switch.expand = True

        ToggleController(
            send_message_personal_switch=self.send_message_personal_switch,
            send_message_group_switch=self.send_message_group_switch,
        ).element_handler_send_message(self.page)

        self.page.views.append(
            ft.View(
                route="/sending_messages_via_chats_menu",
                appbar=await self.gui_program.key_app_bar(),
                spacing=3,
                controls=[
                    ft.Row(controls=[
                        await self.gui_program.create_gradient_text(
                            text=f"{translations['ru']['message_sending_menu']['sending_messages_files_via_chats']}"
                                 f" и Отправка сообщений в личку"
                        )
                    ]),
                    ft.Row(controls=[list_view], height=200),
                    ft.Row(expand=True, controls=[account_drop_down_list]),
                    ft.Row(controls=[
                        self.send_message_personal_switch,
                        self.send_message_group_switch,
                    ]),
                    ft.Row(controls=[self.limits], expand=True),
                    ft.Row(controls=[self.tb_time_from, self.tb_time_to], expand=True),
                    ft.Row(controls=[
                        self.auto_reply_text_field,
                        self.chat_list_field,
                    ], expand=True),

                    ft.Column(
                        spacing=5,  # ← расстояние между кнопками в пикселях
                        controls=[
                            ft.Row(expand=True, controls=[
                                ft.Button(
                                    content="Проверка ссылок для рассылки",
                                    expand=True, height=BUTTON_HEIGHT,
                                    on_click=checking_links_group,
                                ),
                            ]),
                            ft.Row(expand=True, controls=[
                                ft.Button(
                                    content=translations["ru"]["buttons"]["done"],
                                    expand=True, height=BUTTON_HEIGHT,
                                    on_click=launching_action,
                                ),
                            ]),
                            ft.Row(expand=True, controls=[
                                ft.Button(
                                    content="⛔ Остановить рассылку",
                                    expand=True, height=BUTTON_HEIGHT,
                                    on_click=stop_sending,
                                ),
                            ]),
                        ],
                    ),

                ],
            )
        )

    # ─────────────────────────────────────────────────────────
    # Утилиты (без изменений)
    # ─────────────────────────────────────────────────────────

    async def all_find_and_all_files(self):
        return (
            await self.utils.find_files(directory_path=path_folder_with_messages, extension=self.file_extension),
            await self.utils.all_find_files(directory_path="user_data/files_to_send"),
        )

    async def select_and_read_random_file(self, entities, folder):
        try:
            if not entities:
                await self.app_logger.log_and_display(f"📁 Папка 'user_data/{folder}' пуста.")
                return None
            random_file = random.choice(entities)
            filename = f"user_data/{folder}/{random_file[0]}.json"
            await self.app_logger.log_and_display(f"Выбран файл: {random_file[0]}.json")
            return await self.utils.read_json_file(filename=filename)
        except Exception as error:
            await self.app_logger.log_and_display(f"⚠️ Ошибка чтения из {folder}: {error}", level="error")
            logger.exception(error)
            return None
