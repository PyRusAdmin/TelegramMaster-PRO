# -*- coding: utf-8 -*-
import asyncio
import random
import sys

import flet as ft
from loguru import logger
from telethon import events
from telethon.errors import (ChannelPrivateError, ChatAdminRequiredError, ChatWriteForbiddenError, FloodWaitError,
                             PeerFloodError, SlowModeWaitError, UserBannedInChannelError, UserIdInvalidError,
                             UsernameInvalidError, UsernameNotOccupiedError, UserNotMutualContactError)

from src.core.configs import (BUTTON_HEIGHT, ConfigReader, WIDTH_WIDE_BUTTON, path_accounts_folder,
                              path_folder_with_messages, PATH_SEND_MESSAGE_FOLDER_ANSWERING_MACHINE,
                              path_send_message_folder_answering_machine_message, TIME_SENDING_MESSAGES_1,
                              time_sending_messages_2, time_subscription_1, time_subscription_2)
from src.core.sqlite_working_tools import select_records_with_limit, open_and_read_data
from src.core.utils import Utils
from src.features.account.connect import TGConnect
from src.features.account.parsing.gui_elements import GUIProgram
from src.features.account.subscribe_unsubscribe.subscribe_unsubscribe import SubscribeUnsubscribeTelegram
from src.gui.gui import list_view, AppLogger
from src.locales.translations_loader import translations


