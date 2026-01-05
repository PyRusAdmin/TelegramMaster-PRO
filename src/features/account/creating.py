# -*- coding: utf-8 -*-
import flet as ft
from loguru import logger
from telethon import TelegramClient
from telethon import functions

from src.core.config.configs import BUTTON_HEIGHT, WIDTH_WIDE_BUTTON
from src.core.database.account import getting_account, get_account_list
from src.core.utils import Utils
from src.features.account.connect import TGConnect
from src.gui.gui import AppLogger, list_view
from src.gui.gui_elements import GUIProgram
from src.gui.notification import show_notification
from src.locales.translations_loader import translations


class CreatingGroupsAndChats:
    """
    Создание групп (чатов) в автоматическом режиме
    """

    def __init__(self, page: ft.Page):
        """
        Инициализация класса для создания групп и чатов Telegram.

        :param page: Страница интерфейса Flet для отображения элементов управления
        """
        self.page = page
        self.connect = TGConnect(page=page)
        self.app_logger = AppLogger(page=page)
        self.utils = Utils(page=page)
        self.gui_program = GUIProgram()
        self.session_string = getting_account()  # Получаем строку сессии из файла базы данных
        self.account_data = get_account_list()  # Получаем список аккаунтов из базы данных

    async def creating_groups_and_chats(self) -> None:
        """
        Создание групп (чатов) в автоматическом режиме

        :param page: Страница интерфейса Flet для отображения элементов управления
        :return: None
        """
        self.page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        self.page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        # Создаём опции: текст — номер, ключ — session_string
        account_options = [
            ft.DropdownOption(text=phone, key=session_str)
            for phone, session_str in self.account_data
        ]
        # Создаем выпадающий список с названиями групп
        account_drop_down_list = ft.Dropdown(
            label="📂 Выберите аккаунт",  # ✅ Название выпадающего списка
            width=WIDTH_WIDE_BUTTON,  # ✅ Ширина выпадающего списка
            options=account_options,  # ✅ Опции выпадающего списка
            autofocus=True  # ✅ Автозаполнение
        )

        async def add_items(_):
            """
            🚀 Запускает процесс создания групп и отображает статус в интерфейсе.
            """
            selected_account = account_drop_down_list.value  # ← Получаем key выбранного аккаунта

            start = await self.app_logger.start_time()
            self.page.update()

            try:
                client: TelegramClient = await self.connect.client_connect_string_session(session_name=selected_account)
                # await self.connect.getting_account_data(client=client)
                await client(functions.channels.CreateChannelRequest(title='My awesome title',
                                                                     about='Description for your group',
                                                                     megagroup=True))
                await self.app_logger.log_and_display(
                    message=translations["ru"]["notifications"]["notification_creating"])
            except TypeError:
                pass
            except Exception as error:
                logger.exception(error)
            await self.app_logger.end_time(start=start)
            await show_notification(page=self.page,
                                    message="🔚 Создания групп (чатов)")  # Выводим уведомление пользователю

        # Добавляем элементы интерфейса на страницу
        self.page.views.append(ft.View("/creating_groups_and_chats_menu",
                                       [await self.gui_program.key_app_bar(),
                                        ft.Text(spans=[
                                            ft.TextSpan(translations["ru"]["menu"]["create_groups"], ft.TextStyle(
                                                size=20, weight=ft.FontWeight.BOLD,
                                                foreground=ft.Paint(gradient=ft.PaintLinearGradient((0, 20), (150, 20),
                                                                                                    [ft.Colors.PINK,
                                                                                                     ft.Colors.PURPLE]))))]),
                                        list_view,
                                        account_drop_down_list,
                                        ft.Button(
                                              translations["ru"]["buttons"]["start"],
                                              width=WIDTH_WIDE_BUTTON,
                                              height=BUTTON_HEIGHT,
                                              on_click=add_items),
                                        ]))
        self.page.update()
# 144
