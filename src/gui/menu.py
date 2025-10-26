# -*- coding: utf-8 -*-
import base64

import flet as ft

from src.core.configs import BUTTON_HEIGHT, WIDTH_WIDE_BUTTON
from src.core.configs import PROGRAM_NAME, DATE_OF_PROGRAM_CHANGE, PROGRAM_VERSION
from src.gui.gui_elements import GUIProgram
from src.gui.gui import list_view
from src.locales.translations_loader import translations
from flet import DecorationImage, ImageFit


class Menu:

    def __init__(self, page: ft.Page):
        self.page = page
        self.gui_program = GUIProgram()

    async def main_menu_program(self):
        """
        Главное меню программы
        """
        # Загрузка изображения из файла и преобразование в base64
        with open("src/gui/image_display/telegram.png", "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode("utf-8")

        # Создание изображения и установка
        img = ft.Image(
            src_base64=img_base64,
            width=30,
            height=30,
            fit=ft.ImageFit.CONTAIN,
        )

        self.page.views.append(
            ft.View("/", [await self.gui_program.key_app_bar(),
                          ft.Row([
                              # Левая колонка — кнопки
                              ft.Column([
                                  # 🚀 Инвайтинг
                                  ft.ElevatedButton(width=350, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["inviting_menu"]["inviting"],
                                                    on_click=lambda _: self.page.go("/inviting")),
                                  # 📊 Парсинг
                                  ft.ElevatedButton(width=350, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["menu"]["parsing"],
                                                    on_click=lambda _: self.page.go("/parsing")),
                                  # 📇 Работа с контактами
                                  ft.ElevatedButton(width=350, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["menu"]["contacts"],
                                                    on_click=lambda _: self.page.go("/working_with_contacts")),
                                  # 🔄 Подписка, отписка
                                  ft.ElevatedButton(width=350, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["menu"]["subscribe_unsubscribe"],
                                                    on_click=lambda _: self.page.go("/subscribe_unsubscribe")),
                                  # 🔐 Подключение аккаунтов
                                  ft.ElevatedButton(width=350, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["menu"]["account_connect"],
                                                    on_click=lambda _: self.page.go("/account_connection_menu")),
                                  # 📨 Отправка сообщений в личку
                                  ft.ElevatedButton(width=350, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["message_sending_menu"][
                                                        "sending_personal_messages_with_limits"],
                                                    on_click=lambda _: self.page.go(
                                                        "/sending_files_to_personal_account_with_limits")),
                                  # ❤️ Работа с реакциями
                                  ft.ElevatedButton(width=350, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["menu"]["reactions"],
                                                    on_click=lambda _: self.page.go("/working_with_reactions")),
                                  # 🔍 Проверка аккаунтов
                                  ft.ElevatedButton(width=350, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["menu"]["account_check"],
                                                    on_click=lambda _: self.page.go("/account_verification_menu")),
                                  # 👥 Создание групп (чатов)
                                  ft.ElevatedButton(width=350, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["menu"]["create_groups"],
                                                    on_click=lambda _: self.page.go("/creating_groups")),
                                  # ✏️ Редактирование_BIO
                                  ft.ElevatedButton(width=350, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["menu"]["edit_bio"],
                                                    on_click=lambda _: self.page.go("/bio_editing")),
                                  # 👁️‍🗨️ Накручиваем просмотры постов
                                  ft.ElevatedButton(width=350, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["reactions_menu"][
                                                        "we_are_winding_up_post_views"],
                                                    on_click=lambda _: self.page.go("/viewing_posts_menu")),
                                  # 💬 Рассылка сообщений по чатам
                                  ft.ElevatedButton(width=350, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["message_sending_menu"][
                                                        "sending_messages_via_chats"],
                                                    on_click=lambda _: self.page.go(
                                                        "/sending_messages_files_via_chats")),
                                  # 📋 Импорт списка от ранее спарсенных данных
                                  ft.ElevatedButton(width=350, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["parsing_menu"][
                                                        "importing_a_list_of_parsed_data"],
                                                    on_click=lambda _: self.page.go(
                                                        "/importing_a_list_of_parsed_data")),
                                  # ⚙️ Настройки
                                  ft.ElevatedButton(width=350, height=BUTTON_HEIGHT,
                                                    text=translations["ru"]["menu"]["settings"],
                                                    on_click=lambda _: self.page.go("/settings")),
                              ], scroll=ft.ScrollMode.AUTO),
                              # Вертикальный разделитель - улучшенные параметры
                              ft.VerticalDivider(
                                  width=20,  # Ширина контейнера
                                  thickness=2,  # Толщина линии
                                  color=ft.Colors.GREY_400  # Цвет линии
                              ),
                              # Правая колонка — текст
                              ft.Column([
                                  ft.Text(spans=[ft.TextSpan(
                                      f"{PROGRAM_NAME}",
                                      ft.TextStyle(
                                          size=40,
                                          weight=ft.FontWeight.BOLD,
                                          foreground=ft.Paint(
                                              gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                                   ft.Colors.PURPLE])),
                                      ),
                                  )], ),

                                  ft.Text(
                                      disabled=False,
                                      spans=[
                                          ft.TextSpan(text=f"Версия программы: {PROGRAM_VERSION}"),
                                      ],
                                  ),

                                  ft.Text(
                                      disabled=False,
                                      spans=[
                                          ft.TextSpan(text=f"Дата выхода: {DATE_OF_PROGRAM_CHANGE}"),
                                      ],
                                  ),

                                  ft.Row([img,
                                          ft.Text(disabled=False,
                                                  spans=[ft.TextSpan(translations["ru"]["main_menu_texts"]["text_1"]),
                                                         ft.TextSpan(
                                                             translations["ru"]["main_menu_texts"]["text_link_1"],
                                                             ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                                                             url=translations["ru"]["main_menu_texts"][
                                                                 "text_2"], ), ], ),
                                          ]),
                                  ft.Row([
                                      img,
                                      ft.Text(disabled=False,
                                              spans=[ft.TextSpan(translations["ru"]["main_menu_texts"]["text_2"]),
                                                     ft.TextSpan(translations["ru"]["main_menu_texts"]["text_link_2"],
                                                                 ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                                                                 url=translations["ru"]["main_menu_texts"][
                                                                     "text_2"], ), ], ),
                                  ])
                              ]),
                          ], vertical_alignment=ft.CrossAxisAlignment.START, expand=True)
                          ]))

    async def settings_menu(self):
        """
        Меню настройки
        """
        self.page.views.append(
            ft.View("/settings",
                    [await self.gui_program.key_app_bar(),
                     ft.Text(spans=[ft.TextSpan(translations["ru"]["menu"]["settings"],
                                                ft.TextStyle(size=20, weight=ft.FontWeight.BOLD, foreground=ft.Paint(
                                                    gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                                         ft.Colors.PURPLE]))))]),
                     ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                         # 👍 Выбор реакций
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["menu_settings"]["choice_of_reactions"],
                                           on_click=lambda _: self.page.go("/choice_of_reactions")),
                         # 🔐 Запись proxy
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["menu_settings"]["proxy_entry"],
                                           on_click=lambda _: self.page.go("/proxy_entry")),
                         # 📝 Запись api_id, api_hash
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["menu_settings"]["recording_api_id_api_hash"],
                                           on_click=lambda _: self.page.go("/recording_api_id_api_hash")),
                         # ✉️ Запись сообщений
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["menu_settings"]["message_recording"],
                                           on_click=lambda _: self.page.go("/message_recording")),
                         # 🔗 Запись ссылки для реакций
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["menu_settings"]["recording_reaction_link"],
                                           on_click=lambda _: self.page.go("/recording_reaction_link")),
                     ])]))

    async def reactions_menu(self):
        """
        Меню ❤️ Работа с реакциями
        """
        self.page.views.append(
            ft.View("/working_with_reactions",
                    [await self.gui_program.key_app_bar(),  # Кнопка "Назад"
                     ft.Text(spans=[ft.TextSpan(
                         translations["ru"]["menu"]["reactions"],
                         ft.TextStyle(
                             size=20, weight=ft.FontWeight.BOLD,
                             foreground=ft.Paint(
                                 gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                      ft.Colors.PURPLE])), ), ), ], ),
                     ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                         # 👍 Ставим реакции
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["reactions_menu"]["setting_reactions"],
                                           on_click=lambda _: self.page.go("/setting_reactions")),
                         # 🤖 Автоматическое выставление реакций
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["reactions_menu"]["automatic_setting_of_reactions"],
                                           on_click=lambda _: self.page.go("/automatic_setting_of_reactions")),
                     ])]))
