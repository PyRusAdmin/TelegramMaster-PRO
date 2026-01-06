# -*- coding: utf-8 -*-
import flet as ft  # Импортируем библиотеку flet

from src.locales.translations_loader import translations


class GUIProgram:
    """Элементы графического интерфейса программы."""

    @staticmethod
    async def key_app_bar(page: ft.Page):
        """
        Создает верхнюю панель приложения с кнопкой возврата в главное меню.
        """
        return ft.AppBar(
            toolbar_height=40,
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                tooltip="На главную",
                on_click=lambda _: page.go("/"),
            ),
            title=ft.Text(translations["ru"]["menu"]["main"]),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        )

    @staticmethod
    async def outputs_text_gradient():
        """
        Создает текст с градиентным оформлением.

        :return: Объект Text с градиентом
        """
        # Создаем текст с градиентным оформлением через TextStyle
        return ft.Text(
            spans=[
                ft.TextSpan(
                    translations["ru"]["menu"]["parsing"],
                    ft.TextStyle(
                        size=20,
                        weight=ft.FontWeight.NORMAL,
                        foreground=ft.Paint(
                            color=ft.Colors.PINK,
                        ),
                    ),
                )
            ],
        )

    # TODO: Применить во всем проекте, для одинакового оформления GUI программы
    @staticmethod
    async def diver_castom():
        """
        Создает разделительную линию в интерфейсе.

        :return: Объект Divider
        """
        return ft.Divider(height=1, color="red")
