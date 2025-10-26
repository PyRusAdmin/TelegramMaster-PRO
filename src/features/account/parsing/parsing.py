# -*- coding: utf-8 -*-
import asyncio
import sqlite3

import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from telethon import functions
from telethon.errors import (AuthKeyUnregisteredError, ChannelPrivateError, ChatAdminRequiredError, FloodWaitError,
                             UsernameInvalidError)
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantsSearch, InputPeerEmpty, InputUser

from src.core.configs import WIDTH_WIDE_BUTTON, TIME_ACTIVITY_USER_2, BUTTON_HEIGHT
from src.core.database.account import get_account_list
from src.core.database.database import (MembersAdmin, add_member_to_db, save_group_channel_info,
                                        administrators_entries_in_database)
from src.features.account.connect import TGConnect
from src.features.account.parsing.user_info import UserInfo
from src.features.account.subscribe_unsubscribe.subscribe import Subscribe
from src.features.account.switch_controller import ToggleController
from src.gui.gui import AppLogger, list_view
from src.gui.gui_elements import GUIProgram
from src.locales.translations_loader import translations


class ParsingGroupMembers:
    """Класс для парсинга групп, на которые подписан аккаунт."""

    def __init__(self, page):
        self.page = page
        self.connect = TGConnect(page)
        self.app_logger = AppLogger(page)
        self.subscribe = Subscribe(page=page)  # Инициализация экземпляра класса Subscribe (Подписка)
        self.gui_program = GUIProgram()
        self.account_data = get_account_list()  # Получаем список аккаунтов из базы данных

    async def account_selection_menu(self):
        """Меню парсинга групп"""

        list_view.controls.clear()  # ✅ Очистка логов перед новым запуском
        self.page.controls.append(list_view)  # Добавляем ListView на страницу для отображения логов 📝
        self.page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        """
        TextField - поле для ввода ссылки на чат
        Dropdown - выпадающий список с названиями групп , аккаунтами
        """
        chat_input = ft.TextField(label="🔗 Введите ссылку на чат...", disabled=True)

        # Создаём опции: текст — номер, ключ — session_string
        account_options = [
            ft.DropdownOption(text=phone, key=session_str)
            for phone, session_str in self.account_data
        ]
        # Создаем выпадающий список с названиями групп
        account_drop_down_list = ft.Dropdown(
            label="📂 Выберите аккаунт",  # ✅ Название выпадающего списка
            width=WIDTH_WIDE_BUTTON,  # ✅ Ширина выпадающего списка
            options=account_options,  # ✅ Опции выпадающего списка
            autofocus=True  # ✅ Автозаполнение
        )

        # Кнопки-переключатели
        account_groups_switch = ft.CupertinoSwitch(label="Группы аккаунта", value=False, disabled=True)
        admin_switch = ft.CupertinoSwitch(label="Администраторов", value=False, disabled=True)
        members_switch = ft.CupertinoSwitch(label="Участников", value=False, disabled=True)
        active_switch = ft.CupertinoSwitch(label="Активные", value=False, disabled=True)
        account_group_selection_switch = ft.CupertinoSwitch(label="Выбрать группу", value=False, disabled=True)

        ToggleController(admin_switch, account_groups_switch, members_switch, account_group_selection_switch,
                         active_switch).element_handler(self.page)

        async def add_items(_):
            """🚀 Запускает процесс парсинга групп и отображает статус в интерфейсе."""
            try:

                logger.debug(f"Аккаунт: {account_drop_down_list.value}")

                client = await self.connect.client_connect_string_session(session_name=account_drop_down_list.value)
                await self.connect.getting_account_data(client)

                await self.load_groups(dropdown, result_text)  # ⬅️ Подгружаем группы

                data = chat_input.value.split()
                logger.info(f"Полученные данные: {data}")  # Отладка
                # Удаляем дубликаты ссылок введенных пользователем
                start = await self.app_logger.start_time()
                self.page.update()  # Обновите страницу, чтобы сразу показать сообщение 🔄
                try:
                    if account_groups_switch.value:  # Парсинг групп, на которые подписан аккаунт
                        await self.parsing_account_groups(client=client)
                    if admin_switch.value:  # Если выбрано парсить администраторов, выполняем парсинг администраторов 👤
                        for groups in data:
                            await self.obtaining_administrators(client=client, groups=groups)
                    if members_switch.value:  # Парсинг участников
                        for groups in data:
                            await parse_group(client=client, groups_wr=groups)
                    if active_switch.value:  # ⚠️ Парсинг активных пользователей
                        await self.app_logger.log_and_display(
                            f"🔍 Сканируем чат: {chat_input.value} на {limit_active_user.value} сообщений")
                        await self.parse_active_users(
                            chat_input=chat_input.value,
                            limit_active_user=int(limit_active_user.value),
                            client=client
                        )
                    if account_group_selection_switch.value:  # Парсинг выбранной группы
                        await self.load_groups(dropdown, result_text)  # ⬅️ Подгружаем группы
                        await start_group_parsing(client=client, dropdown=dropdown, result_text=result_text)
                    await self.app_logger.end_time(start)
                except Exception as error:
                    logger.exception(error)
            except Exception as error:
                logger.exception(error)

        async def start_group_parsing(client, dropdown, result_text):
            """
            🚀 Запускает процесс парсинга группы и отображает статус в интерфейсе.
            :param client: Сессия Telethon
            :param dropdown: Выпадающий список
            :param result_text: Текст
            """

            await self.load_groups(client=client, dropdown=dropdown, result_text=result_text)

            if not dropdown.value:
                await self.app_logger.log_and_display("⚠️ Группа не выбрана")
                return
            await self.app_logger.log_and_display(f"▶️ Парсинг группы: {dropdown.value}")
            logger.warning(f"🔍 Парсим группу: {dropdown.value}")
            await parse_group(client=client, groups_wr=dropdown.value)
            await client.disconnect()
            await self.app_logger.log_and_display("🔚 Парсинг завершен")

        async def parse_group(client, groups_wr) -> None:
            """
            Выполняет парсинг групп, на которые пользователь подписался. Аргумент phone используется декоратором
            @handle_exceptions для отлавливания ошибок и записи их в базу данных user_data/software_database.db.

            :param client: Сессия Telethon
            :param groups_wr: Ссылка на группу
            """

            await self.app_logger.log_and_display("🔍 Ищем участников... 💾 Сохраняем в файл software_database.db...")
            try:
                all_participants: list = []
                while_condition = True
                my_filter = ChannelParticipantsSearch("")
                offset = 0
                while while_condition:
                    try:
                        logger.warning(f"🔍 Получаем участников группы: {groups_wr}")
                        participants = await client(
                            GetParticipantsRequest(channel=groups_wr, offset=offset, filter=my_filter, limit=200,
                                                   hash=0, ))
                        all_participants.extend(participants.users)
                        offset += len(participants.users)
                        if len(participants.users) < 1:
                            while_condition = False
                    except TypeError:
                        await self.app_logger.log_and_display(f"❌ Ошибка: {groups_wr} не является группой / каналом.",
                                                              level="error")
                        await asyncio.sleep(2)
                        break
                    except ChatAdminRequiredError:
                        await self.app_logger.log_and_display(translations["ru"]["errors"]["admin_rights_required"])
                        await asyncio.sleep(2)
                        break
                    except ChannelPrivateError:
                        await self.app_logger.log_and_display(translations["ru"]["errors"]["channel_private"])
                        await asyncio.sleep(2)
                        break
                    except AuthKeyUnregisteredError:
                        await self.app_logger.log_and_display(translations["ru"]["errors"]["auth_key_unregistered"])
                        await asyncio.sleep(2)
                        break
                    except sqlite3.DatabaseError:  # TODO Обработка ошибок базы данных (придумать универсальнео наименование)
                        await self.app_logger.log_and_display("Ошибка базы данных аккаунта")
                        await asyncio.sleep(2)
                        break

                for user in all_participants:
                    await self.app_logger.log_and_display(f"Полученные данные: {user}")
                    logger.info(f"Полученные данные: {user}")
                    log_data = await self.collect_user_log_data(user)
                    add_member_to_db(log_data=log_data)

            except TypeError as error:
                logger.exception(f"❌ Ошибка: {error}")
                return []  # Возвращаем пустой список в случае ошибки
            except Exception as error:
                logger.exception(error)

        limit_active_user = ft.TextField(label="💬 Кол-во сообщений", expand=True, disabled=True)
        # Выпадающий список для выбора группы
        dropdown = ft.Dropdown(width=WIDTH_WIDE_BUTTON, options=[], autofocus=True, disabled=True)
        result_text = ft.Text(value="📂 Группы не загружены")
        parse_button = ft.ElevatedButton(text="🔍 Парсить", width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                         on_click=add_items, disabled=True)

        # После успешного выбора файла:
        admin_switch.disabled = False
        members_switch.disabled = False
        account_groups_switch.disabled = False
        account_group_selection_switch.disabled = False
        active_switch.disabled = False
        chat_input.disabled = False
        limit_active_user.disabled = False
        dropdown.disabled = False
        parse_button.disabled = False

        # Выравнивание элементов управления
        admin_switch.expand = True
        members_switch.expand = True
        account_groups_switch.expand = True

        account_group_selection_switch.expand = True
        active_switch.expand = True
        self.page.update()

        # Представление (View)
        view = ft.View(
            route="/parsing",
            controls=[
                await self.gui_program.key_app_bar(),
                await self.gui_program.outputs_text_gradient(),
                list_view,
                ft.Column([
                    account_drop_down_list,  # ⬅️ Выбор аккаунта из выпадающего списка
                    ft.Row([admin_switch, members_switch, account_groups_switch, account_group_selection_switch,
                            active_switch]),
                    chat_input,
                    await self.gui_program.diver_castom(),  # Горизонтальная линия
                    ft.Row([limit_active_user]),
                    await self.gui_program.diver_castom(),  # Горизонтальная линия
                    result_text,
                    dropdown,
                    parse_button,  # ⬅️ Кнопка для парсинга
                ])
            ]
        )
        self.page.views.append(view)
        self.page.update()

    async def collect_user_log_data(self, user):
        return {
            "username": await UserInfo().get_username(user),
            "user_id": await UserInfo().get_user_id(user),
            "access_hash": await UserInfo().get_access_hash(user),
            "first_name": await UserInfo().get_first_name(user),
            "last_name": await UserInfo().get_last_name(user),
            "user_phone": await UserInfo().get_user_phone(user),
            "online_at": await UserInfo().get_user_online_status(user),
            "photos_id": await UserInfo().get_photo_status(user),
            "user_premium": await UserInfo().get_user_premium_status(user),
        }

    async def load_groups(self, client, dropdown, result_text):
        """
        Выводит список групп, на которые подписан аккаунт.

        :param client: Сессия Telethon
        :param dropdown: Выпадающий список
        :param result_text: Текст
        """
        try:
            result = await client(
                GetDialogsRequest(offset_date=None, offset_id=0, offset_peer=InputPeerEmpty(), limit=200, hash=0))
            groups = await self.filtering_groups(result.chats)
            titles = await self.name_of_the_groups(groups)
            dropdown.options = [ft.dropdown.Option(t) for t in titles]
            result_text.value = f"🔽 Найдено групп: {len(titles)}"
            self.page.update()
            # return phone
        except Exception as e:
            logger.exception(e)
            return None

    async def obtaining_administrators(self, client, groups):
        """
        Получает информацию об администраторах группы, включая их биографию, статус, фото и премиум-статус.
        :param groups: Ссылка на группу
        :param client: Клиент Telethon
        """
        try:
            await self.app_logger.log_and_display(f"🔍 Парсинг группы: {groups}")
            try:
                entity = await client.get_entity(groups)  # Получаем сущность группы/канала
                # Проверяем, является ли сущность супергруппой
                if hasattr(entity, "megagroup") and entity.megagroup:
                    # Получаем итератор администраторов
                    async for user in client.iter_participants(entity, filter=ChannelParticipantsAdmins):
                        # Формируем отображаемое имя администратора
                        admin_name = (user.first_name or "").strip()
                        if user.last_name:
                            admin_name += f" {user.last_name}"

                        # Получаем полную информацию о пользователе
                        log_data = {
                            "username": await UserInfo().get_username(user),
                            "user_id": await UserInfo().get_user_id(user),
                            "access_hash": await UserInfo().get_access_hash(user),
                            "first_name": await UserInfo().get_first_name(user),
                            "last_name": await UserInfo().get_last_name(user),
                            "phone": await UserInfo().get_user_phone(user),
                            "online_at": await UserInfo().get_user_online_status(user),
                            "photo_status": await UserInfo().get_photo_status(user),
                            "premium_status": await UserInfo().get_user_premium_status(user),
                            "user_status": "Admin",
                            "bio": await UserInfo().get_bio_user(await UserInfo().get_full_user_info(user, client)),
                            "group": groups,
                        }
                        # Задержка для избежания ограничений Telegram API
                        await asyncio.sleep(0.5)
                        await self.app_logger.log_and_display(f"Полученные данные: {log_data}")

                        existing_user = MembersAdmin.select().where(
                            MembersAdmin.user_id == log_data["user_id"]).first()
                        if not existing_user:
                            administrators_entries_in_database(log_data)
                        else:
                            await self.app_logger.log_and_display(
                                f"⚠️ Пользователь с user_id {log_data['user_id']} уже есть в базе. Пропущен.")
                else:
                    try:
                        await self.app_logger.log_and_display(f"Это не группа, а канал: {entity.title}")
                        # Удаляем группу из списка после завершения парсинга 🗑️
                    except AttributeError:
                        await self.app_logger.log_and_display(
                            f"⚠️ Ошибка при получении сущности группы {groups[0]}")
            except UsernameInvalidError:
                await self.app_logger.log_and_display(translations["ru"]["errors"]["group_entity_error"])
            except ValueError:
                await self.app_logger.log_and_display(translations["ru"]["errors"]["group_entity_error"])
            await client.disconnect()
        except FloodWaitError as e:
            await self.app_logger.log_and_display(f"{translations["ru"]["errors"]["flood_wait"]}{e}", level="error")
            await client.disconnect()
        except Exception as error:
            logger.exception(error)

    async def parsing_account_groups(self, client):
        """
        Парсит группы на которые подписан аккаунт
        :param client: Клиент Telethon
        """
        # Обрабатываем все файлы сессий по очереди 📂
        await self.connect.getting_account_data(client)

        await self.forming_a_list_of_groups(client)

    async def parse_active_users(self, chat_input, limit_active_user, client) -> None:
        """
        Парсинг активных пользователей в чате.
        :param client: Клиент Telethon
        :param chat_input: ссылка на чат
        :param limit_active_user: лимит сообщений
        """
        try:
            await self.subscribe.subscribe_to_group_or_channel(client=client, groups=chat_input)
            try:
                await asyncio.sleep(int(TIME_ACTIVITY_USER_2 or 5))
            except TypeError:
                await asyncio.sleep(5)
            # Все операции с Telegram API должны быть здесь
            await self.get_active_users(client=client, chat=chat_input, limit_active_user=limit_active_user)
        except Exception as error:
            logger.exception(error)

    async def get_active_users(self, client, chat, limit_active_user) -> None:
        """
        Получаем данные участников группы которые писали сообщения.

        :param client: Клиент Telegram
        :param chat: ссылка на чат
        :param limit_active_user: лимит активных участников
        """
        try:
            entity = await client.get_entity(chat)
            async for message in client.iter_messages(entity, limit=limit_active_user):
                from_id = getattr(message, 'from_id', None)
                if from_id:
                    user = await client.get_entity(from_id)
                    try:
                        await self.app_logger.log_and_display(message=f"{message.from_id}")
                        # Получаем входную сущность пользователя
                        from_user = InputUser(user_id=await UserInfo().get_user_id(user=user),
                                              access_hash=await UserInfo().get_access_hash(
                                                  user=user))  # Создаем InputUser
                        await self.app_logger.log_and_display(message=f"{from_user}")
                        # Получаем данные о пользователе
                        log_data = await self.collect_user_log_data(user=user)
                        await self.app_logger.log_and_display(message=f"{log_data}")
                        add_member_to_db(log_data=log_data)
                    except ValueError as e:
                        await self.app_logger.log_and_display(
                            message=f"❌ Не удалось найти сущность для пользователя {message.from_id.user_id}: {e}")
                else:
                    await self.app_logger.log_and_display(f"Сообщение {message.id} не имеет действительного from_id.")
        except Exception as error:
            logger.exception(error)

    @staticmethod
    async def filtering_groups(chats):
        """
        Фильтрация чатов для получения только групп.

        :param chats: Список чатов.
        :return: Список групп.
        """
        groups = []
        for chat in chats:
            try:
                if chat.megagroup:
                    groups.append(chat)
            except AttributeError:
                continue  # Игнорируем объекты без атрибута megagroup
        return groups

    @staticmethod
    async def name_of_the_groups(groups):
        """
        Получение названий групп.

        :param groups: Список групп.
        :return: Список названий групп.
        """
        group_names = []  # Создаем новый список для названий групп
        for group in groups:
            group_names.append(group.title)  # Добавляем название группы в список
        return group_names

    async def forming_a_list_of_groups(self, client) -> None:
        """
        Формирует список групп и каналов без дублирования записей.

        Метод собирает информацию о группах и каналах, включая их ID, название, описание, ссылку, количество участников
        и время последнего парсинга. Данные сохраняются в базу данных.

        :param client: Экземпляр клиента Telegram.
        """
        try:
            async for dialog in client.iter_dialogs():
                try:
                    entity = await client.get_entity(dialog.id)
                    # Пропускаем личные чаты
                    from telethon.tl.types import Chat, Channel
                    if isinstance(entity, Chat):
                        logger.debug(f"💬 Пропущен личный чат: {dialog.id}")
                        continue
                    # Проверяем, является ли супергруппой или каналом
                    if not getattr(entity, 'megagroup', False) and not getattr(entity, 'broadcast', False):
                        continue
                    full_channel_info = await client(functions.channels.GetFullChannelRequest(channel=entity))
                    chat = full_channel_info.full_chat
                    if not hasattr(chat, 'participants_count'):
                        logger.warning(f"⚠️ participants_count отсутствует для {dialog.id}")
                        continue
                    participants_count = chat.participants_count
                    username = getattr(entity, 'username', None)
                    link = f"https://t.me/{username}" if username else None
                    title = entity.title or "Без названия"
                    about = getattr(chat, 'about', '')
                    # Логируем информацию
                    await self.app_logger.log_and_display(
                        f"{dialog.id}, {title}, {link or 'без ссылки'}, {participants_count}")
                    await save_group_channel_info(
                        dialog=dialog, title=title, about=about, link=link,
                        participants_count=participants_count)
                except TypeError as te:
                    logger.warning(f"❌ TypeError при обработке диалога {dialog.id}: {te}")
                    continue
                except Exception as e:
                    logger.exception(f"⚠️ Ошибка при обработке диалога {dialog.id}: {e}")
                    continue
        except Exception as error:
            logger.exception(f"🔥 Критическая ошибка в forming_a_list_of_groups: {error}")

# 690
