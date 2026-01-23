# -*- coding: utf-8 -*-
import asyncio
import random
import re

import flet as ft
from loguru import logger
from telethon import events, types, TelegramClient
from telethon.errors import ReactionInvalidError, TypeNotFoundError
from telethon.tl.functions.messages import SendReactionRequest

from src.core.configs import WIDTH_WIDE_BUTTON, BUTTON_HEIGHT
from src.core.database.account import getting_account
from src.core.utils import Utils
from src.features.account.connect import TGConnect
from src.features.account.subscribe import Subscribe
from src.features.account.subscribe_unsubscribe import SubscribeUnsubscribeTelegram
from src.gui.buttons import FunctionButton
from src.gui.gui import AppLogger, list_view
from src.gui.gui_elements import GUIProgram
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
        self.session_string = getting_account()
        self.subscribe = Subscribe(page=page)
        self.gui_program = GUIProgram(page=page)

    async def reactions_menu(self):
        """
        Отображает меню работы с реакциями в Telegram.

        :return: None
        """
        try:
            list_view.controls.clear()  # Очищаем список контролов

            # 2 поля ввода для ссылки на группу и на сообщение, пост.
            chat = ft.TextField(
                label="Введите ссылку на группу / чат:",
                multiline=False,
                max_lines=1,
                width=WIDTH_WIDE_BUTTON,
            )
            message = ft.TextField(
                label="Введите ссылку на сообщение или пост:",
                multiline=False,
                max_lines=1,
                width=WIDTH_WIDE_BUTTON,
            )

            async def send_reaction_request(_) -> None:
                start = await self.app_logger.start_time()
                logger.info("▶️ Начало Проставления реакций")

                try:
                    for session_name in self.session_string:
                        client: TelegramClient = await self.connect.client_connect_string_session(
                            session_name=session_name)

                        if client is None:
                            await self.app_logger.log_and_display("⚠️ Клиент не подключен. Проверьте сессию аккаунта.")
                            await self.app_logger.log_and_display(
                                "Рекомендации:\n"
                                "1. Проверьте аккаунты через меню 'Проверка аккаунтов'.\n"
                                "2. Обновите Telethon до последней версии.\n"
                                "3. Пересоздайте сессии через 'Подключение по номеру'."
                            )
                            continue

                        await self.app_logger.log_and_display(f"➕ Работаем с группой: {chat.value}")
                        await self.subscribe.subscribe_to_group_or_channel(client=client, groups=chat.value)

                        try:
                            msg_id = int(re.search(r'/(\d+)$', message.value).group(1))
                            await asyncio.sleep(5)

                            await client(SendReactionRequest(
                                peer=chat.value,
                                msg_id=msg_id,
                                reaction=[types.ReactionEmoji(emoticon=f'{await self.choosing_random_reaction()}')]
                            ))
                            await asyncio.sleep(1)
                        except AttributeError:
                            await self.app_logger.log_and_display("⚠️ Неверный формат ссылки на сообщение.")
                        except ReactionInvalidError:
                            await self.app_logger.log_and_display("❌ Ошибка: предоставлена неверная реакция")
                        finally:
                            await client.disconnect()

                except Exception as error:
                    logger.exception(error)
                finally:
                    logger.info("🔚 Конец Проставления реакций")
                    await self.app_logger.end_time(start)

            async def setting_reactions(_) -> None:
                start = await self.app_logger.start_time()
                try:
                    for session_name in self.session_string:
                        client: TelegramClient = await self.connect.client_connect_string_session(
                            session_name=session_name)

                        if client is None:
                            await self.app_logger.log_and_display("⚠️ Клиент не подключен.")
                            continue

                        chat_link = chat.value
                        if not chat_link:
                            await self.app_logger.log_and_display("❌ Ошибка: не указана ссылка на чат")
                            continue

                        await self.app_logger.log_and_display(f"🎧 Подписка и прослушивание чата: {chat_link}")
                        await self.subscribe.subscribe_to_group_or_channel(client=client, groups=chat_link)

                        @client.on(events.NewMessage(chats=chat_link))
                        async def handler(event):
                            msg = event.message
                            msg_id = msg.id
                            await self.app_logger.log_and_display(f"📩 Новое сообщение: {msg_id}")

                            if msg.post and not msg.out:
                                for session_name_reactions in self.session_string:
                                    if session_name == session_name_reactions:
                                        continue

                                    sub_client = await self.connect.client_connect_string_session(
                                        session_name=session_name_reactions)
                                    if sub_client is None:
                                        continue

                                    try:
                                        await sub_client(SendReactionRequest(
                                            peer=chat_link,
                                            msg_id=msg_id,
                                            reaction=[types.ReactionEmoji(
                                                emoticon=f'{await self.choosing_random_reaction()}')]
                                        ))
                                    except ReactionInvalidError:
                                        await self.app_logger.log_and_display(
                                            translations["ru"]["errors"]["invalid_reaction"])
                                    finally:
                                        await sub_client.disconnect()

                        try:
                            await client.run_until_disconnected()
                        except TypeNotFoundError:
                            await self.app_logger.log_and_display(
                                "⚠️ Ошибка: Неизвестный тип сообщения. Попробуйте обновить Telethon.")
                except Exception as error:
                    logger.exception(error)
                finally:
                    await self.app_logger.end_time(start)
                    await self.gui_program.show_notification(  # ✅ Показываем уведомление пользователю
                        message="🔚 Конец Автоматического выставления реакций"
                    )

            self.page.views.append(
                # Теперь создаём View ПОСЛЕ объявления chat и message
                ft.View(
                    route="/working_with_reactions",
                    appbar=await self.gui_program.key_app_bar(),  # Кнопка назад
                    controls=[
                        ft.Text(
                            spans=[
                                ft.TextSpan(
                                    translations["ru"]["menu"]["reactions"],
                                    ft.TextStyle(
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        foreground=ft.Paint(
                                            gradient=ft.PaintLinearGradient(
                                                (0, 20), (150, 20), [ft.Colors.PINK, ft.Colors.PURPLE]
                                            )
                                        ),
                                    ),
                                ),
                            ],
                        ),
                        list_view,
                        chat,
                        message,
                        ft.Column([
                            ft.ElevatedButton(
                                content=ft.Text(translations["ru"]["reactions_menu"]["setting_reactions"]),
                                width=WIDTH_WIDE_BUTTON,
                                height=BUTTON_HEIGHT,
                                on_click=send_reaction_request,
                            ),
                            ft.ElevatedButton(
                                content=ft.Text(translations["ru"]["reactions_menu"]["automatic_setting_of_reactions"]),
                                width=WIDTH_WIDE_BUTTON,
                                height=BUTTON_HEIGHT,
                                on_click=setting_reactions,
                            ),
                        ]),
                    ],
                )

            )
            self.page.update()

        except Exception as e:
            logger.exception(e)

    async def choosing_random_reaction(self):
        """
        Выбирает случайную реакцию из JSON-файла.

        :return: Случайная реакция (эмодзи) или None при ошибке
        """
        try:
            reactions = await self.utils.read_json_file('user_data/reactions/reactions.json')
            if not reactions:
                await self.app_logger.log_and_display("⚠️ Список реакций пуст.")
                return None
            random_value = random.choice(reactions)
            await self.app_logger.log_and_display(f"✅ Выбрана реакция: {random_value}")
            return random_value
        except Exception as error:
            logger.exception(error)
            return None
