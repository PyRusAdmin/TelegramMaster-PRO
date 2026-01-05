# -*- coding: utf-8 -*-
import asyncio
import random
import sys
import time

import flet as ft
from loguru import logger
from telethon import events, TelegramClient
from telethon.errors import (ChannelPrivateError, ChatAdminRequiredError, ChatWriteForbiddenError, FloodWaitError,
                             PeerFloodError, SlowModeWaitError, UserBannedInChannelError, UserIdInvalidError,
                             UsernameInvalidError, UsernameNotOccupiedError, UserNotMutualContactError, ForbiddenError)

from src.core.config.configs import (BUTTON_HEIGHT, WIDTH_WIDE_BUTTON, path_folder_with_messages,
                                     TIME_SENDING_MESSAGES_1, TIME_SENDING_MESSAGES_2, time_subscription_1,
                                     time_subscription_2, width_one_input)
from src.core.database.account import getting_account, get_account_list
from src.core.database.database import select_records_with_limit, get_writing_group_links
from src.core.utils import Utils
from src.features.account.connect import TGConnect
from src.features.account.subscribe import Subscribe
from src.gui.gui import list_view, AppLogger
from src.gui.gui_elements import GUIProgram
from src.gui.notification import show_notification
from src.locales.translations_loader import translations


