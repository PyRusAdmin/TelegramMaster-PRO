# -*- coding: utf-8 -*-
import asyncio
import datetime as dt

import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from scheduler.asyncio import Scheduler
from telethon.errors import (AuthKeyDuplicatedError, ChannelPrivateError, SessionRevokedError, TypeNotFoundError,
                             UserBannedInChannelError, UserChannelsTooMuchError, UserNotMutualContactError,
                             UserKickedError, UserDeactivatedBanError, UsernameInvalidError, UsernameNotOccupiedError,
                             UserIdInvalidError, ChatAdminRequiredError, UserPrivacyRestrictedError,
                             BotGroupsBlockedError, BadRequestError, ChatWriteForbiddenError, InviteRequestSentError,
                             FloodWaitError, AuthKeyUnregisteredError, PeerFloodError)
from telethon.tl.functions.channels import InviteToChannelRequest

from src.core.configs import (BUTTON_HEIGHT, ConfigReader, LIMITS, WIDTH_WIDE_BUTTON, TIME_INVITING_1, TIME_INVITING_2)
from src.core.sqlite_working_tools import (select_records_with_limit, get_links_inviting, save_links_inviting,
                                           getting_account)
from src.core.utils import Utils
from src.features.account.connect import TGConnect
from src.gui.gui_elements import GUIProgram
from src.features.account.parsing.switch_controller import ToggleController
from src.gui.gui_input_builders import TimeInputRowBuilder, LinkInputRowBuilder
from src.features.account.subscribe_unsubscribe.subscribe import Subscribe
from src.features.account.subscribe_unsubscribe.subscribe_unsubscribe import SubscribeUnsubscribeTelegram
from src.features.settings.setting import SettingPage
from src.gui.gui import AppLogger
from src.gui.gui import list_view
from src.gui.notification import show_notification
from src.locales.translations_loader import translations


