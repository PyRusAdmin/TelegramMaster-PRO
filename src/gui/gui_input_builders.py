# -*- coding: utf-8 -*-
import flet as ft  # Импортируем библиотеку flet


class GUIProgram:
    """
    Компонент Flet для отображения текстового поля ввода и кнопки сохранения.
    Используется для ввода ссылок на Telegram-группы и каналы, на которые необходимо подписаться.
    """

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
