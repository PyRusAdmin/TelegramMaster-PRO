import flet as ft
from loguru import logger
from telethon import TelegramClient
from telethon import functions

from src.core.configs import BUTTON_HEIGHT, WIDTH_WIDE_BUTTON
from src.core.database.account import getting_account, get_account_list
from src.core.utils import Utils
from src.features.account.connect import TGConnect
from src.gui.gui import AppLogger, list_view
from src.gui.gui_elements import GUIProgram
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
        self.page = page  # Страница интерфейса Flet для отображения элементов управления
        self.connect = TGConnect(page=page)  # Класс для подключения к Telegram
        self.app_logger = AppLogger(page=page)  # Класс для логирования приложения
        self.utils = Utils(page=page)  # Класс для вспомогательных функций
        self.gui_program = GUIProgram(page=page)  # Класс для работы с графическим интерфейсом
        self.session_string = getting_account()  # Получаем строку сессии из файла базы данных
        self.account_data = get_account_list()  # Получаем список аккаунтов из базы данных

    async def creating_groups_and_chats(self) -> None:
        """
        Создание групп (чатов) в автоматическом режиме

        :return: None
        """
        self.page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        account_drop_down_list = self.gui_program.create_account_dropdown(self.account_data)

        async def add_items(_):
            """
            🚀 Запускает процесс создания групп и отображает статус в интерфейсе.
            """
            selected_account = account_drop_down_list.value  # ← Получаем key выбранного аккаунта

            start = await self.app_logger.start_time()
            self.page.update()

            try:
                client: TelegramClient = await self.connect.client_connect_string_session(session_name=selected_account)

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
            await self.gui_program.show_notification(  # ✅ Показываем уведомление пользователю
                message="🔚 Создания групп (чатов)")  # Выводим уведомление пользователю

        # Добавляем элементы интерфейса на страницу
        self.page.views.append(
            ft.View(
                route="/creating_groups_and_chats_menu",
                appbar=await self.gui_program.key_app_bar(),  # Кнопка назад
                controls=[
                    await self.gui_program.create_gradient_text(
                        text=translations["ru"]["menu"]["create_groups"]
                    ),
                    list_view,
                    account_drop_down_list,
                    ft.Button(
                        content=translations["ru"]["buttons"]["start"],
                        width=WIDTH_WIDE_BUTTON,
                        height=BUTTON_HEIGHT,
                        on_click=add_items),
                ]))
        self.page.update()
# 144
