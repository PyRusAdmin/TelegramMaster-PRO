# -*- coding: utf-8 -*-
import asyncio

import flet as ft  # Импортируем библиотеку flet

from src.core.configs import BUTTON_HEIGHT, BUTTON_WIDTH, WIDTH_WIDE_BUTTON
from src.locales.translations_loader import translations


class GUIProgram:
    """Элементы графического интерфейса программы."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.color_diver = "red"

    async def build_link_input_with_save_button(self, label_text, width):
        """
        Создаёт текстовое поле для ввода ссылок.

        :param label_text: Текст, отображаемый над полем ввода
        :param width: Ширина поля ввода
        :return: Объект TextField
        """
        # Поле ввода, для ссылок для подписки
        link_input = ft.TextField(
            label=label_text,
            label_style=ft.TextStyle(color=ft.Colors.GREY_400),
            width=width
        )
        return link_input

    async def compose_link_input_row(self, link_input: ft.TextField):
        """
        Создаёт горизонтальный контейнер с полем ввода ссылки.

        :param link_input: Поле ввода ссылки
        :return: Контейнер Row с полем ввода
        """
        return ft.Row(
            controls=[
                link_input,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

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
            padding=1,  # Внутренний отступ контейнера (маленький, чтобы кнопка не "прилипала" к краям)
            content=ft.Button(
                content=text,  # Текст кнопки, переданный как параметр
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(  # Стиль кнопки с закруглёнными краями
                        radius=3
                    )
                ),
                width=BUTTON_WIDTH,  # Ширина кнопки берётся из конфигурации
                height=BUTTON_HEIGHT,  # Высота кнопки берётся из конфигурации
                on_click=lambda _: asyncio.create_task(self.page.push_route(route)),
                # При клике — переход по указанному маршруту
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

    async def diver_castom(self):
        """
        Создает разделительную линию в интерфейсе.

        :return: Объект Divider
        """
        return ft.Divider(height=1, color=self.color_diver)

    async def vertical_diver(self):
        """
        Создает вертикальную разделительную линию

        :return: Объект VerticalDivider
        """
        return ft.VerticalDivider(width=1, color=self.color_diver)

    def create_account_dropdown(self, account_data):
        """
        Создаёт выпадающий список (Dropdown) для выбора аккаунта.

        :param account_data: Список кортежей вида (phone: str, session_str: str)
        :param width: Ширина выпадающего списка
        :return: Экземпляр ft.Dropdown
        """
        # Создаём опции: текст — номер, ключ — session_string
        account_options = [
            ft.DropdownOption(
                text=phone,
                key=session_str
            )
            for phone, session_str in account_data
        ]

        # Создаем выпадающий список с названием "Выберите аккаунт"
        return ft.Dropdown(
            label="📂 Выберите аккаунт",  # ✅ Название выпадающего списка
            width=WIDTH_WIDE_BUTTON,  # ✅ Ширина выпадающего списка
            options=account_options,  # ✅ Опции выпадающего списка
            autofocus=True,  # ✅ Автозаполнение
            expand=True,  # Полноразмерное расширение (при изменении размера окна, подстраивается под размер)
        )
