# -*- coding: utf-8 -*-
import asyncio
import datetime as dt

import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from scheduler.asyncio import Scheduler
from telethon import TelegramClient
from telethon.errors import (AuthKeyDuplicatedError, ChannelPrivateError, SessionRevokedError, TypeNotFoundError,
                             UserBannedInChannelError, UserChannelsTooMuchError, UserNotMutualContactError,
                             UserKickedError, UserDeactivatedBanError, UsernameInvalidError, UsernameNotOccupiedError,
                             UserIdInvalidError, ChatAdminRequiredError, UserPrivacyRestrictedError,
                             BotGroupsBlockedError, BadRequestError, ChatWriteForbiddenError, InviteRequestSentError,
                             FloodWaitError, AuthKeyUnregisteredError, PeerFloodError)
from telethon.tl.functions.channels import InviteToChannelRequest

from src.core.configs import BUTTON_HEIGHT, WIDTH_WIDE_BUTTON, width_tvo_input, width_one_input
from src.core.database.account import getting_account
from src.core.database.database import (select_records_with_limit, get_links_inviting, save_links_inviting)
from src.core.utils import Utils
from src.features.account.connect import TGConnect
from src.features.account.subscribe import Subscribe
from src.features.account.subscribe_unsubscribe import SubscribeUnsubscribeTelegram
from src.features.account.switch_controller import ToggleController
from src.gui.gui import AppLogger, list_view
from src.gui.gui_elements import GUIProgram
from src.gui.gui_input_builders import TimeInputRowBuilder, LinkInputRowBuilder
from src.gui.notification import show_notification
from src.locales.translations_loader import translations


def get_limit(limits):
    """
    Извлекает и преобразует пользовательский ввод лимита в целое число.

    :param limits: Объект, содержащий поле `value` с введённым пользователем значением.
    :return LIMITS: Целое число — установленный лимит, если значение предоставлено и не пустое; иначе — None.
    """
    if limits.value:
        limits = int(limits.value)  # Преобразуем в число, если значение есть
    else:
        limits = None  # Оставляем LIMITS без изменений
    return limits


