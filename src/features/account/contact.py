# -*- coding: utf-8 -*-
import asyncio

import flet as ft
from loguru import logger
from telethon import functions, types
from telethon.errors import SessionRevokedError, AuthKeyUnregisteredError

from src.core.configs import BUTTON_HEIGHT, WIDTH_WIDE_BUTTON, WIDTH_INPUT_FIELD_AND_BUTTON
from src.core.configs import path_accounts_folder
from src.core.sqlite_working_tools import (add_member_to_db, write_to_database_contacts_accounts, write_contact_db,
                                           getting_contacts_from_database, delete_contact_db)
from src.core.utils import Utils
from src.features.account.connect import TGConnect
from src.gui.gui_elements import GUIProgram
from src.features.account.parsing.parsing import UserInfo
from src.gui.gui import AppLogger, list_view
from src.gui.notification import show_notification
from src.locales.translations_loader import translations


class StatusDisplay:

    def __init__(self, page: ft.Page):
        """
        Инициализация экземпляра класса StatusDisplay
        :param page: Объект страницы ft.Page
        """
        self.page = page
        self.utils = Utils(page=page)

    def display_account_count(self):
        # Получаем количество аккаунтов
        sessions_count = len(self.utils.find_filess(directory_path=path_accounts_folder, extension='session'))
        list_view.controls.append(ft.Text(f"Подключенных аккаунтов {sessions_count}"))
        return sessions_count


