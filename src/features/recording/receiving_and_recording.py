from datetime import datetime, time

import flet as ft  # Импортируем библиотеку flet
import openpyxl

from src.core.database.account import Account
from src.core.database.database import (
    read_parsed_chat_participants_from_db, MembersGroups, GroupsSendMessages, AccountContacts, WritingGroupLinks,
    GroupsAndChannels, MembersAdmin, LinksInviting, Contact, Proxy
)


class ReceivingAndRecording:
    """Работа с базой данных"""

    def __init__(self, page: ft.Page):
        self.page = page  # Сохраняем ссылку на страницу Flet

    async def clear_database(self):
        """Очистка базы данных"""

        # Удаляем все строки из таблицы MembersGroups
        rows_deleted = MembersGroups.delete().execute()
        print(f"Удалено строк: {rows_deleted}")

        # Удаляем все строки из таблицы GroupsSendMessages
        rows_deleted = GroupsSendMessages.delete().execute()
        print(f"Удалено строк: {rows_deleted}")

        # Удаляем все строки из таблицы AccountContacts
        rows_deleted = AccountContacts.delete().execute()
        print(f"Удалено строк: {rows_deleted}")

        # Удаляем все строки из таблицы WritingGroupLinks
        rows_deleted = WritingGroupLinks.delete().execute()
        print(f"Удалено строк: {rows_deleted}")

        # Удаляем все строки из таблицы GroupsAndChannels
        rows_deleted = GroupsAndChannels.delete().execute()
        print(f"Удалено строк: {rows_deleted}")

        # Удаляем все строки из таблицы MembersAdmin
        rows_deleted = MembersAdmin.delete().execute()
        print(f"Удалено строк: {rows_deleted}")

        # Удаляем все строки из таблицы LinksInviting
        rows_deleted = LinksInviting.delete().execute()
        print(f"Удалено строк: {rows_deleted}")

        # Удаляем все строки из таблицы Contact
        rows_deleted = Contact.delete().execute()
        print(f"Удалено строк: {rows_deleted}")

        # Удаляем все строки из таблицы Proxy
        rows_deleted = Proxy.delete().execute()
        print(f"Удалено строк: {rows_deleted}")

        # Удаляем все строки из таблицы Account
        rows_deleted = Account.delete().execute()
        print(f"Удалено строк: {rows_deleted}")

        # Возврат в главное меню
        self.page.route = "/"
        await self.page.push_route("/")

    # В классе ReceivingAndRecording
    async def write_data_to_excel(self, file_name: str):
        """
        Запись данных в Excel файл и возврат в главное меню.
        :param file_name: Имя файла для сохранения данных
        """
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Chat Participants"
        sheet.append([
            "username", "id", "access_hash", "first_name", "last_name", "user_phone", "online_at", "photos_id",
            "user_premium"
        ])
        for row in read_parsed_chat_participants_from_db():
            clean_row = []
            for item in row:
                if isinstance(item, (datetime, time)) and item.tzinfo is not None:
                    item = item.replace(tzinfo=None)
                clean_row.append(item)
            sheet.append(clean_row)

        workbook.save(file_name)

        # Возврат в главное меню
        self.page.route = "/"
        await self.page.push_route("/")  # или page.update() + вызов route_change, но go() лучше
