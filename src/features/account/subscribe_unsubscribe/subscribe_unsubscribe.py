# -*- coding: utf-8 -*-
import asyncio
import sqlite3

import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from telethon import functions, types
from telethon.errors import (AuthKeyUnregisteredError, ChannelPrivateError, ChannelsTooMuchError, FloodWaitError,
                             InviteHashExpiredError, InviteHashInvalidError, InviteRequestSentError,
                             SessionPasswordNeededError, SessionRevokedError, UserNotParticipantError)
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

from src.core.configs import (BUTTON_HEIGHT, WIDTH_WIDE_BUTTON, path_accounts_folder, time_subscription_1,
                              time_subscription_2)
from src.core.sqlite_working_tools import get_writing_group_links, write_writing_group_links_to_db
from src.core.utils import find_filess
from src.features.account.TGConnect import TGConnect
from src.features.account.parsing.gui_elements import GUIProgram
from src.features.account.subscribe_unsubscribe.gui_input_builders import LinkInputRowBuilder, TimeInputRowBuilder
from src.features.settings.setting import recording_limits_file, writing_settings_to_a_file
from src.gui.gui import AppLogger, list_view
from src.gui.notification import show_notification
from src.locales.translations_loader import translations


class SubscribeUnsubscribeTelegram:

    def __init__(self, page):
        self.page = page  # Страница интерфейса Flet для отображения элементов управления.
        self.tg_connect = TGConnect(page=page)
        self.app_logger = AppLogger(page=page)

    async def subscribe_and_unsubscribe_menu(self):
        """
        Меню подписка и отписка
        """
        self.page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        self.page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        async def unsubscribe_all(_) -> None:
            """
            Отписываемся от групп, каналов, личных сообщений
            """
            start = await self.app_logger.start_time()
            try:
                for session_name in find_filess(directory_path=path_accounts_folder, extension='session'):
                    client = await self.tg_connect.get_telegram_client(session_name,
                                                                       account_directory=path_accounts_folder)
                    dialogs = client.iter_dialogs()
                    await self.app_logger.log_and_display(f"Диалоги: {dialogs}")
                    async for dialog in dialogs:
                        await self.app_logger.log_and_display(f"{dialog.name}, {dialog.id}")
                        await client.delete_dialog(dialog)
                    await client.disconnect()
            except Exception as error:
                logger.exception(error)
            await self.app_logger.end_time(start)

        async def add_items(_):
            """Подписываемся на группы и каналы"""
            start = await self.app_logger.start_time()
            for session_name in find_filess(directory_path=path_accounts_folder, extension='session'):
                session_string = await self.tg_connect.get_string_session(session_name)
                # Создаем клиент, используя StringSession и вашу строку
                client = TelegramClient(
                    StringSession(session_string),  # <-- Используем StringSession
                    api_id=7655060,
                    api_hash="cc1290cd733c1f1d407598e5a31be4a8",
                    system_version="4.16.30-vxCUSTOM",
                )
                await client.connect()
                await self.tg_connect.getting_account_data(client)

                if client is None:
                    logger.error("❌ Не удалось подключиться к Telegram")
                # Получение ссылки
                links_inviting: list = get_writing_group_links()  # Открываем базу данных
                await self.app_logger.log_and_display(f"Ссылка для подписки и проверки:  {links_inviting}")
                for link_tuple in links_inviting:
                    await self.app_logger.log_and_display(f"Ссылка для подписки и проверки:  {link_tuple}")
                    # Проверка ссылок для подписки и подписка на группу или канал
                    logger.info(f"Работа с аккаунтом {session_name}")
                    await self.checking_links(client, link_tuple)
                try:
                    await client.disconnect()
                except sqlite3.DatabaseError:
                    logger.error("❌ Не удалось подписаться на канал / группу, так как файл аккаунта повреждён")
            await self.app_logger.end_time(start)

        async def save(_):
            """Сохраняет ссылки в базу данных в таблицу writing_group_links, для последующей подписки"""
            logger.info(f"Сохранение ссылок для подписки")
            writing_group_links = link_entry_field.value.strip().split()
            data_to_save = {
                "writing_group_links": writing_group_links,
            }
            write_writing_group_links_to_db(data_to_save)
            logger.info(f"Сохранение ссылок для подписки завершено")

        async def btn_click(_) -> None:
            """Обработчик клика по кнопке"""
            try:
                smaller_times = int(smaller_timex.value)
                larger_times = int(larger_timex.value)
                if smaller_times < larger_times:  # Проверяем, что первое время меньше второго
                    # Если условие прошло проверку, то возвращаем первое и второе время
                    writing_settings_to_a_file(
                        await recording_limits_file(str(smaller_times), str(larger_times), variable="time_subscription",
                                                    page=self.page))
                    list_view.controls.append(ft.Text("Данные успешно записаны!"))  # отображаем сообщение в ListView
                    await show_notification(self.page, "Данные успешно записаны!")
                    # page.go("/settings")  # Изменение маршрута в представлении существующих настроек
                else:
                    list_view.controls.append(ft.Text("Ошибка: первое время должно быть меньше второго!"))
            except ValueError:
                list_view.controls.append(ft.Text("Ошибка: введите числовые значения!"))
            self.page.update()  # обновляем страницу

        time_range = [time_subscription_1, time_subscription_2]
        self.page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        for time_range_message in time_range: list_view.controls.append(
            ft.Text(f"Записанные данные в файле {time_range_message}"))  # отображаем сообщение в ListView

        # Поле ввода ссылок и кнопка сохранения для подписки
        link_entry_field, save_button = await LinkInputRowBuilder().build_link_input_with_save_button(save,
                                                                                                      "Введите ссылки для подписки на группы и каналы",
                                                                                                      width=500)
        # Два поля ввода для времени и кнопка сохранить
        smaller_timex, larger_timex, save_button_time = await TimeInputRowBuilder().build_time_inputs_with_save_button(
            btn_click,
            label_min="Время в секундах (меньшее)",
            label_max="Время в секундах (большее)",
            width=344
        )

        self.page.views.append(
            ft.View("/subscribe_unsubscribe",
                    [await GUIProgram().key_app_bar(),
                     ft.Text(spans=[ft.TextSpan(
                         translations["ru"]["menu"]["subscribe_unsubscribe"],
                         ft.TextStyle(
                             size=20, weight=ft.FontWeight.BOLD,
                             foreground=ft.Paint(
                                 gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                      ft.Colors.PURPLE])), ), ), ], ),

                     list_view,  # Отображение логов 📝

                     await GUIProgram().diver_castom(),  # Горизонтальная линия
                     ft.Text(
                         value="⏱ Укажите интервал времени (в секундах) между подписками на группы.\n"
                               "🤖 После каждой подписки аккаунт сделает паузу на случайное время из указанного диапазона,\n"
                               "🔁 затем продолжит подписку на следующую группу.",
                         size=14
                     ),
                     await TimeInputRowBuilder().compose_time_input_row(smaller_timex, larger_timex,
                                                                        save_button_time),
                     await GUIProgram().diver_castom(),  # Горизонтальная линия
                     ft.Text(
                         value="🔗 Укажите ссылки на группы или каналы для подписки.\n"
                               "📌 Если вы уже вводили их ранее — ввод не обязателен, данные сохранены в системе.",
                         size=14
                     ),
                     await LinkInputRowBuilder().compose_link_input_row(link_entry_field, save_button),
                     await GUIProgram().diver_castom(),  # Горизонтальная линия
                     ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                         # 🔔 Подписка
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["subscribe_unsubscribe_menu"]["subscription"],
                                           on_click=add_items),
                         # 🚫 Отписываемся
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["subscribe_unsubscribe_menu"]["unsubscribe"],
                                           on_click=unsubscribe_all),
                     ])]))

    @staticmethod
    async def extract_channel_id(link):
        """Сокращает ссылку с https://t.me/+yjqd0uZQETc4NGEy до yjqd0uZQETc4NGEy"""
        # Проверяем, начинается ли ссылка с 'https://t.me/'
        if link.startswith('https://t.me/'):
            return link[len('https://t.me/'):]
        # Если ссылка начинается просто с 't.me/', удалим 't.me/'
        elif link.startswith('t.me/'):
            return link[len('t.me/'):]
        # В остальных случаях возвращаем None
        else:
            return None

    async def checking_links(self, client, link) -> None:
        """
        Проверка ссылок на подписку

        :param client: Клиент Telegram
        :param link: Ссылка на подписку
        """
        try:
            if link.startswith("https://t.me/+"):
                # Извлекаем хэш из ссылки на приглашение
                link_hash = link.split("+")[-1]
                try:
                    result = await client(functions.messages.CheckChatInviteRequest(hash=link_hash))
                    if isinstance(result, types.ChatInvite):
                        await self.app_logger.log_and_display(
                            f"Ссылка валидна: {link}, Название группы: {result.title}, "
                            f"Количество участников: {result.participants_count}, "
                            f"Мега-группа: {'Да' if result.megagroup else 'Нет'}, Описание: {result.about or 'Нет описания'}")
                        try:
                            await self.app_logger.log_and_display(
                                f"Подписка на группу / канал по ссылке приглашению {link}")
                            try:
                                await client(ImportChatInviteRequest(
                                    link_hash))  # Подписка на группу / канал по ссылке приглашению
                            except InviteHashInvalidError:
                                await self.app_logger.log_and_display(
                                    translations["ru"]["errors"]["invite_request_sent"])
                        except InviteHashExpiredError:
                            await self.app_logger.log_and_display(translations["ru"]["errors"]["subscribe_error"])
                            try:
                                await client(ImportChatInviteRequest(
                                    link_hash))  # Подписка на группу / канал по ссылке приглашению
                                await self.app_logger.log_and_display(
                                    f"Подписка на группу / канал по ссылке приглашению {link_hash}")
                            except InviteHashInvalidError:
                                await self.app_logger.log_and_display(
                                    translations["ru"]["errors"]["invite_request_sent"])
                    elif isinstance(result, types.ChatInviteAlready):
                        await self.app_logger.log_and_display(
                            f"Вы уже состоите в группе: {link}, Название группы: {result.chat.title}")
                except FloodWaitError as e:
                    await self.app_logger.log_and_display(f"{translations["ru"]["errors"]["flood_wait"]}{e}",
                                                          level="error")

            elif link.startswith("https://t.me/"):
                # Извлекаем имя пользователя или группы
                username = link.split("/")[-1]

                result = await client(functions.contacts.ResolveUsernameRequest(username=username))
                chat = result.chats[0] if result.chats else None
                if chat:
                    await self.app_logger.log_and_display(f"Публичная группа/канал: {link}, Название: {chat.title}, "
                                                          f"Количество участников: {chat.participants_count if hasattr(chat, 'participants_count') else 'Неизвестно'}, "
                                                          f"Мега-группа: {'Да' if getattr(chat, 'megagroup', False) else 'Нет'}")
                    logger.info(f"Подписка на группу / канал по ссылке {link}")
                    try:
                        await client(JoinChannelRequest(link))
                    except ChannelsTooMuchError:
                        await self.app_logger.log_and_display(translations["ru"]["errors"]["user_channels_too_much"])
                else:
                    await self.app_logger.log_and_display(f"Не удалось найти публичный чат: {link}")

            else:
                # Считаем, что это просто хэш
                try:
                    result = await client(functions.messages.CheckChatInviteRequest(hash=link))
                    if isinstance(result, types.ChatInvite):
                        await self.app_logger.log_and_display(
                            f"Ссылка валидна: {link}, Название группы: {result.title}, "
                            f"Количество участников: {result.participants_count}, "
                            f"Мега-группа: {'Да' if result.megagroup else 'Нет'}, "
                            f"Описание: {result.about or 'Нет описания'}")
                        await client(JoinChannelRequest(link))
                    elif isinstance(result, types.ChatInviteAlready):
                        await self.app_logger.log_and_display(
                            f"Вы уже состоите в группе: {link}, Название группы: {result.chat.title}")
                except FloodWaitError as e:
                    await self.app_logger.log_and_display(f"{translations["ru"]["errors"]["flood_wait"]}{e}",
                                                          level="error")
                except InviteHashExpiredError:
                    await self.app_logger.log_and_display(f"Повторная проверка ссылки: {link}")
                    result = await client(functions.contacts.ResolveUsernameRequest(username=link))
                    chat = result.chats[0] if result.chats else None
                    if chat:
                        await self.app_logger.log_and_display(
                            f"Публичная группа/канал: {link}, Название: {chat.title}, "
                            f"Количество участников: {chat.participants_count if hasattr(chat, 'participants_count') else 'Неизвестно'}, "
                            f"Мега-группа: {'Да' if getattr(chat, 'megagroup', False) else 'Нет'}")
                    else:
                        await self.app_logger.log_and_display(f"Не удалось найти публичный чат: {link}")

                except AuthKeyUnregisteredError:
                    await self.app_logger.log_and_display(translations["ru"]["errors"]["auth_key_unregistered"])
                    await asyncio.sleep(2)
                except SessionPasswordNeededError:
                    await self.app_logger.log_and_display(translations["ru"]["errors"]["two_factor_required"])
                    await asyncio.sleep(2)

        except FloodWaitError as e:
            await self.app_logger.log_and_display(f"{translations["ru"]["errors"]["flood_wait"]}{e}", level="error")
        except InviteRequestSentError:
            await self.app_logger.log_and_display(translations["ru"]["errors"]["invite_request_sent"])
        except AuthKeyUnregisteredError:
            await self.app_logger.log_and_display(translations["ru"]["errors"]["auth_key_unregistered"])
            await asyncio.sleep(2)
        except SessionPasswordNeededError:
            await self.app_logger.log_and_display(translations["ru"]["errors"]["two_factor_required"])
            await asyncio.sleep(2)

    # async def subscribe_telegram(self, page: ft.Page) -> None:
    #     """
    #     Подписка на группы / каналы Telegram
    #
    #     :param page: Страница интерфейса Flet для отображения элементов управления.
    #     """
    #
    #     # TODO реализовать проверку ссылок перед подпиской, что бы пользователи не подсовывали программе не рабочие
    #     #  ссылки или ссылки которые не являются группой или каналом
    #
    #     async def back_button_clicked(_):
    #         """
    #         ⬅️ Обрабатывает нажатие кнопки "Назад", возвращая в меню подписки на группы / каналы Telegram.
    #         """
    #         page.go("/subscribe_unsubscribe")  # Переходим к основному меню подписки на группы / каналы Telegram. 🏠
    #
    #     # Добавляем кнопки и другие элементы управления на страницу
    #     page.views.append(
    #         ft.View(
    #             "/subscription_all",
    #             [
    #                 ft.Text(value="Подписка на группы / каналы Telegram"),  # Выбор группы для инвайтинга
    #                 list_view,  # Отображение логов 📝
    #                 ft.Column(),  # Резерв для приветствия или других элементов интерфейса
    #                 # ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT, text="🚀 Начать подписку",
    #                 #                   on_click=add_items),  # Кнопка "🚀 Начать подписку"
    #                 ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
    #                                   text=translations["ru"]["buttons"]["back"],
    #                                   on_click=back_button_clicked)  # Кнопка "⬅️ Назад"
    #             ],
    #         )
    #     )
    #
    #     page.update()  # обновляем страницу после добавления элементов управления 🔄

    async def unsubscribe_from_the_group(self, client, group_link) -> None:
        """
        Отписываемся от группы.

        :param group_link: Группа или канал
        :param client: Телеграм клиент
        """
        logger.info(f"Отписываемся от группы: {group_link}")
        try:
            entity = await client.get_entity(group_link)
            if entity:
                await client(LeaveChannelRequest(entity))
            # await client.disconnect()  # Разрываем соединение с Telegram
        except ChannelPrivateError:  # Аккаунт Telegram не может отписаться так как не имеет доступа
            await self.app_logger.log_and_display(translations["ru"]["errors"]["channel_private"])
        except UserNotParticipantError:
            await self.app_logger.log_and_display(translations["ru"]["errors"]["unsubscribe_not_member"])
        except SessionRevokedError:
            await self.app_logger.log_and_display(translations["ru"]["errors"]["invalid_auth_session_terminated"])
        except sqlite3.DatabaseError:
            await self.app_logger.log_and_display(
                f"❌ Попытка подписки на группу / канал {group_link}. Ошибка базы данных, аккаунта или аккаунт заблокирован.")
        except ConnectionError:
            await self.app_logger.log_and_display("Ошибка соединения с Telegram")
        # except Exception as error:
        #     logger.exception(error)

        # finally:
        #     await client.disconnect()  # Разрываем соединение с Telegram

# 409
