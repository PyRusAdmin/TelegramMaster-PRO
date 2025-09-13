# -*- coding: utf-8 -*-
import flet as ft

from src.features.account.connect import TGConnect


class TGChek:

    def __init__(self, page: ft.Page):
        self.page = page
        self.connect = TGConnect(page)

    async def account_verification_menu(self):
        """
        Меню 🔍 Проверка аккаунтов
        """

        # async def validation_check(_) -> None:
        #     """Проверка валидности аккаунтов"""
        #     await self.connect.verify_all_accounts()

        # async def renaming_accounts(_):
        #     """Переименование аккаунтов"""
        #     await self.connect.renaming_accounts()

        # async def checking_for_spam_bots(_):
        #     """Проверка на спам ботов"""
        #     await self.connect.check_for_spam()

        # async def full_verification(_):
        #     """Полная проверка аккаунтов"""
        #     await self.connect.full_verification()

        # self.page.views.append(
        #     ft.View("/account_verification_menu",
        #             [await GUIProgram().key_app_bar(),  # Добавляет кнопку назад на страницу (page)
        #              ft.Text(spans=[ft.TextSpan(
        #                  translations["ru"]["menu"]["account_check"],
        #                  ft.TextStyle(size=20, weight=ft.FontWeight.BOLD,
        #                               foreground=ft.Paint(
        #                                   gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
        #                                                                                        ft.Colors.PURPLE])), ), ), ], ),
        #              list_view,
        #              ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
        #                  # 🤖 Проверка через спам бот
        #                  ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
        #                                    text=translations["ru"]["account_verification"]["spam_check"],
        #                                    on_click=checking_for_spam_bots),
        #                  # ✅ Проверка на валидность
        #                  ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
        #                                    text=translations["ru"]["account_verification"]["validation"],
        #                                    on_click=validation_check),
        #                  # ✏️ Переименование аккаунтов
        #                  ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
        #                                    text=translations["ru"]["account_verification"]["renaming"],
        #                                    on_click=renaming_accounts),
        #                  # 🔍 Полная проверка
        #                  ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
        #                                    text=translations["ru"]["account_verification"]["full_verification"],
        #                                    on_click=full_verification),
        #              ])]))
