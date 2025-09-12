# -*- coding: utf-8 -*-
import flet as ft  # Импортируем библиотеку flet

from src.core.configs import WIDTH_WIDE_BUTTON, BUTTON_HEIGHT
from src.features.account.parsing.gui_elements import GUIProgram
from src.locales.translations_loader import translations


class FunctionButton:

    def __init__(self, page: ft.Page):
        self.page = page

    def function_button_ready(self, btn_click, back_button_clicked, user_input) -> None:
        """
        Функция для кнопки "Готово" и кнопки "Назад"

        :param btn_click: Кнопка "Готово"
        :param user_input: Введенные данные пользователем
        :param back_button_clicked: Кнопка "Назад"
        :return: None
        """
        self.page.views.append(
            ft.View(
                "/bio_editing",
                [
                    user_input,
                    ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                    ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                      text=translations["ru"]["buttons"]["done"], on_click=btn_click),
                    # Кнопка "Готово"
                    ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                      text=translations["ru"]["buttons"]["back"], on_click=back_button_clicked),
                    # Кнопка "Назад"
                ], ))

    def function_button_ready_reactions(self, btn_click, back_button_clicked, chat, message) -> None:
        """
        Функция для кнопки "Готово" и кнопки "Назад"

        :param btn_click: Кнопка "Готово"
        :param chat: Введенные данные пользователем
        :param message: Введенные данные пользователем
        :param back_button_clicked:Кнопка "Назад"
        :return: None
        """
        self.page.views.append(
            ft.View(
                "/working_with_reactions",
                [
                    chat,  # Поле ввода ссылки на чат
                    message,  # Поле ввода ссылки пост
                    ft.Column(),  # Заполнитель для приветствия или другого содержимого (необязательно)
                    ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                      text=translations["ru"]["buttons"]["done"], on_click=btn_click),
                    # Кнопка "Готово"
                    ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                      text=translations["ru"]["buttons"]["back"], on_click=back_button_clicked),
                    # Кнопка "Назад"
                ], ))

    async def function_button_ready_viewing(self, btn_click, link_channel, link_post):
        """
        Функция для кнопки "Готово" и кнопки "Назад"

        :param btn_click: Кнопка "Готово"
        :param link_channel: Введенные данные пользователем
        :param link_post: Введенные данные пользователем
        """
        # Добавление представления на страницу
        self.page.views.append(
            ft.View(
                "/viewing_posts_menu",  # Маршрут для этого представления
                [
                    await GUIProgram().key_app_bar(),  # Кнопка "Назад"
                    link_channel,  # Поле ввода ссылки на чат
                    link_post,  # Поле ввода ссылки пост
                    ft.Column(),  # Колонка для размещения других элементов (при необходимости)
                    ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                      text=translations["ru"]["buttons"]["done"], on_click=btn_click),
                ]))