class SendTelegramMessages:
    """
    Отправка (текстовых) сообщений в личку Telegram пользователям из базы данных.
    """

    def __init__(self, page: ft.Page):
        """
        Инициализация класса для отправки сообщений в Telegram.

        :param page: Страница интерфейса Flet для отображения элементов управления
        """
        self.page = page
        self.connect = TGConnect(page=page)
        self.file_extension = "json"
        self.app_logger = AppLogger(page=page)
        self.utils = Utils(page=page)
        self.gui_program = GUIProgram()
        self.session_string = getting_account()  # Получаем строку сессии из файла базы данных
        self.subscribe = Subscribe(page=page)  # Инициализация экземпляра класса Subscribe (Подписка)
        self.account_data = get_account_list()  # Получаем список аккаунтов из базы данных
        self.tb_time_from = ft.TextField(label="Время сна от", width=width_one_input, hint_text="Введите время",
                                         border_radius=5)
        self.tb_time_to = ft.TextField(label="Время сна до", width=width_one_input, hint_text="Введите время",
                                       border_radius=5)

    async def send_files_to_personal_chats(self) -> None:
        """
        Отображает интерфейс для отправки файлов в личные сообщения пользователей Telegram.

        :param page: Страница интерфейса Flet для отображения элементов управления
        :return: None
        """
        limits = ft.TextField(label="Введите лимит на сообщения")

        # Группа полей ввода для времени сна

        async def button_clicked(_):
            """Обработчик кнопки "Готово" """

            if self.tb_time_from.value < self.tb_time_to.value:
                try:
                    start = await self.app_logger.start_time()
                    # Просим пользователя ввести расширение сообщения
                    for session_name in self.session_string:  # Перебор всех сессий
                        # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
                        client: TelegramClient = await self.connect.client_connect_string_session(
                            session_name=session_name)

                        try:
                            for username in await select_records_with_limit(limit=int(limits.value),
                                                                            app_logger=self.app_logger):
                                logger.info(f"Отправляем сообщение в личку {username}")
                                await self.app_logger.log_and_display(message=f"[!] Отправляем сообщение: {username}")
                                try:
                                    user_to_add = await client.get_input_entity(username)
                                    messages, files = await self.all_find_and_all_files()
                                    await self.send_content(client, user_to_add, messages, files)
                                    await self.app_logger.log_and_display(
                                        message=f"Отправляем сообщение в личку {username}. Файл {files} отправлен пользователю {username}.")
                                    await self.utils.record_inviting_results(time_range_1=int(self.tb_time_from.value),
                                                                             time_range_2=int(self.tb_time_to.value),
                                                                             username=username)
                                    await self.app_logger.log_and_display(message=f"Смена аккаунта, ожидайте 8 секунд")
                                    time.sleep(8)

                                except FloodWaitError as e:
                                    await self.app_logger.log_and_display(
                                        message=f"{translations["ru"]["errors"]["flood_wait"]}{e}",
                                        level="error")
                                    await self.utils.record_and_interrupt(time_range_1=self.tb_time_from.value,
                                                                          time_range_2=self.tb_time_to.value)
                                    break  # Прерываем работу и меняем аккаунт
                                except PeerFloodError:
                                    await self.utils.record_and_interrupt(time_range_1=self.tb_time_from.value,
                                                                          time_range_2=self.tb_time_to.value)
                                    break  # Прерываем работу и меняем аккаунт
                                except UserNotMutualContactError:
                                    await self.app_logger.log_and_display(
                                        message=translations["ru"]["errors"]["user_not_mutual_contact"])
                                except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                                    await self.app_logger.log_and_display(
                                        message=translations["ru"]["errors"]["invalid_username"])
                                except ChatWriteForbiddenError:
                                    await self.app_logger.log_and_display(
                                        message=translations["ru"]["errors"]["chat_write_forbidden"])
                                    await self.utils.record_and_interrupt(time_range_1=self.tb_time_from.value,
                                                                          time_range_2=self.tb_time_to.value)
                                    break  # Прерываем работу и меняем аккаунт
                                except (TypeError, UnboundLocalError):
                                    continue  # Записываем ошибку в software_database.db и продолжаем работу
                        except KeyError:
                            sys.exit(1)
                    await self.app_logger.end_time(start=start)
                    await show_notification(page=self.page,
                                            message="🔚 Конец рассылки сообщений")  # Выводим уведомление пользователю
                except Exception as error:
                    logger.exception(error)
            else:
                await self.app_logger.log_and_display(f"Время сна: Некорректный диапазон, введите корректные значения")
            self.page.update()

        # Разделение интерфейса на верхнюю и нижнюю части
        self.page.views.append(
            ft.View(
                route="/sending_messages_via_chats_menu",
                controls=[
                    await self.gui_program.key_app_bar(),  # Кнопка "Назад"
                    ft.Text("Отправка сообщений в личку", size=18, weight=ft.FontWeight.BOLD),
                    list_view,  # Отображение логов 📝
                    ft.Row(controls=[self.tb_time_from, self.tb_time_to], spacing=20, ),
                    limits,
                    ft.Column(  # Верхняя часть: контрольные элементы
                        controls=[
                            ft.Button(
                                              translations["ru"]["buttons"]["done"],
                                              width=WIDTH_WIDE_BUTTON,
                                              height=BUTTON_HEIGHT,
                                              on_click=button_clicked),
                        ],
                    ), ], ))

    async def performing_the_operation(self, checs: bool, chat_list_fields: list, selected_account: str = None,
                                       auto_reply_text: str = None) -> None:
        """
        Выполняет рассылку сообщений по чатам или работу с автоответчиком.

        :param checs: Флаг режима автоответчика
        :param chat_list_fields: Список ссылок на группы для рассылки
        :param selected_account: Выбранный аккаунт (для автоответчика)
        :param auto_reply_text: Текст сообщения для автоответчика
        :return: None
        """

        # Определяем, какие сессии использовать
        if checs and selected_account:
            # Режим автоответчика: только один выбранный аккаунт
            sessions_to_use = [selected_account]
        else:
            # Обычный режим: все аккаунты
            sessions_to_use = self.session_string

        if not sessions_to_use:
            await self.app_logger.log_and_display("❌ Нет доступных аккаунтов для работы.")
            return

        if checs:
            # === РЕЖИМ АВТООТВЕТЧИКА ===
            try:
                for session_name in sessions_to_use:  # Перебор всех сессий
                    # Пользователь должен сам выбрать аккаунт
                    # Подключение к Telegram и вывод имя аккаунта в консоль / терминал
                    client: TelegramClient = await self.connect.client_connect_string_session(session_name=session_name)

                    @client.on(events.NewMessage(incoming=True))  # Обработчик личных сообщений
                    async def handle_private_messages(event):
                        """Обрабатывает входящие личные сообщения"""
                        if event.is_private:  # Проверяем, является ли сообщение личным
                            await self.app_logger.log_and_display(
                                message=f"📩 Входящее сообщение: {event.message.message}")
                            reply_text = auto_reply_text or "Спасибо за сообщение! Мы ответим позже."
                            await event.respond(reply_text)
                            await self.app_logger.log_and_display(f"🤖 Ответ отправлен: {reply_text}")

                    # Получаем список чатов, которым нужно отправить сообщение
                    await self.app_logger.log_and_display(message=f"Всего групп: {len(chat_list_fields)}")
                    for group_link in chat_list_fields:
                        try:
                            # Подписываемся на группы
                            await self.subscribe.subscribe_to_group_or_channel(client=client, groups=group_link)
                            await self.app_logger.log_and_display(message=f"✅ Подписка на группы: {group_link}")

                            # Находит все файлы в папке с сообщениями и папке с файлами для отправки.
                            messages, files = await self.all_find_and_all_files()
                            # Отправляем сообщения и файлы в группу
                            await self.send_content(client, group_link, messages, files)
                        except UserBannedInChannelError:
                            await self.app_logger.log_and_display(
                                message=f"❌ Запрещено отправлять сообщения в супергруппы/каналы.")
                        except ValueError:
                            await self.app_logger.log_and_display(
                                message=f"❌ Ошибка рассылки, проверьте ссылку: {group_link}")
                            break
                        await self.random_dream()  # Прерываем работу и меняем аккаунт
                    await client.run_until_disconnected()  # Запускаем программу и ждем отключения клиента
            except Exception as error:
                logger.exception(error)
        else:
            # === ОБЫЧНЫЙ РЕЖИМ РАССЫЛКИ ===
            try:
                start = await self.app_logger.start_time()
                for session_name in self.sessions_to_use:  # Перебор всех сессий
                    client: TelegramClient = await self.connect.client_connect_string_session(session_name=session_name)
                    # await self.connect.getting_account_data(client)

                    # Открываем базу данных с группами, в которые будут рассылаться сообщения
                    await self.app_logger.log_and_display(message=f"Всего групп: {len(chat_list_fields)}")
                    for group_link in chat_list_fields:  # Поочередно выводим записанные группы
                        try:

                            # Подписываемся на группы
                            await self.subscribe.subscribe_to_group_or_channel(client=client, groups=group_link)
                            await self.app_logger.log_and_display(message=f"✅ Подписка на группы: {group_link}")

                            # Находит все файлы в папке с сообщениями и папке с файлами для отправки.
                            messages, files = await self.all_find_and_all_files()
                            # Отправляем сообщения и файлы в группу
                            await self.send_content(client, group_link, messages, files)
                        except ChannelPrivateError:
                            await self.app_logger.log_and_display(
                                message=f"🔒 Группа {group_link} приватная или недоступна.")
                        except PeerFloodError:
                            await self.utils.record_and_interrupt(time_range_1=time_subscription_1,
                                                                  time_range_2=time_subscription_2)
                            break  # Прерываем работу и меняем аккаунт
                        except FloodWaitError as e:
                            await self.app_logger.log_and_display(
                                message=f"{translations["ru"]["errors"]["flood_wait"]}{e}",
                                level="error")
                            await asyncio.sleep(e.seconds)
                        except UserBannedInChannelError:
                            await self.utils.record_and_interrupt(time_range_1=time_subscription_1,
                                                                  time_range_2=time_subscription_2)
                            break  # Прерываем работу и меняем аккаунт
                        except ChatAdminRequiredError:
                            await self.app_logger.log_and_display(
                                message=translations["ru"]["errors"]["admin_rights_required"])
                            break
                        except ChatWriteForbiddenError:
                            await self.app_logger.log_and_display(
                                message=translations["ru"]["errors"]["chat_write_forbidden"])
                            await self.utils.record_and_interrupt(time_range_1=time_subscription_1,
                                                                  time_range_2=time_subscription_2)
                            break  # Прерываем работу и меняем аккаунт
                        except SlowModeWaitError as e:
                            await self.app_logger.log_and_display(
                                message=translations["ru"]["errors"]["slow_mode_wait"])
                            await asyncio.sleep(e.seconds)
                        except ValueError:
                            await self.app_logger.log_and_display(
                                message=translations["ru"]["errors"]["sending_error_check_link"])
                            break
                        except (TypeError, UnboundLocalError):
                            continue  # Записываем ошибку в software_database.db и продолжаем работу
                        except Exception as error:
                            logger.exception(error)
                    await client.disconnect()  # Разрываем соединение Telegram
                await self.app_logger.log_and_display(message="🔚 Конец отправки сообщений + файлов по чатам")
                await self.app_logger.end_time(start)
            except Exception as error:
                logger.exception(error)

    async def sending_messages_files_via_chats(self) -> None:
        """
        Отображает интерфейс для рассылки сообщений и файлов по чатам Telegram.

        :param page: Страница интерфейса Flet для отображения элементов управления
        :return: None
        """
        # Чекбокс для работы с автоответчиком
        c = ft.Checkbox(label="Работа с автоответчиком")
        # Поле для формирования списка чатов
        chat_list_field = ft.TextField(label="Формирование списка чатов")

        # Поле для текста автоответчика
        auto_reply_text_field = ft.TextField(
            label="Автоответчик: текст ответа",
            multiline=True,
            min_lines=2,
            max_lines=5,
            width=WIDTH_WIDE_BUTTON,
            hint_text="Введите сообщение для автоответа...",
        )

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

        # Обработчик кнопки "Готово"
        async def button_clicked(_):
            # Получаем значение третьего поля и разделяем его на список по пробелам
            chat_list_input = chat_list_field.value.strip()  # Удаляем лишние пробелы
            if chat_list_input:  # Если поле не пустое
                chat_list_fields = chat_list_input.split()  # Разделяем строку по пробелам
            else:
                # Если поле пустое, используем данные из базы данных
                links: list = get_writing_group_links()  # Открываем базу данных # Получение ссылки
                logger.info(links)
                chat_list_fields = [group for group in links]  # Извлекаем только ссылки из кортежей
                logger.info(chat_list_fields)
            if self.tb_time_from.value or TIME_SENDING_MESSAGES_1 < self.tb_time_to.value or TIME_SENDING_MESSAGES_2:
                selected_account = account_drop_down_list.value  # ← Получаем key выбранного аккаунта
                await self.performing_the_operation(
                    checs=c.value,
                    chat_list_fields=chat_list_fields,
                    selected_account=selected_account,
                    auto_reply_text=auto_reply_text_field.value
                )
            else:
                t.value = f"Время сна: Некорректный диапазон, введите корректные значения"
                t.update()
            self.page.update()

        t = ft.Text()
        # Разделение интерфейса на верхнюю и нижнюю части
        self.page.views.append(
            ft.View(
                route="/sending_messages_via_chats_menu",
                controls=[
                    await self.gui_program.key_app_bar(),  # Кнопка "Назад"
                    ft.Text(spans=[
                        ft.TextSpan(translations["ru"]["message_sending_menu"]["sending_messages_files_via_chats"],
                                    ft.TextStyle(size=20, weight=ft.FontWeight.BOLD,
                                                 foreground=ft.Paint(
                                                     gradient=ft.PaintLinearGradient((0, 20),
                                                                                     (150, 20),
                                                                                     [ft.Colors.PINK,
                                                                                      ft.Colors.PURPLE])), ), ), ], ),
                    list_view,  # Отображение логов 📝
                    account_drop_down_list,  # Выпадающий список с аккаунтами
                    auto_reply_text_field,  # Поле для текста автоответчика
                    c,
                    ft.Row(
                        controls=[self.tb_time_from, self.tb_time_to],
                        spacing=20,
                    ),
                    t,
                    chat_list_field,
                    ft.Column(  # Верхняя часть: контрольные элементы
                        controls=[
                            ft.Button(
                                translations["ru"]["buttons"]["done"],
                                width=WIDTH_WIDE_BUTTON,
                                height=BUTTON_HEIGHT,
                                on_click=button_clicked
                            ),
                        ],
                    ),
                ],
            )
        )

    async def send_content(self, client, target, messages, files):
        """
        Отправляет сообщения и файлы в указанную цель (личку или группу).

        :param client: Экземпляр клиента Telegram
        :param target: Ссылка на группу или личку
        :param messages: Список сообщений для отправки
        :param files: Список файлов для отправки
        :return: None
        """
        await self.app_logger.log_and_display(f"Отправляем сообщение: {target}")
        if not messages:
            for file in files:
                await client.send_file(target, f"user_data/files_to_send/{file}")
                await self.app_logger.log_and_display(f"Файл {file} отправлен в {target}.")
        else:
            message = await self.select_and_read_random_file(messages, folder="message")
            if not files:
                try:
                    await client.send_message(entity=target, message=message)
                except ForbiddenError as e:
                    if "ALLOW_PAYMENT_REQUIRED" in str(e):
                        await self.app_logger.log_and_display(
                            f"❌ Невозможно отправить сообщение: пользователь закрыл личку от незнакомцев.",
                            level="warning"
                        )
            else:
                for file in files:
                    await client.send_file(target, f"user_data/files_to_send/{file}", caption=message)
                    await self.app_logger.log_and_display(f"Сообщение и файл отправлены: {target}")
        await self.random_dream()

    async def all_find_and_all_files(self):
        """
        Находит все файлы в папках с сообщениями и файлами для отправки.

        :return: Кортеж с двумя списками - сообщениями и файлами
        """
        return (await self.utils.find_files(directory_path=path_folder_with_messages, extension=self.file_extension),
                await self.utils.all_find_files(directory_path="user_data/files_to_send"))

    async def random_dream(self):
        """
        Выполняет случайную задержку между операциями.

        :return: None
        """
        try:
            time_in_seconds = random.randrange(TIME_SENDING_MESSAGES_1, TIME_SENDING_MESSAGES_2)
            await self.app_logger.log_and_display(f"Спим {time_in_seconds} секунд...")
            await asyncio.sleep(time_in_seconds)  # Спим 1 секунду
        except Exception as error:
            logger.exception(error)

    async def select_and_read_random_file(self, entities, folder):
        """
        Выбирает случайный файл и читает из него данные.

        :param entities: Список имён файлов (без расширения) для чтения
        :param folder: Подпапка внутри user_data (например, "message" или "answering_machine")
        :return: Содержимое JSON-файла или None при ошибке
        """
        try:
            if not entities:
                await self.app_logger.log_and_display(f"📁 Папка 'user_data/{folder}' пуста. Нет файлов для выбора.")
                return None

            random_file = random.choice(entities)
            filename = f"user_data/{folder}/{random_file[0]}.json"

            logger.info(f"Выбран файл для чтения: {filename}")

            await self.app_logger.log_and_display(f"Выбран файл для чтения: {random_file[0]}.json")

            return await self.utils.read_json_file(filename=filename)

        except Exception as error:
            await self.app_logger.log_and_display(f"⚠️ Ошибка при чтении файла из папки {folder}: {error}",
                                                  level="error")
            logger.exception(error)
            return None

# 455
