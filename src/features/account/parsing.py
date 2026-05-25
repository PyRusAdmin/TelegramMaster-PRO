import asyncio
import sqlite3

import flet as ft
from loguru import logger
from telethon import functions
from telethon.errors import (
    AuthKeyUnregisteredError, ChannelPrivateError, ChatAdminRequiredError, FloodWaitError, UsernameInvalidError
)
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantsSearch, InputPeerEmpty, InputUser, Chat

from src.core.configs import WIDTH_WIDE_BUTTON, TIME_ACTIVITY_USER_2, BUTTON_HEIGHT
from src.core.database.account import get_account_list
from src.core.database.database import (
    MembersAdmin, add_member_to_db, save_group_channel_info, administrators_entries_in_database
)
from src.features.account.connect import TGConnect
from src.features.account.subscribe import Subscribe
from src.features.account.switch_controller import ToggleController
from src.features.account.user_info import UserInfo
from src.features.proxy.checking_proxy import Proxy
from src.gui.gui import AppLogger, list_view
from src.gui.gui_elements import GUIProgram
from src.locales.translations_loader import translations


class ParsingGroupMembers:
    """Класс для парсинга групп, на которые подписан аккаунт."""

    def __init__(self, page: ft.Page):
        """
        Инициализация класса для парсинга участников групп Telegram.

        :param page: Страница интерфейса Flet для отображения элементов управления
        """
        self.page = page  # Сохраняем ссылку на страницу Flet
        self.connect = TGConnect(page=page)  # Инициализация экземпляра класса TGConnect
        self.app_logger = AppLogger(page=page)  # Инициализация экземпляра класса AppLogger
        self.subscribe = Subscribe(page=page)  # Инициализация экземпляра класса Subscribe (Подписка)
        self.gui_program = GUIProgram(page=page)  # Инициализация экземпляра класса GUIProgram
        self.account_data = get_account_list()  # Получаем список аккаунтов из базы данных
        self.proxy = Proxy(page=page)  # Инициализация класса Proxy для проверки прокси.
        self.group_map = {}
        self.chat_input = ft.TextField(
            label="🔗 Введите ссылку на чат...",
            expand=True,  # Полноразмерное расширение
            disabled=True
        )
        self.limit_active_user = ft.TextField(
            label="💬 Кол-во сообщений",
            expand=True,
            disabled=True
        )

    async def load_groups(self, client, dropdown, result_text):
        """
        Загружает группы, на которые подписан аккаунт, и сохраняет их в self.group_map.
        :param client: Сессия Telethon
        :param dropdown: Выпадающий список
        :param result_text: Текст
        """
        try:
            result = await client(GetDialogsRequest(
                offset_date=None,
                offset_id=0,
                offset_peer=InputPeerEmpty(),
                limit=200,
                hash=0
            )
            )
            groups = [chat for chat in result.chats if getattr(chat, 'megagroup', False)]
            titles = [group.title for group in groups]

            # Сохраняем соответствие название → сущность
            self.group_map = {group.title: group for group in groups}

            dropdown.options = [ft.dropdown.Option(title) for title in titles]
            result_text.value = f"🔽 Найдено групп: {len(titles)}"
            self.page.update()
        except Exception as e:
            logger.exception("Ошибка при загрузке групп")
            result_text.value = "❌ Ошибка загрузки групп"
            dropdown.options = []
            self.page.update()

    async def account_selection_menu(self):
        """
        Отображает меню выбора аккаунта для парсинга групп.

        :return: None
        """
        try:
            list_view.controls.clear()  # ✅ Очистка логов перед новым запуском
            self.page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

            """
            TextField - поле для ввода ссылки на чат
            Dropdown - выпадающий список с названиями групп , аккаунтами
            """

            account_drop_down_list = self.gui_program.create_account_dropdown(self.account_data)

            # Выпадающий список для выбора группы
            dropdown = ft.Dropdown(
                label="📋 Выберите группу",
                width=WIDTH_WIDE_BUTTON,
                options=[],
                autofocus=True,
                disabled=True
            )
            result_text = ft.Text(value="📂 Сначала выберите аккаунт")

            # Кнопки-переключатели
            account_groups_switch = ft.CupertinoSwitch(label="Группы аккаунта", value=False, disabled=True)
            admin_switch = ft.CupertinoSwitch(label="Администраторов", value=False, disabled=True)
            members_switch = ft.CupertinoSwitch(label="Участников", value=False, disabled=True)
            active_switch = ft.CupertinoSwitch(label="Активные", value=False, disabled=True)
            account_group_selection_switch = ft.CupertinoSwitch(label="Выбрать группу", value=False, disabled=True)

            ToggleController(
                admin_switch, account_groups_switch, members_switch, account_group_selection_switch, active_switch
            ).element_handler(self.page)

            async def on_account_change(e):
                """📂 Обработчик изменения аккаунта."""
                if account_drop_down_list.value:
                    # Сбрасываем состояние при смене аккаунта
                    dropdown.options = []
                    dropdown.value = None
                    dropdown.disabled = True
                    result_text.value = "📂 Аккаунт выбран. Включите 'Выбрать группу' для загрузки групп"
                    self.group_map = {}  # Очищаем предыдущие группы
                    self.page.update()
                else:
                    dropdown.options = []
                    dropdown.value = None
                    dropdown.disabled = True
                    result_text.value = "📂 Выберите аккаунт"
                    self.page.update()

            async def on_group_selection_switch_change(e):
                """🔄 Обработчик переключателя 'Выбрать группу'"""
                if account_group_selection_switch.value:
                    # Переключатель включен - загружаем группы
                    if not account_drop_down_list.value:
                        await self.app_logger.log_and_display("⚠️ Сначала выберите аккаунт")
                        account_group_selection_switch.value = False
                        self.page.update()
                        return

                    # Загружаем группы выбранного аккаунта
                    result_text.value = "⏳ Загрузка групп..."
                    dropdown.disabled = True
                    self.page.update()

                    try:
                        client = await self.connect.client_connect_string_session(
                            session_name=account_drop_down_list.value
                        )

                        if client:
                            await self.load_groups(client, dropdown, result_text)
                            dropdown.disabled = False  # ✅ Разблокируем dropdown после загрузки
                            await client.disconnect()
                        else:
                            result_text.value = "❌ Не удалось подключиться к аккаунту"
                            account_group_selection_switch.value = False
                            dropdown.disabled = True

                    except Exception as error:
                        logger.exception(error)
                        result_text.value = f"❌ Ошибка загрузки групп: {str(error)}"
                        account_group_selection_switch.value = False
                        dropdown.disabled = True

                    self.page.update()
                else:
                    # Переключатель выключен - очищаем список групп
                    dropdown.options = []
                    dropdown.value = None
                    dropdown.disabled = True
                    result_text.value = "📂 Включите переключатель для загрузки групп"
                    self.group_map = {}
                    self.page.update()

            account_drop_down_list.on_change = on_account_change
            account_group_selection_switch.on_change = on_group_selection_switch_change

            async def add_items(_):
                """🚀 Запускает процесс парсинга групп и отображает статус в интерфейсе."""
                try:
                    logger.debug(f"Аккаунт: {account_drop_down_list.value}")
                    client = await self.connect.client_connect_string_session(session_name=account_drop_down_list.value)
                    data = self.chat_input.value.split()
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
                                f"🔍 Сканируем чат: {self.chat_input.value} на {self.limit_active_user.value} сообщений")
                            limit_val = self.limit_active_user.value.strip()
                            if not limit_val.isdigit():
                                await self.app_logger.log_and_display(
                                    "⚠️ Укажите корректное число для количества сообщений.")
                                return
                            await self.parse_active_users(
                                chat_input=self.chat_input.value,
                                limit_active_user=int(limit_val),
                                client=client
                            )
                        if account_group_selection_switch.value:  # Парсинг выбранной группы
                            await start_group_parsing(client=client, dropdown=dropdown)
                        await self.app_logger.end_time(start)
                    except Exception as error:
                        logger.exception(error)
                except Exception as error:
                    logger.exception(error)

            async def start_group_parsing(client, dropdown):
                """
                Парсит выбранную группу.
                :param client: Клиент сессии телеграм
                :param dropdown: выпадающий список
                """
                if not dropdown.value:
                    await self.app_logger.log_and_display("⚠️ Группа не выбрана")
                    return

                group_entity = self.group_map.get(dropdown.value)
                if not group_entity:
                    await self.app_logger.log_and_display("❌ Не удалось найти группу")
                    return

                await self.app_logger.log_and_display(f"▶️ Парсинг группы: {dropdown.value}")
                await parse_group(client=client, groups_wr=group_entity)  # ← передаём entity
                await self.app_logger.log_and_display("🔚 Парсинг завершён")

            async def parse_group(client, groups_wr) -> None:
                """
                Выполняет парсинг участников указанной группы.

                :param client: Экземпляр клиента Telegram
                :param groups_wr: Ссылка на группу или её entity
                :return: None
                """

                await self.app_logger.log_and_display(
                    "🔍 Ищем участников... 💾 Сохраняем в файл software_database.db...")
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
                            await self.app_logger.log_and_display(
                                f"❌ Ошибка: {groups_wr} не является группой / каналом.",
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
                        except sqlite3.DatabaseError:
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
                    return []
                except Exception as error:
                    logger.exception(error)

            # parse_text
            # parse_button = ft.Button(
            #     content="🔍 Парсить",
            #     width=WIDTH_WIDE_BUTTON,
            #     height=BUTTON_HEIGHT,
            #     on_click=add_items,
            #     disabled=True
            # )

            parse_button = await self.gui_program.gui_button(
                text=translations["ru"]["parsing_menu"]["parse_text"],
                on_click=add_items,
                bgcolor=ft.Colors.GREEN,
                disabled=True
            )

            # После успешного выбора файла:
            admin_switch.disabled = False
            members_switch.disabled = False
            account_groups_switch.disabled = False
            account_group_selection_switch.disabled = False
            active_switch.disabled = False
            self.chat_input.disabled = False
            self.limit_active_user.disabled = False
            parse_button.disabled = False

            # Выравнивание элементов управления
            admin_switch.expand = True
            members_switch.expand = True
            account_groups_switch.expand = True
            account_group_selection_switch.expand = True
            active_switch.expand = True
            self.page.update()

            self.page.views.append(
                ft.View(
                    route="/parsing",
                    appbar=await self.gui_program.key_app_bar(),
                    controls=[
                        await self.gui_program.create_gradient_text(
                            text=translations["ru"]["menu"]["parsing"]
                        ),
                        list_view,
                        ft.Column(
                            [
                                account_drop_down_list,  # ⬅️ Выбор аккаунта из выпадающего списка
                                ft.Row(
                                    [
                                        admin_switch, members_switch, account_groups_switch,
                                        account_group_selection_switch,
                                        active_switch
                                    ]
                                ),
                                self.chat_input,  # ⬅️ Поле для ввода ссылки на чат
                                await self.gui_program.diver_castom(),  # Горизонтальная линия
                                ft.Row(
                                    [
                                        self.limit_active_user  # ⬅️ Поле для ввода кол-ва сообщений
                                    ]
                                ),
                                await self.gui_program.diver_castom(),  # Горизонтальная линия
                                result_text,
                                dropdown,
                                ft.Row(
                                    controls=[parse_button]
                                ),  # ⬅️ Кнопка для парсинга
                            ])
                    ]
                )
            )
            self.page.update()

        except Exception as e:
            logger.exception(e)

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

    async def obtaining_administrators(self, client, groups):
        """
        Получает информацию об администраторах группы, включая их биографию, статус, фото и премиум-статус.

        :param client: Экземпляр клиента Telegram
        :param groups: Ссылка на группу
        :return: None
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
        Парсит группы, на которые подписан аккаунт.

        :param client: Экземпляр клиента Telegram
        :return: None
        """
        # Обрабатываем все файлы сессий по очереди 📂

        await self.forming_a_list_of_groups(client)

    async def parse_active_users(self, chat_input, limit_active_user, client) -> None:
        """
        Парсинг активных пользователей в чате.

        :param client: Экземпляр клиента Telegram
        :param chat_input: ссылка на чат
        :param limit_active_user: лимит количества сообщений для анализа
        :return: None
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
        Получаем данные участников группы, которые писали сообщения.

        :param client: Экземпляр клиента Telegram
        :param chat: ссылка на чат
        :param limit_active_user: лимит количества сообщений для анализа
        :return: None
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
                        from_user = InputUser(
                            user_id=await UserInfo().get_user_id(
                                user=user
                            ),
                            access_hash=await UserInfo().get_access_hash(
                                user=user
                            )
                        )  # Создаем InputUser
                        await self.app_logger.log_and_display(message=f"{from_user}")
                        # Получаем данные о пользователе
                        log_data = await self.collect_user_log_data(user=user)
                        await self.app_logger.log_and_display(message=f"{log_data}")
                        add_member_to_db(log_data=log_data)
                    except ValueError as e:
                        await self.app_logger.log_and_display(
                            message=f"❌ Не удалось найти сущность для пользователя {message.from_id.user_id}: {e}")
                else:
                    await self.app_logger.log_and_display(
                        message=f"Сообщение {message.id} не имеет действительного from_id.")
        except Exception as error:
            logger.exception(error)

    async def forming_a_list_of_groups(self, client) -> None:
        """
        Формирует список групп и каналов без дублирования записей.

        Метод собирает информацию о группах и каналах, включая их ID, название, описание, ссылку, количество участников
        и время последнего парсинга. Данные сохраняются в базу данных.

        :param client: Экземпляр клиента Telegram
        :return: None
        """
        try:
            async for dialog in client.iter_dialogs():
                try:
                    entity = await client.get_entity(dialog.id)
                    # Пропускаем личные чаты
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
                    save_group_channel_info(
                        dialog=dialog,
                        title=title,
                        about=about,
                        link=link,
                        participants_count=participants_count
                    )
                except TypeError as te:
                    logger.warning(f"❌ TypeError при обработке диалога {dialog.id}: {te}")
                    continue
                except Exception as e:
                    logger.exception(f"⚠️ Ошибка при обработке диалога {dialog.id}: {e}")
                    continue
        except Exception as error:
            logger.exception(f"🔥 Критическая ошибка в forming_a_list_of_groups: {error}")