class SendTelegramMessages:
    """
    Отправка (текстовых) сообщений в личку Telegram пользователям из базы данных.
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.connect = TGConnect(page)
        self.sub_unsub_tg = SubscribeUnsubscribeTelegram(page)
        self.account_extension = "session"  # Расширение файла аккаунта
        self.file_extension = "json"
        self.app_logger = AppLogger(page=page)
        self.utils = Utils(page=page)

    async def send_files_to_personal_chats(self) -> None:
        """
        Отправка файлов в личку
        """

        output = ft.Text("Отправка сообщений в личку", size=18, weight=ft.FontWeight.BOLD)

        async def button_clicked(_):
            """Обработчик кнопки "Готово" """
            time_from = tb_time_from.value or TIME_SENDING_MESSAGES_1  # Получаем значение первого поля
            time_to = tb_time_to.value or time_sending_messages_2  # Получаем значение второго поля

            # Получаем значение третьего поля и разделяем его на список по пробелам
            account_limits_input = account_limits_inputs.value  # Удаляем лишние пробелы
            if account_limits_input:  # Если поле не пустое
                limits = account_limits_input  # Разделяем строку по пробелам
                await self.app_logger.log_and_display(f"{limits}")
            else:
                limits = ConfigReader().get_limits()
            if time_from < time_to:
                try:
                    # Просим пользователя ввести расширение сообщения
                    for session_name in self.utils.find_filess(directory_path=path_accounts_folder,
                                                               extension=self.account_extension):
                        client = await self.connect.get_telegram_client(session_name,
                                                                        account_directory=path_accounts_folder)
                        try:
                            # Открываем parsing список user_data/software_database.db для inviting в группу
                            usernames = select_records_with_limit(limit=int(limits))
                            # Количество аккаунтов на данный момент в работе
                            await self.app_logger.log_and_display(f"Всего username: {len(usernames)}")
                            for rows in usernames:
                                username = rows[
                                    0]  # Получаем имя аккаунта из базы данных user_data/software_database.db
                                await self.app_logger.log_and_display(f"[!] Отправляем сообщение: {username}")
                                try:
                                    user_to_add = await client.get_input_entity(username)
                                    messages, files = await self.all_find_and_all_files()
                                    await self.send_content(client, user_to_add, messages, files)
                                    await self.app_logger.log_and_display(
                                        f"Отправляем сообщение в личку {username}. Файл {files} отправлен пользователю {username}.")
                                    await self.utils.record_inviting_results(time_from, time_to, rows)
                                except FloodWaitError as e:
                                    await self.app_logger.log_and_display(
                                        f"{translations["ru"]["errors"]["flood_wait"]}{e}",
                                        level="error")
                                    await self.utils.record_and_interrupt(time_from, time_to)
                                    break  # Прерываем работу и меняем аккаунт
                                except PeerFloodError:
                                    await self.utils.record_and_interrupt(time_from, time_to)
                                    break  # Прерываем работу и меняем аккаунт
                                except UserNotMutualContactError:
                                    await self.app_logger.log_and_display(
                                        translations["ru"]["errors"]["user_not_mutual_contact"])
                                except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
                                    await self.app_logger.log_and_display(
                                        translations["ru"]["errors"]["invalid_username"])
                                except ChatWriteForbiddenError:
                                    await self.app_logger.log_and_display(
                                        translations["ru"]["errors"]["chat_write_forbidden"])
                                    await self.utils.record_and_interrupt(time_from, time_to)
                                    break  # Прерываем работу и меняем аккаунт
                                except (TypeError, UnboundLocalError):
                                    continue  # Записываем ошибку в software_database.db и продолжаем работу
                        except KeyError:
                            sys.exit(1)
                except Exception as error:
                    logger.exception(error)
            else:
                t.value = f"Время сна: Некорректный диапазон, введите корректные значения"
                t.update()
            self.page.update()

        # GUI элементы

        tb_time_from, tb_time_to = await self.sleep_selection_input()
        sleep_time_group = ft.Row(controls=[tb_time_from, tb_time_to], spacing=20, )
        # Поле для формирования списка чатов
        account_limits_inputs = ft.TextField(label="Введите лимит на сообщения", multiline=True, max_lines=12)

        # Кнопка "Готово"
        button_done = ft.ElevatedButton(text=translations["ru"]["buttons"]["done"], width=WIDTH_WIDE_BUTTON,
                                        height=BUTTON_HEIGHT,
                                        on_click=button_clicked, )

        t = ft.Text()
        # Разделение интерфейса на верхнюю и нижнюю части
        self.page.views.append(
            ft.View("/sending_messages_via_chats_menu",
                    controls=[
                        await GUIProgram().key_app_bar(),  # Кнопка "Назад"
                        output, sleep_time_group, t, account_limits_inputs,
                        ft.Column(  # Верхняя часть: контрольные элементы
                            controls=[
                                button_done,
                            ],
                        ), ], ))

    @staticmethod
    async def sleep_selection_input():
        # Группа полей ввода для времени сна
        tb_time_from = ft.TextField(label="Время сна от", width=297, hint_text="Введите время", border_radius=5, )
        tb_time_to = ft.TextField(label="Время сна до", width=297, hint_text="Введите время", border_radius=5, )
        return tb_time_from, tb_time_to

    async def performing_the_operation(self, checs, chat_list_fields) -> None:
        """
        Рассылка сообщений по чатам
        :param chat_list_fields: список ссылок на группы
        :param checs: значение чекбокса
        """
        # Создаем ListView для отображения логов
        self.page.views.clear()
        self.page.update()
        self.page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
        # Кнопка "Назад"
        button_back = ft.ElevatedButton(text=translations["ru"]["buttons"]["back"], width=WIDTH_WIDE_BUTTON,
                                        height=BUTTON_HEIGHT,
                                        on_click=lambda _: self.page.go("/sending_messages_via_chats_menu"))
        # Создание View с элементами
        self.page.views.append(
            ft.View(
                "/sending_messages_via_chats_menu",
                controls=[
                    list_view,  # отображение логов 📝
                    ft.Column(
                        controls=[button_back]
                    )]))

        if checs == True:
            try:
                for session_name in self.utils.find_filess(directory_path=PATH_SEND_MESSAGE_FOLDER_ANSWERING_MACHINE,
                                                           extension=self.account_extension):
                    client = await self.connect.get_telegram_client(session_name,
                                                                    account_directory=PATH_SEND_MESSAGE_FOLDER_ANSWERING_MACHINE)

                    @client.on(events.NewMessage(incoming=True))  # Обработчик личных сообщений
                    async def handle_private_messages(event):
                        """Обрабатывает входящие личные сообщения"""
                        if event.is_private:  # Проверяем, является ли сообщение личным
                            await self.app_logger.log_and_display(f"Входящее сообщение: {event.message.message}")
                            entities = self.utils.find_files(
                                directory_path=path_send_message_folder_answering_machine_message,
                                extension=self.file_extension)
                            await self.app_logger.log_and_display(f"{entities}")
                            data = await self.select_and_read_random_file(entities, folder="answering_machine")
                            await self.app_logger.log_and_display(f"{data}")
                            await event.respond(f'{data}')  # Отвечаем на входящее сообщение

                    # Получаем список чатов, которым нужно отправить сообщение
                    await self.app_logger.log_and_display(f"Всего групп: {len(chat_list_fields)}")
                    self.page.update()
                    for group_link in chat_list_fields:
                        try:
                            await self.sub_unsub_tg.subscribe_to_group_or_channel(client, group_link, self.page)
                            # Находит все файлы в папке с сообщениями и папке с файлами для отправки.
                            messages, files = await self.all_find_and_all_files()
                            # Отправляем сообщения и файлы в группу
                            await self.send_content(client, group_link, messages, files)
                        except UserBannedInChannelError:
                            await self.app_logger.log_and_display(
                                f"Вам запрещено отправлять сообщения в супергруппах/каналах (вызвано запросом SendMessageRequest)")
                        except ValueError:
                            await self.app_logger.log_and_display(
                                f"❌ Ошибка рассылки, проверьте ссылку  на группу: {group_link}")
                            break
                        await self.random_dream()  # Прерываем работу и меняем аккаунт
                    await client.run_until_disconnected()  # Запускаем программу и ждем отключения клиента
            except Exception as error:
                logger.exception(error)
        else:
            try:
                start = await self.app_logger.start_time()
                for session_name in self.utils.find_filess(directory_path=path_accounts_folder,
                                                           extension=self.account_extension):
                    client = await self.connect.get_telegram_client(session_name,
                                                                    account_directory=path_accounts_folder)
                    # Открываем базу данных с группами, в которые будут рассылаться сообщения
                    await self.app_logger.log_and_display(f"Всего групп: {len(chat_list_fields)}")
                    for group_link in chat_list_fields:  # Поочередно выводим записанные группы
                        try:
                            await self.sub_unsub_tg.subscribe_to_group_or_channel(client, group_link, self.page)
                            # Находит все файлы в папке с сообщениями и папке с файлами для отправки.
                            messages, files = await self.all_find_and_all_files()
                            # Отправляем сообщения и файлы в группу
                            await self.send_content(client, group_link, messages, files)
                        except ChannelPrivateError:
                            await self.app_logger.log_and_display(
                                f"Группа {group_link} приватная или подписка запрещена.")
                        except PeerFloodError:
                            await self.utils.record_and_interrupt(time_subscription_1, time_subscription_2)
                            break  # Прерываем работу и меняем аккаунт
                        except FloodWaitError as e:
                            await self.app_logger.log_and_display(f"{translations["ru"]["errors"]["flood_wait"]}{e}",
                                                                  level="error")
                            await asyncio.sleep(e.seconds)
                        except UserBannedInChannelError:
                            await self.utils.record_and_interrupt(time_subscription_1, time_subscription_2)
                            break  # Прерываем работу и меняем аккаунт
                        except ChatAdminRequiredError:
                            await self.app_logger.log_and_display(translations["ru"]["errors"]["admin_rights_required"])
                            break
                        except ChatWriteForbiddenError:
                            await self.app_logger.log_and_display(translations["ru"]["errors"]["chat_write_forbidden"])
                            await self.utils.record_and_interrupt(time_subscription_1, time_subscription_2)
                            break  # Прерываем работу и меняем аккаунт
                        except SlowModeWaitError as e:
                            await self.app_logger.log_and_display(translations["ru"]["errors"]["slow_mode_wait"])
                            await asyncio.sleep(e.seconds)
                        except ValueError:
                            await self.app_logger.log_and_display(
                                translations["ru"]["errors"]["sending_error_check_link"])
                            break
                        except (TypeError, UnboundLocalError):
                            continue  # Записываем ошибку в software_database.db и продолжаем работу
                        except Exception as error:
                            logger.exception(error)
                    await client.disconnect()  # Разрываем соединение Telegram
                await self.app_logger.log_and_display("🔚 Конец отправки сообщений + файлов по чатам")
                await self.app_logger.end_time(start)
            except Exception as error:
                logger.exception(error)

    async def sending_messages_files_via_chats(self) -> None:
        """
        Рассылка сообщений + файлов по чатам
        """

        # Обработчик кнопки "Готово"
        async def button_clicked(_):
            # Получаем значение третьего поля и разделяем его на список по пробелам
            chat_list_input = chat_list_field.value.strip()  # Удаляем лишние пробелы
            if chat_list_input:  # Если поле не пустое
                chat_list_fields = chat_list_input.split()  # Разделяем строку по пробелам
            else:
                # Если поле пустое, используем данные из базы данных
                db_chat_list = await open_and_read_data(table_name="writing_group_links",
                                                        page=self.page)
                chat_list_fields = [group[0] for group in db_chat_list]  # Извлекаем только ссылки из кортежей
            if tb_time_from.value or TIME_SENDING_MESSAGES_1 < tb_time_to.value or time_sending_messages_2:
                await self.performing_the_operation(c.value, chat_list_fields)
            else:
                t.value = f"Время сна: Некорректный диапазон, введите корректные значения"
                t.update()
            self.page.update()

        # Чекбокс для работы с автоответчиком
        c = ft.Checkbox(label="Работа с автоответчиком")
        tb_time_from, tb_time_to = await self.sleep_selection_input()
        # Поле для формирования списка чатов
        chat_list_field = ft.TextField(label="Формирование списка чатов", multiline=True, max_lines=12)

        t = ft.Text()
        # Разделение интерфейса на верхнюю и нижнюю части
        self.page.views.append(
            ft.View(
                "/sending_messages_via_chats_menu",
                controls=[
                    await GUIProgram().key_app_bar(),  # Кнопка "Назад"
                    ft.Text(translations["ru"]["message_sending_menu"]["sending_messages_files_via_chats"], size=18,
                            weight=ft.FontWeight.BOLD), c, ft.Row(controls=[tb_time_from, tb_time_to], spacing=20, ), t,
                    chat_list_field,
                    ft.Column(  # Верхняя часть: контрольные элементы
                        controls=[
                            ft.ElevatedButton(text=translations["ru"]["buttons"]["done"], width=WIDTH_WIDE_BUTTON,
                                              height=BUTTON_HEIGHT,
                                              on_click=button_clicked, ),
                        ],
                    ), ], ))

    async def send_content(self, client, target, messages, files):
        """
        Отправляет сообщения и файлы в личку.
        :param client: Телеграм клиент
        :param target: Ссылка на группу (или личку)
        :param messages: Список сообщений
        :param files: Список файлов
        """
        await self.app_logger.log_and_display(f"Отправляем сообщение: {target}")
        if not messages:
            for file in files:
                await client.send_file(target, f"user_data/files_to_send/{file}")
                await self.app_logger.log_and_display(f"Файл {file} отправлен в {target}.")
        else:
            message = await self.select_and_read_random_file(messages, folder="message")
            if not files:
                await client.send_message(entity=target, message=message)
            else:
                for file in files:
                    await client.send_file(target, f"user_data/files_to_send/{file}", caption=message)
                    await self.app_logger.log_and_display(f"Сообщение и файл отправлены: {target}")
        await self.random_dream()

    async def all_find_and_all_files(self):
        """
        Находит все файлы в папке с сообщениями и папке с файлами для отправки.
        """
        messages = self.utils.find_files(directory_path=path_folder_with_messages, extension=self.file_extension)
        files = self.utils.all_find_files(directory_path="user_data/files_to_send")
        return messages, files

    async def random_dream(self):
        """
        Рандомный сон
        """
        try:
            time_in_seconds = random.randrange(TIME_SENDING_MESSAGES_1, time_sending_messages_2)
            await self.app_logger.log_and_display(f"Спим {time_in_seconds} секунд...")
            await asyncio.sleep(time_in_seconds)  # Спим 1 секунду
        except Exception as error:
            logger.exception(error)

    async def select_and_read_random_file(self, entities, folder):
        """
        Выбираем рандомный файл для чтения

        :param entities: список файлов для чтения
        :param folder: папка для сохранения файлов
        """
        try:
            if entities:  # Проверяем, что список не пустой, если он не пустой
                # Выбираем рандомный файл для чтения
                random_file = random.choice(entities)  # Выбираем случайный файл для чтения из списка файлов
                await self.app_logger.log_and_display(f"Выбран файл для чтения: {random_file[0]}.json")
                data = self.utils.read_json_file(filename=f"user_data/{folder}/{random_file[0]}.json")
            return data  # Возвращаем данные из файла
        except Exception as error:
            logger.exception(error)
            return None