class InvitingToAGroup:

    def __init__(self, page: ft.Page):
        self.page = page
        self.config_reader = ConfigReader()
        self.hour, self.minutes = self.config_reader.get_hour_minutes_every_day()
        self.scheduler = Scheduler()  # Создаем экземпляр планировщика
        self.api_id_api_hash = self.config_reader.get_api_id_data_api_hash_data()
        self.api_id = self.api_id_api_hash[0]
        self.api_hash = self.api_id_api_hash[1]
        self.links_inviting = get_links_inviting()  # Получаем список ссылок на группы для инвайтинга из базы данных
        self.app_logger = AppLogger(page=page)
        self.connect = TGConnect(page=page)
        self.utils = Utils(page=page)
        self.setting_page = SettingPage(page=page)
        self.subscribe = Subscribe(page=page)  # Инициализация экземпляра класса Subscribe (Подписка)
        self.gui_program = GUIProgram()
        self.session_string = getting_account()  # Получаем строку сессии из файла базы данных

    async def inviting_menu(self):
        """
        Меню инвайтинг
        """
        list_view.controls.clear()  # ✅ Очистка логов перед новым запуском
        self.page.controls.append(list_view)  # Добавляем ListView на страницу для отображения логов 📝
        self.page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        # Отображение информации о настройках инвайтинга
        await self.app_logger.log_and_display(message=f"Лимит на аккаунт: {LIMITS}\n"
                                                      f"Всего usernames: {len(select_records_with_limit(limit=None))}\n"
                                                      f"Всего подключенных аккаунтов: {len(self.session_string)}\n")

        async def general_invitation_to_the_group(_):
            """
            Основной метод для инвайтинга
            """
            start = await self.app_logger.start_time()
            self.page.update()  # Обновите страницу, чтобы сразу показать сообщение 🔄
            for session_name in self.utils.find_filess(directory_path=path_accounts_folder, extension='session'):

                client = await self.connect.client_connect_string_session(session_name)
                await self.connect.getting_account_data(client)

                await self.subscribe.subscribe_to_group_or_channel(client=client, groups=dropdown.value)
                logger.info(f"Подписка на группу {dropdown.value} выполнена")
                await self.app_logger.log_and_display(message=f"{dropdown.value}")

                if limits.value:
                    LIMITS = int(limits.value)  # Преобразуем в число, если значение есть
                else:
                    pass  # Оставляем LIMITS без изменений

                usernames = select_records_with_limit(limit=LIMITS)
                logger.info(f"Список usernames: {usernames}")
                if len(usernames) == 0:
                    await self.app_logger.log_and_display(message=f"В таблице members нет пользователей для инвайтинга")
                    await SubscribeUnsubscribeTelegram(self.page).unsubscribe_from_the_group(client, dropdown.value)
                    break  # Прерываем работу и меняем аккаунт
                for username in usernames:
                    logger.info(f"Пользователь: {username}")
                    await self.app_logger.log_and_display(message=f"Пользователь username: {username}")
                    # Инвайтинг в группу по полученному списку
                    try:
                        await self.add_user_test(client, dropdown.value, username)
                    except KeyboardInterrupt:  # Закрытие окна программы
                        await self.app_logger.log_and_display(message=translations["ru"]["errors"]["script_stopped"],
                                                              level="error")
                await SubscribeUnsubscribeTelegram(self.page).unsubscribe_from_the_group(client, dropdown.value)
                await self.app_logger.log_and_display(message=f"[!] Инвайтинг окончен!")
            await self.app_logger.end_time(start)
            await show_notification(self.page, "🔚 Конец инвайтинга")  # Выводим уведомление пользователю
            self.page.go("/inviting")  # переходим к основному меню инвайтинга 🏠

        async def save(_):
            """Запись ссылки для инвайтинга в базу данных"""
            links = link_entry_field.value.strip().split()

            logger.info(f"Пользователь ввел ссылку(и): {links}")
            data_to_save = {
                "links_inviting": links,
            }
            save_links_inviting(data=data_to_save)
            logger.success(f"Сохранено в базу данных: {data_to_save}")
            await self.app_logger.log_and_display(message="✅ Ссылки успешно сохранены.")

            # 🔄 Обновляем список в выпадающем списке
            updated_links = get_links_inviting()
            dropdown.options = [ft.dropdown.Option(link) for link in updated_links]
            dropdown.value = links[0] if links else None  # Автоматически выбрать первую новую ссылку (если нужно)
            self.page.update()  # Обновляем интерфейс

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
                    message=f"Скрипт будет запускаться каждый день в {hour_textfield.value}:{minutes_textfield.value}")
                self.scheduler.once(dt.time(hour=int(hour_textfield.value), minute=int(minutes_textfield.value)),
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
                message=f"Скрипт будет запускаться каждый день в {hour_textfield.value}:{self.minutes}")
            self.scheduler.daily(dt.time(hour=int(hour_textfield.value), minute=int(minutes_textfield.value)),
                                 general_invitation_group_scheduler)
            while True:
                await asyncio.sleep(1)

        async def write_tame_start_inviting(_):
            """Записывает время запуска инвайтинга по времени. Час запуска и минуты запуска"""
            await self.setting_page.recording_the_time_to_launch_an_invite_every_day(hour_textfield=hour_textfield,
                                                                                     minutes_textfield=minutes_textfield)

        async def write_limit_account_inviting_timex(_):
            """Записывает время между сном во время ивайтинга"""
            await self.setting_page.create_main_window(variable="time_inviting", smaller_timex=smaller_timex,
                                                       larger_timex=larger_timex)

        async def write_limit_account_inviting(_):
            """Записывает лимит на аккаунт для инвайтинга"""
            await self.setting_page.record_setting(limit_type="account_limits", limits=limits)

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
        dropdown = ft.Dropdown(width=WIDTH_WIDE_BUTTON,
                               options=[ft.DropdownOption(link) for link in self.links_inviting],
                               autofocus=True)
        width_tvo_input = 215
        width_one_input = 440

        # Два поля ввода для времени и кнопка сохранить
        smaller_timex, larger_timex, save_button_timex = await TimeInputRowBuilder().build_time_inputs_with_save_button(
            on_save_click=write_limit_account_inviting_timex,
            label_min="Мин. задержка (сек)",
            label_max="Макс. задержка (сек)",
            width=width_tvo_input
        )
        # Два поля ввода для времени и кнопка сохранить
        hour_textfield, minutes_textfield, save_button_time = await TimeInputRowBuilder().build_time_inputs_with_save_button(
            on_save_click=write_tame_start_inviting,
            label_min="Час запуска (0–23)",
            label_max="Минуты (0–59)",
            width=width_tvo_input
        )

        # Поле ввода, для ссылок для инвайтинга
        limits, save_button_limit = await LinkInputRowBuilder().build_link_input_with_save_button(
            on_save_click=write_limit_account_inviting,
            label_text="Введите лимит на аккаунт", width=width_one_input)

        link_entry_field, save_button = await LinkInputRowBuilder().build_link_input_with_save_button(
            on_save_click=save,
            label_text="Введите ссылку на группу для инвайтинга",
            width=width_one_input)

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
            ft.View("/inviting",
                    [await self.gui_program.key_app_bar(),  # Кнопка назад
                     ft.Text(spans=[ft.TextSpan(translations["ru"]["inviting_menu"]["inviting"],
                                                ft.TextStyle(size=20, weight=ft.FontWeight.BOLD,
                                                             foreground=ft.Paint(
                                                                 gradient=ft.PaintLinearGradient((0, 20), (150, 20),
                                                                                                 [ft.Colors.PINK,
                                                                                                  ft.Colors.PURPLE])), ), ), ], ),
                     list_view,  # Отображение логов 📝

                     ft.Row([await TimeInputRowBuilder().compose_time_input_row(min_time_input=smaller_timex,
                                                                                max_time_input=larger_timex,
                                                                                save_button=save_button_timex),
                             await TimeInputRowBuilder().compose_time_input_row(min_time_input=hour_textfield,
                                                                                max_time_input=minutes_textfield,
                                                                                save_button=save_button_time)]),

                     await self.gui_program.diver_castom(),  # Горизонтальная линия

                     ft.Row([await LinkInputRowBuilder().compose_link_input_row(link_input=limits,
                                                                                save_button=save_button_limit),
                             await LinkInputRowBuilder().compose_link_input_row(link_input=link_entry_field,
                                                                                save_button=save_button), ]),

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

    async def add_user_test(self, client, username_group, username):
        try:
            await self.app_logger.log_and_display(message=f"Попытка приглашения {username} в группу {username_group}.")
            await client.connect()

            # Выполняем приглашение
            await client(InviteToChannelRequest(username_group, [username]))
            await self.app_logger.log_and_display(
                message=f"✅  Участник {username} добавлен, если не состоит в чате {username_group}. Спим от {TIME_INVITING_1} до {TIME_INVITING_2}")
            await self.utils.record_inviting_results(time_range_1=TIME_INVITING_1, time_range_2=TIME_INVITING_2,
                                                     username=username)
        except UserChannelsTooMuchError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["user_channels_too_much"])
            await self.utils.record_inviting_results(time_range_1=TIME_INVITING_1, time_range_2=TIME_INVITING_2,
                                                     username=username)
        except (ChannelPrivateError, TypeNotFoundError, AuthKeyDuplicatedError, UserBannedInChannelError,
                SessionRevokedError):
            await self.app_logger.log_and_display(
                message=translations["ru"]["errors"]["invalid_auth_session_terminated"])
            await self.utils.record_and_interrupt(time_range_1=TIME_INVITING_1, time_range_2=TIME_INVITING_2)
            await client.disconnect()
        except UserNotMutualContactError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["user_not_mutual_contact"])
            await self.utils.record_inviting_results(time_range_1=TIME_INVITING_1, time_range_2=TIME_INVITING_2,
                                                     username=username)
        except (UserKickedError, UserDeactivatedBanError):
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["user_kicked_or_banned"])
            await self.utils.record_inviting_results(time_range_1=TIME_INVITING_1, time_range_2=TIME_INVITING_2,
                                                     username=username)
        except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["invalid_username"])
            await self.utils.record_inviting_results(time_range_1=TIME_INVITING_1, time_range_2=TIME_INVITING_2,
                                                     username=username)
        except ChatAdminRequiredError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["admin_rights_required"])
            await self.utils.record_inviting_results(time_range_1=TIME_INVITING_1, time_range_2=TIME_INVITING_2,
                                                     username=username)
        except UserPrivacyRestrictedError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["user_privacy_restricted"])
            await self.utils.record_inviting_results(time_range_1=TIME_INVITING_1, time_range_2=TIME_INVITING_2,
                                                     username=username)
        except BotGroupsBlockedError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["bot_group_blocked"])
            await self.utils.record_inviting_results(time_range_1=TIME_INVITING_1, time_range_2=TIME_INVITING_2,
                                                     username=username)
        except (TypeError, UnboundLocalError):
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["type_or_scope"])
        except BadRequestError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["chat_member_add_failed"])

        # Ошибка инвайтинга прерываем работу
        except ChatWriteForbiddenError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["chat_write_forbidden"])
            await self.utils.record_inviting_results(time_range_1=TIME_INVITING_1, time_range_2=TIME_INVITING_2,
                                                     username=username)
            await client.disconnect()  # Прерываем работу и меняем аккаунт
        except InviteRequestSentError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["invite_request_sent"])
            await self.utils.record_inviting_results(time_range_1=TIME_INVITING_1, time_range_2=TIME_INVITING_2,
                                                     username=username)
            await client.disconnect()  # Прерываем работу и меняем аккаунт
        except FloodWaitError as e:
            await self.app_logger.log_and_display(message=f"{translations["ru"]["errors"]["flood_wait"]}{e}",
                                                  level="error")
            await self.utils.record_and_interrupt(time_range_1=TIME_INVITING_1, time_range_2=TIME_INVITING_2)
            await client.disconnect()  # Прерываем работу и меняем аккаунт
        except AuthKeyUnregisteredError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["auth_key_unregistered"])
            await self.utils.record_and_interrupt(time_range_1=TIME_INVITING_1, time_range_2=TIME_INVITING_2)
            await client.disconnect()
        except PeerFloodError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["peer_flood"], level="error")
            await self.utils.record_and_interrupt(time_range_1=TIME_INVITING_1, time_range_2=TIME_INVITING_2)
            await client.disconnect()  # Прерываем работу и меняем аккаунт
