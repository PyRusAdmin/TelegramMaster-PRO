# -*- coding: utf-8 -*-
import asyncio
import random
import re

import flet as ft  # Импортируем библиотеку flet
from loguru import logger  # Импортируем библиотеку loguru для логирования
from telethon import events, types, TelegramClient
from telethon.errors import ReactionInvalidError
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import SendReactionRequest

from src.core.database.account import getting_account
from src.core.utils import Utils
from src.features.account.connect import TGConnect
from src.features.account.subscribe import Subscribe
from src.features.account.subscribe_unsubscribe import SubscribeUnsubscribeTelegram
from src.gui.buttons import FunctionButton
from src.gui.gui import AppLogger
from src.locales.translations_loader import translations


class WorkingWithReactions:
    """
    Класс для работы с реакциями
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.connect = TGConnect(page=page)
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram(page=page)
        self.app_logger = AppLogger(page=page)
        self.utils = Utils(page=page)
        self.function_button = FunctionButton(page=page)
        self.session_string = getting_account()  # Получаем строку сессии из файла базы данных
        self.subscribe = Subscribe(page=page)  # Инициализация экземпляра класса Subscribe (Подписка)

    async def send_reaction_request(self) -> None:
        """
        Ставим реакции на сообщения
        """
        try:
            # Поле для ввода ссылки на чат
            chat = ft.TextField(label="Введите ссылку на группу / чат:", multiline=False, max_lines=1)
            message = ft.TextField(label="Введите ссылку на сообщение или пост:", multiline=False, max_lines=1)

            async def btn_click(_) -> None:

                for session_name in self.session_string:
                    client: TelegramClient = await self.connect.client_connect_string_session(session_name=session_name)
                    await self.connect.getting_account_data(client)

                    await self.app_logger.log_and_display(f"➕ Работаем с группой: {chat.value}")
                    await self.subscribe.subscribe_to_group_or_channel(client=client, groups=chat.value)
                    msg_id = int(re.search(r'/(\d+)$', message.value).group(1))  # Получаем id сообщения из ссылки
                    await asyncio.sleep(5)
                    try:
                        await client(SendReactionRequest(
                            peer=chat.value, msg_id=msg_id,
                            reaction=[types.ReactionEmoji(emoticon=f'{await self.choosing_random_reaction()}')]))
                        await asyncio.sleep(1)
                        await client.disconnect()
                    except ReactionInvalidError:
                        await self.app_logger.log_and_display(f"Ошибка : Предоставлена неверная реакция")
                        await asyncio.sleep(1)
                        await client.disconnect()

                    # Изменение маршрута на новый (если необходимо)
                    self.page.go("/working_with_reactions")
                    self.page.update()  # Обновление страницы для отображения изменений

            def back_button_clicked(_) -> None:
                """Кнопка возврата в меню проставления реакций"""
                self.page.go("/working_with_reactions")

            self.function_button.function_button_ready_reactions(btn_click=btn_click,
                                                                 back_button_clicked=back_button_clicked, chat=chat,
                                                                 message=message)

        except Exception as error:
            logger.exception(error)

    async def choosing_random_reaction(self):
        """Выбираем случайное значение из списка (реакция)"""
        try:
            random_value = random.choice(self.utils.read_json_file(filename='user_data/reactions/reactions.json'))
            await self.app_logger.log_and_display(f"{random_value}")
            return random_value
        except Exception as error:
            logger.exception(error)
            return None

    async def reactions_for_groups_and_messages_test(self, number, chat) -> None:
        """
        Вводим ссылку на группу и ссылку на сообщение

        :param number: Ссылка на сообщение
        :param chat: Ссылка на группу
        """
        try:
            for session_name in self.utils.find_filess(directory_path="user_data/accounts/reactions_list",
                                                       # TODO переместить путь к файлу в конфиг файл
                                                       extension='session'):
                # "user_data/accounts/reactions_list" - путь к файлу, но пусть пользователь сам выбирает аккаунт
                # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
                client: TelegramClient = await self.connect.client_connect_string_session(session_name=session_name)
                await self.connect.getting_account_data(client)

                await client(JoinChannelRequest(chat))  # Подписываемся на канал / группу
                await asyncio.sleep(5)
                # random_value = await self.choosing_random_reaction()  # Выбираем случайное значение из списка (редакция)
                try:
                    await client(SendReactionRequest(peer=chat, msg_id=int(number),
                                                     reaction=[types.ReactionEmoji(
                                                         emoticon=f'{self.choosing_random_reaction()}')]))
                    await asyncio.sleep(1)
                    await client.disconnect()
                except ReactionInvalidError:
                    await self.app_logger.log_and_display(translations["ru"]["errors"]["invalid_reaction"])
                    await asyncio.sleep(1)
                    await client.disconnect()
        except Exception as error:
            logger.exception(error)

    async def setting_reactions(self) -> None:
        """
        Выставление реакций на новые посты
        """
        try:
            for session_name in self.session_string:

                client: TelegramClient = await self.connect.client_connect_string_session(session_name=session_name)
                await self.connect.getting_account_data(client)

                chat = self.utils.read_json_file(filename='user_data/reactions/link_channel.json')
                await self.app_logger.log_and_display(f"{chat}")
                await client(JoinChannelRequest(chat))  # Подписываемся на канал / группу

                @client.on(events.NewMessage(chats=chat))
                async def handler(event):
                    message = event.message  # Получаем сообщение из события
                    message_id = message.id  # Получаем id сообщение
                    await self.app_logger.log_and_display(f"Идентификатор сообщения: {message_id}, {message}")
                    # Проверяем, является ли сообщение постом и не является ли оно нашим
                    if message.post and not message.out:
                        await self.reactions_for_groups_and_messages_test(message_id, chat)

                await client.run_until_disconnected()  # Запуск клиента в режиме ожидания событий
        except Exception as error:
            logger.exception(error)