class InvitingToAGroup:

    def __init__(self, page: ft.Page):
        self.page = page
        self.scheduler = Scheduler()  # Создаем экземпляр планировщика
        self.links_inviting = get_links_inviting()  # Получаем список ссылок на группы для инвайтинга из базы данных
        self.app_logger = AppLogger(page=page)
        self.connect = TGConnect(page=page)
        self.utils = Utils(page=page)
        self.subscribe = Subscribe(page=page)  # Инициализация экземпляра класса Subscribe (Подписка)
        self.gui_program = GUIProgram()
        self.session_string = getting_account()  # Получаем строку сессии из файла базы данных
        self.subscribe_unsubscribe_telegram = SubscribeUnsubscribeTelegram(page=page)

    async def inviting_menu(self):
        """
        Меню инвайтинг
        """
        list_view.controls.clear()  # ✅ Очистка логов перед новым запуском
        self.page.controls.append(list_view)  # Добавляем ListView на страницу для отображения логов 📝
        self.page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        # Отображение информации о настройках инвайтинга
        await self.app_logger.log_and_display(
            message=(
                f"Всего usernames: {len(select_records_with_limit(limit=None))}\n"
                f"Всего подключенных аккаунтов: {len(self.session_string)}\n"
            )
        )

        async def get_invitation_links():
            """
            Получает ссылки для инвайтинга: сначала пытается взять из поля ввода,
            если оно пустое — использует значение из выпадающего списка.
            """
            input_links = link_entry_field.value.strip()
            if input_links:
                links = input_links.split()
                await self.app_logger.log_and_display(message=f"Пользователь ввёл ссылки: {links}")
                # Сохраняем в БД
                data_to_save = {"links_inviting": links}
                save_links_inviting(data=data_to_save)
                await self.app_logger.log_and_display(message=f"Сохранено в базу данных: {data_to_save}")
                await self.app_logger.log_and_display(message="✅ Ссылки успешно сохранены.")
                return links[0]
            else:
                # Берём из dropdown, если ввод пуст
                links = dropdown.value
                if not links:
                    await self.app_logger.log_and_display(
                        message="⚠️ Не указаны ссылки для инвайтинга.", level="warning"
                    )
                    return None
                if isinstance(links, str):
                    links = [links]  # Приводим к списку, если нужно
                await self.app_logger.log_and_display(message=f"Используем ссылки из dropdown: {links}")
                return links[0]

        async def general_invitation_to_the_group(_):
            """
            Основной метод для выполнения инвайтинга пользователей в указанные группы.
            """

            links = await get_invitation_links()
            if not links:
                return  # Нет ссылок — завершаем выполнение

            time_inviting_1 = TIME_INVITING_1.value
            if time_inviting_1 == "":
                await show_notification(page=self.page, message="Время должно быть больше 0")
                self.page.go("/inviting")
                return

            time_inviting_2 = TIME_INVITING_2.value
            if time_inviting_2 == "":
                await show_notification(page=self.page, message="Время должно быть больше 0")
                self.page.go("/inviting")
                return

            start = await self.app_logger.start_time()
            self.page.update()  # Обновите страницу, чтобы сразу показать сообщение 🔄

            limit = get_limit(limits)  # Получаем лимит введенный пользователем

            usernames = select_records_with_limit(limit=limit, app_logger=self.app_logger)
            await self.app_logger.log_and_display(message=f"Список usernames: {usernames}\n\nЛимит на аккаунт {limit}")

            if not usernames:
                await self.app_logger.log_and_display(
                    message="В таблице members нет пользователей для инвайтинга."
                )
                await show_notification(page=self.page, message="🔚 Нет пользователей для инвайтинга")
                self.page.go("/inviting")
                return

            for session_name in self.session_string:
                client: TelegramClient = await self.connect.client_connect_string_session(session_name=session_name)
                await self.connect.getting_account_data(client)

                # Подписываемся на группы
                await self.subscribe.subscribe_to_group_or_channel(client=client, groups=links)
                await self.app_logger.log_and_display(message=f"✅ Подписка на группы: {links}")

                if len(usernames) == 0:
                    await self.app_logger.log_and_display(message=f"В таблице members нет пользователей для инвайтинга")
                    await self.subscribe_unsubscribe_telegram.unsubscribe_from_the_group(client, links)
                    break  # Прерываем работу и меняем аккаунт

                for username in usernames:
                    await self.app_logger.log_and_display(message=f"Приглашение пользователя: {username}")
                    # Инвайтинг в группу по полученному списку

                    try:
                        await self.add_user_test(
                            client=client,
                            username_group=links,
                            username=username,
                            time_inviting_1=TIME_INVITING_1.value,
                            time_inviting_2=TIME_INVITING_2.value
                        )
                    except KeyboardInterrupt:  # Закрытие окна программы
                        await self.app_logger.log_and_display(message=translations["ru"]["errors"]["script_stopped"],
                                                              level="error")
                await self.subscribe_unsubscribe_telegram.unsubscribe_from_the_group(
                    client=client,
                    group_link=links
                )
                await self.app_logger.log_and_display(message=f"[!] Инвайтинг окончен!")

            await self.app_logger.end_time(start=start)
            await show_notification(page=self.page, message="🔚 Конец инвайтинга")  # Выводим уведомление пользователю
            self.page.go("/inviting")  # переходим к основному меню инвайтинга 🏠

        async def launching_an_invite_once_an_hour(_):
            """
            🚀 Запускает процесс инвайтинга групп и отображает статус в интерфейсе.
            ⏰ Инвайтинг 1 раз в час. Запуск приглашения участников 1 раз в час.
            """
            try:
                async def general_invitation_group_scheduler():
                    await general_invitation_to_the_group(_)

                await self.app_logger.log_and_display(message="Запуск программы в 00 минут каждого часа")
                self.scheduler.hourly(dt.time(minute=00, second=00),
                                      general_invitation_group_scheduler)  # Асинхронная функция для выполнения
                while True:
                    await asyncio.sleep(1)
            except Exception as error:
                logger.exception(error)

        async def schedule_invite(_):
            """
            🚀 Запускает процесс инвайтинга групп и отображает статус в интерфейсе.
            🕒 Инвайтинг в определенное время. Запуск автоматической отправки приглашений участникам каждый день в определенное время.
            """
            try:
                async def general_invitation_group_scheduler():
                    await general_invitation_to_the_group(_)

                await self.app_logger.log_and_display(
                    message=f"Скрипт будет запускаться каждый день в {hour.value}:{minutes.value}")
                self.scheduler.once(dt.time(hour=int(hour.value), minute=int(minutes.value)),
                                    general_invitation_group_scheduler)
                while True:
                    await asyncio.sleep(1)
            except Exception as error:
                logger.exception(error)

        async def launching_invite_every_day_certain_time(_):
            """
            🚀 Запускает процесс инвайтинга групп и отображает статус в интерфейсе.
            📅 Инвайтинг каждый день. Запуск приглашения участников каждый день в определенное время, выбранное пользователем.
            """

            async def general_invitation_group_scheduler():
                await general_invitation_to_the_group(_)

            await self.app_logger.log_and_display(
                message=f"Скрипт будет запускаться каждый день в {hour.value}:{self.minutes}")
            self.scheduler.daily(dt.time(hour=int(hour.value), minute=int(minutes.value)),
                                 general_invitation_group_scheduler)
            while True:
                await asyncio.sleep(1)

        async def start_inviting_grup(_):
            """
            ⚙️ Метод для запуска инвайтинга
            """
            if inviting_switch.value:  # Инвайтинг
                await general_invitation_to_the_group(_)
            if inviting_1_time_per_hour_switch.value:
                await launching_an_invite_once_an_hour(_)
            if inviting_at_a_certain_time_switch.value:  # Инвайтинг в определенное время
                await schedule_invite(_)
            if inviting_every_day_switch.value:  # Инвайтинг каждый день
                await launching_invite_every_day_certain_time(_)

        # Создаем выпадающий список с названиями групп
        dropdown = ft.Dropdown(
            width=WIDTH_WIDE_BUTTON,
            options=[ft.DropdownOption(link) for link in self.links_inviting],
            autofocus=True
        )

        """
        Пользователь вводит время задержки между инвайтингом (приглашениями в группу)
        """

        # Два поля ввода для времени и кнопка сохранить
        TIME_INVITING_1, TIME_INVITING_2 = await TimeInputRowBuilder().build_time_inputs_with_save_button(
            label_min="Мин. задержка (сек)",
            label_max="Макс. задержка (сек)",
            width=width_tvo_input
        )
        # Два поля ввода для времени и кнопка сохранить
        hour, minutes = await TimeInputRowBuilder().build_time_inputs_with_save_button(
            label_min="Час запуска (0–23)",
            label_max="Минуты (0–59)",
            width=width_tvo_input
        )

        """
        Пользователь вводит лимит на аккаунт и вводит ссылку для инвайтинга, нечего сохранять не нужно, что бы не 
        усложнять проект.
        """

        # Поле ввода, для ссылок для инвайтинга
        limits = await LinkInputRowBuilder().build_link_input_with_save_button(
            label_text="Введите лимит на аккаунт",
            width=width_one_input
        )
        link_entry_field = await LinkInputRowBuilder().build_link_input_with_save_button(
            label_text="Введите ссылку на группу для инвайтинга",
            width=width_one_input
        )

        # Кнопки-переключатели
        inviting_switch = ft.CupertinoSwitch(label=translations["ru"]["inviting_menu"]["inviting"], value=False,
                                             disabled=True)
        inviting_1_time_per_hour_switch = ft.CupertinoSwitch(
            label=translations["ru"]["inviting_menu"]["invitation_1_time_per_hour"], value=False,
            disabled=True)
        inviting_at_a_certain_time_switch = ft.CupertinoSwitch(
            label=translations["ru"]["inviting_menu"]["invitation_at_a_certain_time"], value=False,
            disabled=True)
        inviting_every_day_switch = ft.CupertinoSwitch(label=translations["ru"]["inviting_menu"]["inviting_every_day"],
                                                       value=False, disabled=True)
        ToggleController(inviting_switch=inviting_switch,
                         inviting_1_time_per_hour_switch=inviting_1_time_per_hour_switch,
                         inviting_at_a_certain_time_switch=inviting_at_a_certain_time_switch,
                         inviting_every_day_switch=inviting_every_day_switch).element_handler_inviting(self.page)

        start_inviting = ft.ElevatedButton(
            width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
            text="Запуск",
            on_click=start_inviting_grup  # Используем синхронную обёртку
        )

        inviting_switch.disabled = False
        inviting_1_time_per_hour_switch.disabled = False
        inviting_at_a_certain_time_switch.disabled = False
        inviting_every_day_switch.disabled = False
        start_inviting.disabled = False

        self.page.views.append(
            ft.View(route="/inviting",
                    controls=[await self.gui_program.key_app_bar(),  # Кнопка назад
                              ft.Text(spans=[ft.TextSpan(translations["ru"]["inviting_menu"]["inviting"],
                                                         ft.TextStyle(size=20, weight=ft.FontWeight.BOLD,
                                                                      foreground=ft.Paint(
                                                                          gradient=ft.PaintLinearGradient((0, 20),
                                                                                                          (150, 20),
                                                                                                          [ft.Colors.PINK,
                                                                                                           ft.Colors.PURPLE])), ), ), ], ),
                              list_view,  # Отображение логов 📝

                              ft.Row([await TimeInputRowBuilder().compose_time_input_row(
                                  min_time_input=TIME_INVITING_1,
                                  max_time_input=TIME_INVITING_2,
                              ),
                                      await TimeInputRowBuilder().compose_time_input_row(min_time_input=hour,
                                                                                         max_time_input=minutes)]),

                              await self.gui_program.diver_castom(),  # Горизонтальная линия

                              ft.Row([await LinkInputRowBuilder().compose_link_input_row(
                                  link_input=limits,
                              ),
                                      await LinkInputRowBuilder().compose_link_input_row(
                                          link_input=link_entry_field,
                                      ),
                                      ]),

                              await self.gui_program.diver_castom(),  # Горизонтальная линия
                              ft.Text(value="📂 Выберите группу для инвайтинга"),  # Выбор группы для инвайтинга
                              dropdown,  # Выпадающий список с названиями групп
                              await self.gui_program.diver_castom(),  # Горизонтальная линия

                              ft.Row([
                                  inviting_switch,
                                  inviting_1_time_per_hour_switch,
                                  inviting_at_a_certain_time_switch,
                                  inviting_every_day_switch
                              ]),

                              ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                                  start_inviting,
                              ])]))
        self.page.update()  # обновляем страницу после добавления элементов управления 🔄

    async def add_user_test(self, client, username_group, username, time_inviting_1, time_inviting_2):
        """
        Метод для приглашения участников в группу.
        :param client: Телеграм-клиент
        :param username_group: Ссылка на группу
        :param username: Имя пользователя (username)
        :param time_inviting_1: Время ожидания начальное
        :param time_inviting_2: Время ожидания конечное
        :return:
        """
        try:
            await self.app_logger.log_and_display(message=f"Попытка приглашения {username} в группу {username_group}.")
            await client.connect()

            # Выполняем приглашение
            await client(InviteToChannelRequest(username_group, [username]))
            await self.app_logger.log_and_display(
                message=f"✅  Участник {username} добавлен, если не состоит в чате {username_group}. Спим от {time_inviting_1} до {time_inviting_2}")
            await self.utils.record_inviting_results(time_range_1=time_inviting_1, time_range_2=time_inviting_2,
                                                     username=username)
        except UserChannelsTooMuchError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["user_channels_too_much"])
            await self.utils.record_inviting_results(time_range_1=time_inviting_1, time_range_2=time_inviting_2,
                                                     username=username)
        except (ChannelPrivateError, TypeNotFoundError, AuthKeyDuplicatedError, UserBannedInChannelError,
                SessionRevokedError):
            await self.app_logger.log_and_display(
                message=translations["ru"]["errors"]["invalid_auth_session_terminated"])
            await self.utils.record_and_interrupt(time_range_1=time_inviting_1, time_range_2=time_inviting_2)
            await client.disconnect()
        except UserNotMutualContactError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["user_not_mutual_contact"])
            await self.utils.record_inviting_results(time_range_1=time_inviting_1, time_range_2=time_inviting_2,
                                                     username=username)
        except (UserKickedError, UserDeactivatedBanError):
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["user_kicked_or_banned"])
            await self.utils.record_inviting_results(time_range_1=time_inviting_1, time_range_2=time_inviting_2,
                                                     username=username)
        except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["invalid_username"])
            await self.utils.record_inviting_results(time_range_1=time_inviting_1, time_range_2=time_inviting_2,
                                                     username=username)
        except ChatAdminRequiredError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["admin_rights_required"])
            await self.utils.record_inviting_results(time_range_1=time_inviting_1, time_range_2=time_inviting_2,
                                                     username=username)
        except UserPrivacyRestrictedError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["user_privacy_restricted"])
            await self.utils.record_inviting_results(time_range_1=time_inviting_1, time_range_2=time_inviting_2,
                                                     username=username)
        except BotGroupsBlockedError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["bot_group_blocked"])
            await self.utils.record_inviting_results(time_range_1=time_inviting_1, time_range_2=time_inviting_2,
                                                     username=username)
        except (TypeError, UnboundLocalError):
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["type_or_scope"])
        except BadRequestError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["chat_member_add_failed"])

        # Ошибка инвайтинга прерываем работу
        except ChatWriteForbiddenError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["chat_write_forbidden"])
            await self.utils.record_inviting_results(time_range_1=time_inviting_1, time_range_2=time_inviting_2,
                                                     username=username)
            await client.disconnect()  # Прерываем работу и меняем аккаунт
        except InviteRequestSentError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["invite_request_sent"])
            await self.utils.record_inviting_results(time_range_1=time_inviting_1, time_range_2=time_inviting_2,
                                                     username=username)
            await client.disconnect()  # Прерываем работу и меняем аккаунт
        except FloodWaitError as e:
            await self.app_logger.log_and_display(message=f"{translations["ru"]["errors"]["flood_wait"]}{e}",
                                                  level="error")
            await self.utils.record_and_interrupt(time_range_1=time_inviting_1, time_range_2=time_inviting_2)
            await client.disconnect()  # Прерываем работу и меняем аккаунт
        except AuthKeyUnregisteredError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["auth_key_unregistered"])
            await self.utils.record_and_interrupt(time_range_1=time_inviting_1, time_range_2=time_inviting_2)
            await client.disconnect()
        except PeerFloodError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["peer_flood"], level="error")
            await self.utils.record_and_interrupt(time_range_1=time_inviting_1, time_range_2=time_inviting_2)
            await client.disconnect()  # Прерываем работу и меняем аккаунт
