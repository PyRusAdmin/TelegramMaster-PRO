# -*- coding: utf-8 -*-
import flet as ft  # Импортируем библиотеку flet
import openpyxl

from src.core.database.database import read_parsed_chat_participants_from_db


class ReceivingAndRecording:

    def __init__(self, page: ft.Page):
        self.page = page  # Сохраняем ссылку на страницу Flet

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
            sheet.append(row)

        workbook.save(file_name)

        # Возврат в главное меню
        self.page.route = "/"
        self.page.go("/")  # или page.update() + вызов route_change, но go() лучше
