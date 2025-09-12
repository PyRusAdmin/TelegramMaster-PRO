# -*- coding: utf-8 -*-
import asyncio  # Импортируем библиотеку для работы с асинхронным кодом
import re  # Импортируем библиотеку для работы с регулярными выражениями
import sys  # Импортируем библиотеку для работы с системным вызовом

import flet as ft  # Импортируем библиотеку flet
from loguru import logger  # Импортируем библиотеку loguru для логирования
from telethon.errors import SessionRevokedError
from telethon.tl.functions.messages import GetMessagesViewsRequest

from src.core.configs import path_accounts_folder, WIDTH_WIDE_BUTTON, BUTTON_HEIGHT
from src.core.utils import Utils
from src.features.account.TGConnect import TGConnect
from src.features.account.parsing.gui_elements import GUIProgram
from src.features.account.subscribe_unsubscribe.subscribe import Subscribe
from src.features.account.subscribe_unsubscribe.subscribe_unsubscribe import SubscribeUnsubscribeTelegram
from src.gui.buttons import FunctionButton
from src.gui.gui import AppLogger
from src.locales.translations_loader import translations


class ViewingPosts:
    """
    Функционал для накрутки просмотров постов в Telegram.
    """

    def __init__(self, page):
        self.page = page
        self.tg_connect = TGConnect(page=page)
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram(page=page)
        self.app_logger = AppLogger(page=page)
        self.utils = Utils(page=page)
        self.function_button = FunctionButton(page=page)
        self.subscribe = Subscribe(page=page)  # Инициализация экземпляра класса Subscribe (Подписка)

    async def viewing_posts_menu(self):
        """Отображает меню работы с просмотрами."""
        self.page.views.append(
            ft.View("/viewing_posts_menu",
                    [await GUIProgram().key_app_bar(),
                     ft.Text(spans=[ft.TextSpan(
                         translations["ru"]["reactions_menu"]["we_are_winding_up_post_views"],
                         ft.TextStyle(
                             size=20, weight=ft.FontWeight.BOLD,
                             foreground=ft.Paint(
                                 gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                      ft.Colors.PURPLE])), ), ), ], ),
                     ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                         # 👁️‍🗨️ Накручиваем просмотры постов
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["reactions_menu"]["we_are_winding_up_post_views"],
                                           on_click=lambda _: self.page.go("/we_are_winding_up_post_views")),
                     ])]))

    async def viewing_posts_request(self) -> None:
        """Окно с полями ввода и кнопками для накрутки просмотров."""
        try:
            # Поле для ввода ссылки на чат
            link_channel = ft.TextField(label="Введите ссылку на канал:", multiline=False, max_lines=1)
            link_post = ft.TextField(label="Введите ссылку на пост:", multiline=False, max_lines=1)

            async def btn_click(_) -> None:

                for session_name in self.utils.find_filess(directory_path=path_accounts_folder, extension='session'):
                    # client = await self.tg_connect.get_telegram_client(session_name=session_name, account_directory=path_accounts_folder)

                    client = await self.tg_connect.client_connect_string_session(session_name)

                    await self.app_logger.log_and_display(f"[+] Работаем с каналом: {link_channel.value}")

                    await self.subscribe.subscribe_to_group_or_channel(client=client, groups=link_channel.value)

                    msg_id = int(re.search(r'/(\d+)$', link_post.value).group(1))  # Получаем id сообщения из ссылки
                    await self.viewing_posts(client, link_post.value, msg_id, link_channel.value, session_name)
                    await asyncio.sleep(1)
                    await client.disconnect()
                    # Изменение маршрута на новый (если необходимо)
                    self.page.go("/viewing_posts_menu")
                    self.page.update()  # Обновление страницы для отображения изменений

            await self.function_button.function_button_ready_viewing(btn_click=btn_click, link_channel=link_channel,
                                                                     link_post=link_post)
        except Exception as error:
            logger.exception(error)

    async def viewing_posts(self, client, link_post, number, link_channel, session_name) -> None:
        """
        Накрутка просмотров постов

        :param client: Клиент для работы с Telegram
        :param link_post: Ссылка на пост
        :param number: Количество просмотров
        :param link_channel: Ссылка на канал
        :param session_name: Имя сессии (аккаунта Telegram)
        """
        try:
            try:
                await self.subscribe.subscribe_to_group_or_channel(client=client, groups=link_channel)
                channel = await client.get_entity(link_channel)  # Получение информации о канале
                await asyncio.sleep(5)
                await self.app_logger.log_and_display(f"Ссылка на пост: {link_post}\n")
                await asyncio.sleep(5)
                await client(GetMessagesViewsRequest(peer=channel, id=[int(number)], increment=True))
            except KeyError:
                sys.exit(1)
            except SessionRevokedError:
                logger.error(f"Не валидная сессия: {session_name}")
        except Exception as error:
            logger.exception(error)
