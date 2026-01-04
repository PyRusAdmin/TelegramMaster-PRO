# -*- coding: utf-8 -*-
import flet as ft

from src.core.config.configs import (BUTTON_HEIGHT, WIDTH_WIDE_BUTTON)
from src.gui.gui_elements import GUIProgram
from src.locales.translations_loader import translations


class Menu:

    def __init__(self, page: ft.Page):
        self.page = page
        self.gui_program = GUIProgram()

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
