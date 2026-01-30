# -*- coding: utf-8 -*-
import asyncio

import flet as ft  # Импортируем библиотеку flet

from src.core.configs import BUTTON_HEIGHT, BUTTON_WIDTH
from src.locales.translations_loader import translations


class GUIProgram:
    """Элементы графического интерфейса программы."""

    def __init__(self, page: ft.Page):
        self.page = page

    async def build_time_inputs_with_save_button(self, label_min, label_max, width):
        """
        Создаёт текстовые поля для ввода времени и возвращает их.

        :param label_min: Текст для поля ввода минимального значения
        :param label_max: Текст для поля ввода максимального значения
        :param width: Ширина полей ввода
        :return: Кортеж из двух объектов TextField
        """
        min_time_input = ft.TextField(
            label=label_min,
            label_style=ft.TextStyle(size=15),
            autofocus=True,
            width=width,
            text_size=12
        )
        max_time_input = ft.TextField(
            label=label_max,
            label_style=ft.TextStyle(size=15),
            autofocus=True,
            width=width,
            text_size=12
        )
        return min_time_input, max_time_input

    async def compose_time_input_row(self, min_time_input: ft.TextField, max_time_input: ft.TextField):
        """
        Создаёт горизонтальный контейнер с полями ввода времени.

        :param min_time_input: Поле ввода для минимального времени
        :param max_time_input: Поле ввода для максимального времени
        :return: Контейнер Row с полями ввода
        """
        return ft.Row(
            controls=[
                min_time_input,
                max_time_input,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN  # или .START
        )

    async def create_gradient_text(self, text):
        return ft.Text(
            spans=[
                ft.TextSpan(
                    text=text,
                    style=ft.TextStyle(
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        foreground=ft.Paint(
                            gradient=ft.PaintLinearGradient(
                                (0, 20),
                                (150, 20),
                                [
                                    ft.Colors.PINK,
                                    ft.Colors.PURPLE
                                ]
                            )
                        )
                    )
                )
            ]
        )

    async def menu_button(self, text: str, route: str):
        """
        Кнопка-меню главного экрана проекта
        :param text: Текст, отображаемый на кнопке меню.
        :type text: str
        :param route: Путь маршрута (например: "/parsing", "/settings"), на который будет выполнен переход при нажатии.
        :type route: str
        :return: Контейнер с кнопкой меню, готовый для добавления в layout (`Column`, `Row`, `View`).
        :rtype: ft.Container https://docs.flet.dev/controls/container/
        """
        return ft.Container(
            content=ft.Button(
                content=text,
                width=BUTTON_WIDTH,
                height=BUTTON_HEIGHT,
                on_click=lambda _: asyncio.create_task(self.page.push_route(route)),
            )
        )

    async def show_notification(self, message: str):
        """
        Показывает пользователю всплывающее уведомление на странице Flet.

        :param message: Текст уведомления
        :return: None
        """
        # Переход обратно после закрытия диалога
        dlg = ft.AlertDialog(title=ft.Text(message))
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    async def key_app_bar(self):
        """
        Создает верхнюю панель приложения с кнопкой возврата в главное меню.
        """
        return ft.AppBar(
            toolbar_height=40,
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                tooltip="На главную",
                on_click=lambda _: self.page.go("/"),
            ),
            title=ft.Text(translations["ru"]["menu"]["main"]),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        )

    # TODO: Применить во всем проекте, для одинакового оформления GUI программы
    @staticmethod
    async def diver_castom():
        """
        Создает разделительную линию в интерфейсе.

        :return: Объект Divider
        """
        return ft.Divider(height=1, color="red")