class TGContact:
    """
    Работа с контактами Telegram
    """

    def __init__(self, page: ft.Page):
        """
        Инициализация экземпляра класса TGContact
        :param page: Объект страницы ft.Page
        """
        self.page = page
        self.connect = TGConnect(page=page)
        self.app_logger = AppLogger(page=page)
        self.utils = Utils(page=page)
        self.user_info = UserInfo()
        self.gui_program = GUIProgram()
        self.status_display = StatusDisplay(page=page)

    async def working_with_contacts_menu(self):
        """
        Меню 📇 Работа с контактами
        """
        list_view.controls.clear()  # Очистка list_view для отображения новых элементов и недопущения дублирования

        sessions_count = self.status_display.display_account_count()  # Получаем количество аккаунтов
        logger.info(f"Подключенных аккаунтов {sessions_count}")

        async def show_account_contact_list(_) -> None:
            """
            Показать список контактов аккаунтов и запись результатов в файл
            """
            try:
                start = await self.app_logger.start_time()
                for session_name in self.utils.find_filess(directory_path=path_accounts_folder, extension='session'):
                    # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
                    client = await self.connect.client_connect_string_session(session_name)
                    await self.connect.getting_account_data(client)

                    # Парсинг контактов Telegram аккаунта
                    await self.recording_contacts_in_the_database(client=client)
                    client.disconnect()  # Разрываем соединение telegram

                await self.app_logger.end_time(start=start)
                await show_notification(self.page, "🔚 Конец парсинга контактов")  # Выводим уведомление пользователю
            except Exception as error:
                logger.exception(error)

        async def delete_contact(_) -> None:
            """
            Удаляем контакты с аккаунтов
            """
            start = await self.app_logger.start_time()
            for session_name in self.utils.find_filess(directory_path=path_accounts_folder, extension='session'):
                # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
                client = await self.connect.client_connect_string_session(session_name=session_name)
                await self.connect.getting_account_data(client=client)

                await self.we_get_the_account_id(client=client)
                client.disconnect()  # Разрываем соединение telegram

            await self.app_logger.end_time(start=start)
            await show_notification(page=self.page,
                                    message="🔚 Конец удаления контактов контактов")  # Выводим уведомление пользователю

        async def inviting_contact(_) -> None:
            """
            Добавление данных в телефонную книгу с последующим формированием списка software_database.db, для inviting
            """
            try:
                # Открываем базу данных для работы с аккаунтами user_data/software_database.db
                for session_name in self.utils.find_filess(directory_path=path_accounts_folder, extension='session'):
                    # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
                    client = await self.connect.client_connect_string_session(session_name=session_name)
                    await self.connect.getting_account_data(client=client)

                    await self.add_contact_to_phone_book(client=client)
            except Exception as error:
                logger.exception(error)

        async def write_contact_to_db(_) -> None:
            """📋 Формирование списка контактов"""
            data = input_numbers.value.strip()
            if not data:
                await show_notification(self.page, "⚠️ Поле пустое")
                return

            # Разделяем по переносам строк, удаляем пустые и лишние пробелы
            phones = [line.strip() for line in data.splitlines() if line.strip()]

            logger.info(f"Вставлено номеров: {len(phones)}")
            for phone in phones:
                write_contact_db(phone)

            await show_notification(self.page, f"✅ Добавлено {len(phones)} номеров")

        input_numbers = ft.TextField(label="Вставьте список номеров для записи в базу данных.",
                                     label_style=ft.TextStyle(size=15), autofocus=True,
                                     width=WIDTH_INPUT_FIELD_AND_BUTTON,
                                     text_size=12)

        self.page.views.append(
            ft.View("/working_with_contacts",
                    [
                        await self.gui_program.key_app_bar(),
                        ft.Text(spans=[ft.TextSpan(
                            translations["ru"]["menu"]["contacts"],
                            ft.TextStyle(
                                size=20, weight=ft.FontWeight.BOLD,
                                foreground=ft.Paint(
                                    gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                         ft.Colors.PURPLE]))))]),
                        list_view,  # Отображение логов 📝
                        ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.

                            ft.Row([input_numbers,  # Ввод номеров
                                    # 📋 Формирование списка контактов
                                    ft.ElevatedButton(width=WIDTH_INPUT_FIELD_AND_BUTTON, height=BUTTON_HEIGHT,
                                                      text=translations["ru"]["contacts_menu"][
                                                          "creating_a_contact_list"],
                                                      on_click=write_contact_to_db)]),
                            # 👥 Парсинг списка контактов
                            ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                              text=translations["ru"]["contacts_menu"]["show_a_list_of_contacts"],
                                              on_click=show_account_contact_list),
                            # 🗑️ Удаление контактов
                            ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                              text=translations["ru"]["contacts_menu"]["deleting_contacts"],
                                              on_click=delete_contact),
                            # ➕ Добавление контактов
                            ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                              text=translations["ru"]["contacts_menu"]["adding_contacts"],
                                              on_click=inviting_contact),
                        ])]))

    async def parsing_contacts(self, client):
        """
        Парсинг контактов Telegram аккаунта

        :param client: Телеграм клиент
        """
        entities: list = []  # Создаем список сущностей
        for contact in await self.get_and_parse_contacts(client=client):  # Выводим результат parsing
            await self.get_user_data(user=contact, entities=entities)
            logger.info(contact)
        return entities

    async def recording_contacts_in_the_database(self, client) -> None:
        """
        Парсинг и запись контактов в базу данных

        :param client: Телеграм клиент
        """
        try:
            entities = await self.parsing_contacts(client)

            for raw_contact in entities:
                contact_dict = {
                    "username": raw_contact[0],
                    "user_id": raw_contact[1],
                    "access_hash": raw_contact[2],
                    "first_name": raw_contact[3],
                    "last_name": raw_contact[4],
                    "phone": raw_contact[5],
                    "online_at": raw_contact[6],
                    "photo_status": raw_contact[7],
                    "premium_status": raw_contact[8],
                }

                write_to_database_contacts_accounts(contact_dict)
        except Exception as error:
            logger.exception(error)

    async def we_get_the_account_id(self, client) -> None:
        """
        Получаем id аккаунта и удаляем контакты с аккаунта

        :param client: Телеграм клиент
        """
        try:
            for user in await self.get_and_parse_contacts(client):  # Выводим результат parsing
                logger.info(f"Пользователь: {user}")
                await client(functions.contacts.DeleteContactsRequest(id=[await self.user_info.get_user_id(user)]))
        except Exception as error:
            logger.exception(error)

    async def get_and_parse_contacts(self, client):
        """
        Получаем контакты

        :param client: Телеграм клиент
        """
        try:
            all_participants: list = []
            result = await client(functions.contacts.GetContactsRequest(hash=0))
            await self.app_logger.log_and_display(f"{result}")
            all_participants.extend(result.users)
            return all_participants
        except (SessionRevokedError, AuthKeyUnregisteredError) as e:
            logger.warning(f"Сессия отозвана или недействительна: {e}")
            return []  # Возвращаем пустой список вместо None
        except Exception as error:
            logger.exception(error)
            return []

    async def add_contact_to_phone_book(self, client) -> None:
        """
        Добавляем контакт в телефонную книгу

        :param client: Телеграм клиент
        """
        try:
            records: list = getting_contacts_from_database()  # Получаем список номеров из базы данных

            await self.app_logger.log_and_display(f"Всего номеров: {len(records)}")
            entities: list = []  # Создаем список сущностей
            for rows in records:
                logger.info(rows)
                # Добавляем контакт в телефонную книгу
                await client(functions.contacts.ImportContactsRequest(
                    contacts=[types.InputPhoneContact(client_id=0, phone=rows, first_name="Номер", last_name=rows)]
                ))
                try:
                    # Получаем данные номера телефона https://docs.telethon.dev/en/stable/concepts/entities.html
                    contact = await client.get_entity(rows)
                    await self.get_user_data(contact, entities)
                    await self.app_logger.log_and_display(f"➕ Контакт с добавлен в телефонную книгу!")
                    await asyncio.sleep(4)
                    delete_contact_db(phone=rows)  # После работы с номером телефона, программа удаляет номер со списка
                except ValueError:
                    await self.app_logger.log_and_display(
                        translations["ru"]["errors"]["contact_not_registered_or_cannot_add"])
                    delete_contact_db(phone=rows)  # После работы с номером телефона, программа удаляет номер со списка
            client.disconnect()  # Разрываем соединение telegram
            add_member_to_db(log_data=entities)  # Запись должна быть в таблицу members
        except Exception as error:
            logger.exception(error)

    async def get_user_data(self, user, entities) -> None:
        """
        Получаем данные пользователя

        :param user: Телеграм пользователя
        :param entities: Список сущностей
        """
        try:
            entities.append(
                [
                    await self.user_info.get_username(user),
                    await self.user_info.get_user_id(user),
                    await self.user_info.get_access_hash(user),
                    await self.user_info.get_first_name(user),
                    await self.user_info.get_last_name(user),
                    await self.user_info.get_user_phone(user),
                    await self.user_info.get_user_online_status(user),
                    await self.user_info.get_photo_status(user),
                    await self.user_info.get_user_premium_status(user)
                ]
            )
        except Exception as error:
            logger.exception(error)
