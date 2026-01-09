# -*- coding: utf-8 -*-
import flet as ft  # Импортируем библиотеку flet
import openpyxl

from src.core.database.database import read_parsed_chat_participants_from_db


class ReceivingAndRecording:

    # В классе ReceivingAndRecording
    @staticmethod
    async def write_data_to_excel(page: ft.Page, file_name: str):
        """
        Запись данных в Excel файл и возврат в главное меню.
        :param page: Страница Flet
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
        page.route = "/"
        await page.go("/")  # или page.update() + вызов route_change, но go() лучше
