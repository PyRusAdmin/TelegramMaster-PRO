# -*- coding: utf-8 -*-
import flet as ft

from src.core.configs import BUTTON_WIDTH, BUTTON_HEIGHT
from src.features.account.connect import TGConnect
from src.features.account.parsing.gui_elements import GUIProgram
from src.gui.gui import list_view
from src.locales.translations_loader import translations


class TGChek:

    def __init__(self, page: ft.Page):
        self.page = page
        self.connect = TGConnect(page)

    async def account_verification_menu(self):
        """
        Меню проверки аккаунтов
        """

        async def validation_check(_) -> None:
            """Проверка валидности аккаунтов"""
            await self.connect.verify_all_accounts()

        async def renaming_accounts(_):
            """Переименование аккаунтов"""
            await self.connect.get_account_details()

        async def checking_for_spam_bots(_):
            """Проверка на спам ботов"""
            await self.connect.check_for_spam()

        async def full_verification(_):
            """Полная проверка аккаунтов"""
            await self.connect.checking_all_accounts()

        self.page.views.append(
            ft.View("/account_verification_menu",
                    [await GUIProgram().key_app_bar(),  # Добавляет кнопку назад на страницу (page)
                     ft.Text(spans=[ft.TextSpan(
                         translations["ru"]["menu"]["account_check"],
                         ft.TextStyle(size=20, weight=ft.FontWeight.BOLD,
                                      foreground=ft.Paint(
                                          gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                               ft.Colors.PURPLE])), ), ), ], ),
                     list_view,
                     ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                         # 🤖 Проверка через спам бот
                         ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["account_verification"]["spam_check"],
                                           on_click=checking_for_spam_bots),
                         # ✅ Проверка на валидность
                         ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["account_verification"]["validation"],
                                           on_click=validation_check),
                         # ✏️ Переименование аккаунтов
                         ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["account_verification"]["renaming"],
                                           on_click=renaming_accounts),
                         # 🔍 Полная проверка
                         ft.ElevatedButton(width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["account_verification"]["full_verification"],
                                           on_click=full_verification),
                     ])]))
