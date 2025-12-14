# -*- coding: utf-8 -*-
import flet as ft  # Импортируем библиотеку flet


# 344

class TimeInputRowBuilder:

    async def build_time_inputs_with_save_button(self, label_min, label_max, width):
        """
        Создаёт текстовые поля для ввода времени и возвращает их.

        :param label_min: Текст для поля ввода минимального значения
        :param label_max: Текст для поля ввода максимального значения
        :param width: Ширина полей ввода
        :return: Кортеж из двух объектов TextField
        """
        min_time_input = ft.TextField(label=label_min, label_style=ft.TextStyle(size=15), autofocus=True, width=width,
                                      text_size=12)
        max_time_input = ft.TextField(label=label_max, label_style=ft.TextStyle(size=15), autofocus=True, width=width,
                                      text_size=12)
        return min_time_input, max_time_input

    async def compose_time_input_row(self, min_time_input: ft.TextField, max_time_input: ft.TextField):
        """
        Создаёт горизонтальный контейнер (строку) с полем ввода и кнопкой.

        :param min_time_input: Текстовое поле для ввода минимального времени.
        :param max_time_input: Текстовое поле для ввода максимального времени.
        :return: Компонент ft.Row с размещёнными элементами.
        https://flet.dev/docs/cookbook/large-lists/#gridview
        """
        return ft.Row(
            controls=[
                min_time_input,
                max_time_input,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN  # или .START
        )


class LinkInputRowBuilder:
    """
    Компонент Flet для отображения текстового поля ввода и кнопки сохранения.
    Используется для ввода ссылок на Telegram-группы и каналы, на которые необходимо подписаться.
    """

    async def build_link_input_with_save_button(self, label_text, width):
        """
        Создаёт текстовое поле для ввода ссылок и кнопку сохранения.

        :param width: Ширина поля ввода
        :param label_text:  Текст, отображаемый над полем ввода.
        :return: Кортеж из двух элементов: ft.TextField
        https://flet.dev/docs/controls/textfield/
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
        Создаёт горизонтальный контейнер (строку) с полем ввода и кнопкой.

        :param link_input: Текстовое поле для ввода ссылок.
        :return: Компонент ft.Row с размещёнными элементами.
        https://flet.dev/docs/cookbook/large-lists/#gridview
        """
        return ft.Row(
            controls=[
                link_input,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
