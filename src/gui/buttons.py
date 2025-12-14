# -*- coding: utf-8 -*-
import flet as ft  # Импортируем библиотеку flet

from src.core.config.configs import WIDTH_WIDE_BUTTON, BUTTON_HEIGHT
from src.gui.gui_elements import GUIProgram
from src.gui.gui import list_view
from src.locales.translations_loader import translations


class FunctionButton:

    def __init__(self, page: ft.Page):
        """
        Инициализация класса для управления кнопками в интерфейсе.

        :param page: Страница интерфейса Flet для отображения элементов управления
        """
        self.page = page
        self.gui_program = GUIProgram()

    async def function_button_ready_viewing(self, number_views, btn_click, link_channel, link_post):
        """
        Создает интерфейс для накрутки просмотров постов.

        :param number_views: Поле ввода количества просмотров
        :param btn_click: Функция-обработчик для кнопки "Готово"
        :param link_channel: Поле ввода ссылки на канал
        :param link_post: Поле ввода ссылки на пост
        :return: None
        """
        # Добавление представления на страницу
        self.page.views.append(
            ft.View(
                "/viewing_posts_menu",  # Маршрут для этого представления
                [
                    await self.gui_program.key_app_bar(),  # Кнопка "Назад"

                    ft.Text(spans=[ft.TextSpan(
                        translations["ru"]["reactions_menu"]["we_are_winding_up_post_views"],
                        ft.TextStyle(
                            size=20, weight=ft.FontWeight.BOLD,
                            foreground=ft.Paint(
                                gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                     ft.Colors.PURPLE])), ), ), ], ),

                    list_view,  # Отображение логов 📝
                    number_views,  # Поле ввода количества просмотров основываясь на количестве аккаунтов
                    link_channel,  # Поле ввода ссылки на чат
                    link_post,  # Поле ввода ссылки пост
                    ft.Column(),  # Колонка для размещения других элементов (при необходимости)
                    ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                      text=translations["ru"]["buttons"]["done"], on_click=btn_click),
                ]))
