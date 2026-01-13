# -*- coding: utf-8 -*-
import flet as ft  # Импортируем библиотеку flet

from src.locales.translations_loader import translations


class GUIProgram:
    """Элементы графического интерфейса программы."""

    def __init__(self, page: ft.Page):
        self.page = page

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
