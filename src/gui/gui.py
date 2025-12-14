# -*- coding: utf-8 -*-
import datetime

import flet as ft
from loguru import logger

list_view = ft.ListView(expand=10, spacing=1, padding=2, auto_scroll=True)


class AppLogger:

    def __init__(self, page: ft.Page):
        """
        Инициализация класса для логирования и отображения сообщений в GUI.

        :param page: Страница интерфейса Flet для отображения элементов управления
        """
        self.page = page
        self.list_view = list_view  # Используем переданный list_view

    async def start_time(self) -> datetime.datetime:
        """
        Фиксирует и отображает время старта операции.

        Записывает текущее время и выводит его в лог как метку начала выполнения.

        :return: Время старта операции для последующего расчета продолжительности
        """
        start = datetime.datetime.now()
        await self.log_and_display(message=f'▶️ Время старта: {start}')
        return start

    async def end_time(self, start: datetime.datetime):
        """
        Фиксирует и отображает время завершения операции и ее продолжительность.

        Рассчитывает и выводит в лог время окончания операции и общую продолжительность
        выполнения от момента старта до завершения.

        :param start: Время старта операции, полученное от start_time()
        :return: None
        """
        finish = datetime.datetime.now()
        await self.log_and_display(message=f'⏹️ Время окончания: {finish}')
        await self.log_and_display(message=f'⏱️ Время работы: {finish - start}')

    async def log_and_display(self, message: str, level: str = "INFO"):
        """
        Выводит сообщение в GUI и записывает лог с указанным уровнем.

        :param message: Текст сообщения для отображения и записи в лог
        :param level: Уровень логирования ("info" или "error"), по умолчанию "info"
        :return: None
        """
        if level.lower() == "error":
            logger.error(message)
        else:
            self.list_view.controls.append(ft.Text(message))
            logger.info(message)
        self.page.update()
