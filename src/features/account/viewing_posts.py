import asyncio  # Импортируем библиотеку для работы с асинхронным кодом
import re  # Импортируем библиотеку для работы с регулярными выражениями
import sys  # Импортируем библиотеку для работы с системным вызовом

import flet as ft  # Импортируем библиотеку flet
from loguru import logger  # Импортируем библиотеку loguru для логирования
from telethon.errors import SessionRevokedError
from telethon.tl.functions.messages import GetMessagesViewsRequest

from src.core.database.account import getting_account
from src.core.utils import Utils
from src.features.account.connect import TGConnect
from src.features.account.subscribe import Subscribe
from src.features.account.subscribe_unsubscribe import SubscribeUnsubscribeTelegram
from src.gui.buttons import FunctionButton
from src.gui.gui import AppLogger, list_view


class ViewingPosts:
    """
    Функционал для накрутки просмотров постов каналов в Telegram.
    """

    def __init__(self, page: ft.Page):
        """
        Инициализация класса для просмотра постов в Telegram.

        :param page: Страница интерфейса Flet для отображения элементов управления
        """
        self.page = page
        self.connect = TGConnect(page=page)
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram(page=page)
        self.app_logger = AppLogger(page=page)
        self.utils = Utils(page=page)
        self.function_button = FunctionButton(page=page)
        self.subscribe = Subscribe(page=page)  # Инициализация экземпляра класса Subscribe (Подписка)
        self.session_string = getting_account()  # Получаем строку сессии из файла базы данных
        # Поле для ввода ссылки на чат
        self.link_channel = ft.TextField(
            label=f"Введите ссылку на канал:",
            expand=True,  # Полноразмерное расширение
            multiline=False,  # Отключение возможности многострочного ввода
            max_lines=1  # Ограничение на количество строк в поле
        )
        self.link_post = ft.TextField(
            label=f"Введите ссылку на пост:",
            expand=True,  # Полноразмерное расширение
            multiline=False,  # Отключение возможности многострочного ввода
            max_lines=1  # Ограничение на количество строк в поле
        )
        self.number_views = ft.TextField(
            label=f"Введите количество просмотров от 1 до {len(self.session_string)}:",
            expand=True,  # Полноразмерное расширение
            multiline=False,
            max_lines=1
        )

    async def viewing_posts_request(self) -> None:
        """
        Отображает интерфейс для накрутки просмотров постов в Telegram.

        :return: None
        """
        try:
            list_view.controls.clear()  # Очистка list_view для отображения новых элементов и недопущения дублирования

            await self.app_logger.log_and_display(
                message=(
                    f"Всего подключенных аккаунтов: {len(self.session_string)}\n"
                )
            )

            async def btn_click(_) -> None:

                number_session = self.number_views.value
                list_view.controls.append(ft.Text(f"Выбрано просмотров: {number_session}"))
                views_selected = self.session_string[:int(number_session)]

                start = await self.app_logger.start_time()  # Запуск таймера
                self.page.update()  # Обновление страницы, чтобы сразу показать сообщение 🔄

                for session_name in views_selected:
                    client = await self.connect.client_connect_string_session(session_name=session_name)

                    list_view.controls.append(ft.Text(f"➕ Работаем с каналом: {self.link_channel.value}"))

                    await self.subscribe.subscribe_to_group_or_channel(client=client, groups=self.link_channel.value)

                    msg_id = int(
                        re.search(r'/(\d+)$', self.link_post.value).group(1))  # Получаем id сообщения из ссылки
                    await self.viewing_posts(
                        client=client,
                        link_post=self.link_post.value,
                        number=msg_id,
                        link_channel=self.link_channel.value,
                        session_name=session_name
                    )
                    await asyncio.sleep(1)
                    await client.disconnect()
                    # Изменение маршрута на новый (если необходимо)
                    self.page.go("/viewing_posts_menu")
                    self.page.update()  # Обновление страницы для отображения изменений

                await self.app_logger.end_time(start)  # Завершение таймера

            await self.function_button.function_button_ready_viewing(
                number_views=self.number_views,
                btn_click=btn_click,
                link_channel=self.link_channel,
                link_post=self.link_post
            )
        except Exception as error:
            logger.exception(error)

    async def viewing_posts(self, client, link_post, number, link_channel, session_name) -> None:
        """
        Выполняет накрутку просмотров для указанного поста.

        :param client: Экземпляр клиента Telegram
        :param link_post: Ссылка на пост
        :param number: Идентификатор сообщения
        :param link_channel: Ссылка на канал
        :param session_name: Имя сессии (аккаунта Telegram)
        :return: None
        """
        try:
            try:
                await self.subscribe.subscribe_to_group_or_channel(client=client, groups=link_channel)
                channel = await client.get_entity(link_channel)  # Получение информации о канале
                await asyncio.sleep(5)
                await self.app_logger.log_and_display(message=f"Ссылка на пост: {link_post}\n")
                await asyncio.sleep(5)
                await client(GetMessagesViewsRequest(peer=channel, id=[int(number)], increment=True))
            except KeyError:
                sys.exit(1)
            except SessionRevokedError:
                logger.error(f"Не валидная сессия: {session_name}")
        except Exception as error:
            logger.exception(error)
