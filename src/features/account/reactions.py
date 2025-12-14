# -*- coding: utf-8 -*-
import asyncio
import random
import re

import flet as ft  # Импортируем библиотеку flet
from loguru import logger  # Импортируем библиотеку loguru для логирования
from telethon import events, types, TelegramClient
from telethon.errors import ReactionInvalidError, TypeNotFoundError
from telethon.tl.functions.messages import SendReactionRequest

from src.core.config.configs import WIDTH_WIDE_BUTTON, BUTTON_HEIGHT
from src.core.database.account import getting_account
from src.core.utils import Utils
from src.features.account.connect import TGConnect
from src.features.account.subscribe import Subscribe
from src.features.account.subscribe_unsubscribe import SubscribeUnsubscribeTelegram
from src.gui.buttons import FunctionButton
from src.gui.gui import AppLogger, list_view
from src.gui.gui_elements import GUIProgram
from src.gui.notification import show_notification
from src.locales.translations_loader import translations


class WorkingWithReactions:
    """
    Класс для работы с реакциями
    """

    def __init__(self, page: ft.Page):
        """
        Инициализация класса для работы с реакциями в Telegram.

        :param page: Страница интерфейса Flet для отображения элементов управления
        """
        self.page = page
        self.connect = TGConnect(page=page)
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram(page=page)
        self.app_logger = AppLogger(page=page)
        self.utils = Utils(page=page)
        self.function_button = FunctionButton(page=page)
        self.session_string = getting_account()  # Получаем строку сессии из файла базы данных
        self.subscribe = Subscribe(page=page)  # Инициализация экземпляра класса Subscribe (Подписка)
        self.gui_program = GUIProgram()  # Инициализация экземпляра класса GUIProgram
        self.app_logger = AppLogger(page=page)

    async def reactions_menu(self):
        """
        Отображает меню работы с реакциями в Telegram.

        :param page: Страница интерфейса Flet для отображения элементов управления
        :return: None
        """

        list_view.controls.clear()  # ✅ Очистка логов перед новым запуском
        self.page.controls.append(list_view)  # Добавляем ListView на страницу для отображения логов 📝
        self.page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        # Отображение информации о настройках инвайтинга
        await self.app_logger.log_and_display(
            message=(
                f"Всего подключенных аккаунтов: {len(self.session_string)}\n"
            )
        )

        # Поле для ввода ссылки на чат
        chat = ft.TextField(label="Введите ссылку на группу / чат:", multiline=False, max_lines=1)
        message = ft.TextField(label="Введите ссылку на сообщение или пост:", multiline=False, max_lines=1)

        async def send_reaction_request(_) -> None:
            """
            Ставим реакции на сообщения
            """
            start = await self.app_logger.start_time()
            logger.info("▶️ Начало Проставления реакций")

            try:
                for session_name in self.session_string:
                    client: TelegramClient = await self.connect.client_connect_string_session(session_name=session_name)

                    await self.app_logger.log_and_display(f"➕ Работаем с группой: {chat.value}")
                    await self.subscribe.subscribe_to_group_or_channel(client=client, groups=chat.value)
                    msg_id = int(re.search(r'/(\d+)$', message.value).group(1))  # Получаем id сообщения из ссылки
                    await asyncio.sleep(5)
                    try:
                        """
                        Функция client_connect_string_session возвращает None, если сессия недействительна или аккаунт 
                        не авторизован, но в reactions.py нет проверки на этот случай. В результате client = None, и 
                        при попытке вызвать client(...) возникает ошибка.
                        
                        ⚠️ Клиент не подключен. Проверьте сессию аккаунта.
                        Рекомендации

                        1. Проверяйте все аккаунты через меню "Проверка аккаунтов" — возможно, файлы сессий повреждены.
                        2. Обновите Telethon до последней версии, чтобы избежать TypeNotFoundError.
                        3. Если ошибка повторяется — пересоздайте сессии через "Подключение по номеру".
                        """
                        if client is None:
                            await self.app_logger.log_and_display("⚠️ Клиент не подключен. Проверьте сессию аккаунта.")
                            await self.app_logger.log_and_display("Рекомендации:\n1. Проверьте аккаунты через меню 'Проверка аккаунтов'.\n2. Обновите Telethon до последней версии.\n3. Пересоздайте сессии через 'Подключение по номеру'.")
                            continue

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

            except Exception as error:
                logger.exception(error)

            logger.info("🔚 Конец Проставления реакций")
            await self.app_logger.end_time(start)

        async def setting_reactions(_) -> None:
            """
            Выставление реакций на новые посты и сообщения в автоматическом режиме
            """
            start = await self.app_logger.start_time()
            try:
                for session_name in self.session_string:

                    client: TelegramClient = await self.connect.client_connect_string_session(session_name=session_name)
                    # await self.connect.getting_account_data(client)

                    # Сохраняем ссылку на чат заранее
                    chat_link = chat.value
                    if not chat_link:
                        await self.app_logger.log_and_display("Ошибка: не указана ссылка на чат")
                        continue

                    await self.app_logger.log_and_display(f"Подписка и прослушивание чата: {chat_link}")
                    await self.subscribe.subscribe_to_group_or_channel(client=client, groups=chat_link)

                    @client.on(events.NewMessage(chats=chat_link))
                    async def handler(event):
                        message = event.message  # Получаем сообщение из события
                        message_id = message.id  # Получаем id сообщение
                        await self.app_logger.log_and_display(f"Идентификатор сообщения: {message_id}, {message}")
                        # Проверяем, является ли сообщение постом и не является ли оно нашим
                        if message.post and not message.out:

                            for session_name_reactions in self.session_string:

                                if session_name == session_name_reactions:
                                    pass
                                else:

                                    client: TelegramClient = await self.connect.client_connect_string_session(
                                        session_name=session_name_reactions)

                                    await self.subscribe.subscribe_to_group_or_channel(client=client, groups=chat_link)

                                    try:
                                        await client(SendReactionRequest(peer=chat_link, msg_id=int(message_id),
                                                                         reaction=[types.ReactionEmoji(
                                                                             emoticon=f'{await self.choosing_random_reaction()}')]))
                                    except ReactionInvalidError:
                                        await self.app_logger.log_and_display(
                                            translations["ru"]["errors"]["invalid_reaction"])

                    try:
                        await client.run_until_disconnected()  # Запуск клиента в режиме ожидания событий
                    except TypeNotFoundError:
                        """
                        Ошибка TypeNotFoundError: Could not find a matching Constructor ID for the TLObject that was 
                        supposed to be read with ID b92f76cf возникает из-за несоответствия между версией библиотеки 
                        Telethon и текущей схемой Telegram API. Код конструктора b92f76cf не распознаётся, что указывает
                         на то, что Telethon не знает, как десериализовать полученный объект.
                        
                        Причина
                        Эта ошибка обычно появляется, когда:
                        
                        Используется устаревшая версия Telethon, которая не поддерживает новые типы объектов Telegram.
                        Telegram обновил свою схему TL (Telegram Layer), добавив новые типы, которые не отражены в 
                        текущей версии Telethon.
                        """
                        await self.app_logger.log_and_display(message=f"Ошибка: Не найден тип сообщения, попробуйте обновить Telethon")


            except Exception as error:
                logger.exception(error)
            await self.app_logger.end_time(start=start)
            await show_notification(page=self.page,
                                    message="🔚 Конец Автоматического выставления реакций")  # Выводим уведомление пользователю

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
                     list_view,  # Отображение логов 📝

                     chat,  # Поле ввода ссылки на чат
                     message,  # Поле ввода ссылки пост

                     ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                         # 👍 Ставим реакции
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["reactions_menu"]["setting_reactions"],
                                           on_click=send_reaction_request),
                         # 🤖 Автоматическое выставление реакций
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["reactions_menu"]["automatic_setting_of_reactions"],
                                           on_click=setting_reactions),
                     ])]))

    async def choosing_random_reaction(self):
        """Выбираем случайное значение из списка (реакция)"""
        try:
            random_value = random.choice(await self.utils.read_json_file(filename='user_data/reactions/reactions.json'))
            await self.app_logger.log_and_display(f"{random_value}")
            return random_value
        except Exception as error:
            logger.exception(error)
            return None

# 204
