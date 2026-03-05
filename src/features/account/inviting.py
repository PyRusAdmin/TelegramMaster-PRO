# -*- coding: utf-8 -*-
import asyncio
import datetime as dt

import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from scheduler.asyncio import Scheduler
from telethon import TelegramClient
from telethon.errors import (
    AuthKeyDuplicatedError, ChannelPrivateError, SessionRevokedError, TypeNotFoundError, UserBannedInChannelError,
    UserChannelsTooMuchError, UserNotMutualContactError, UserKickedError, UserDeactivatedBanError, UsernameInvalidError,
    UsernameNotOccupiedError, UserIdInvalidError, ChatAdminRequiredError, UserPrivacyRestrictedError,
    BotGroupsBlockedError, BadRequestError, ChatWriteForbiddenError, InviteRequestSentError, FloodWaitError,
    AuthKeyUnregisteredError, PeerFloodError
)
from telethon.tl.functions.channels import InviteToChannelRequest

from src.core.configs import width_tvo_input, width_one_input, window_width, BUTTON_HEIGHT
from src.core.database.account import getting_account
from src.core.database.database import select_records_with_limit, get_links_inviting, save_links_inviting
from src.core.utils import Utils
from src.features.account.connect import TGConnect
from src.features.account.subscribe import Subscribe
from src.features.account.subscribe_unsubscribe import SubscribeUnsubscribeTelegram
from src.features.account.switch_controller import ToggleController
from src.gui.gui import AppLogger, list_view
from src.gui.gui_elements import GUIProgram
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


async def load_and_validate_users(app_logger, gui_program, page, limit, session_string, page_go, action_text):
    """
    Загружает всех пользователей для (инвайтинга, рассылки сообщений) и проверяет наличие данных.
    Возвращает список пользователей или None, если загрузка не удалась.
    """
    # Получаем ВЕСЬ список пользователей для (инвайтинга, рассылки сообщений)
    all_usernames = await select_records_with_limit(limit=None, app_logger=app_logger)

    if not all_usernames:
        await app_logger.log_and_display(
            message=f"В таблице members нет пользователей для {action_text}."
        )
        await gui_program.show_notification(  # ✅ Показываем уведомление пользователю
            message=f"🔚 Нет пользователей для {action_text}"
        )
        page.go(page_go)
        return None

    await app_logger.log_and_display(
        message=f"Всего пользователей для {action_text}: {len(all_usernames)}\n"
                f"Лимит на аккаунт: {limit if limit else 'не установлен'}\n"
                f"Количество аккаунтов: {len(session_string)}"
    )

    return all_usernames


class InvitingToAGroup:

    def __init__(self, page: ft.Page):
        """
        Инициализация класса для инвайтинга пользователей в группы Telegram.

        :param page: Страница интерфейса Flet для отображения элементов управления
        """
        self.page = page
        self.scheduler = Scheduler()  # Создаем экземпляр планировщика
        self.links_inviting = get_links_inviting()  # Получаем список ссылок на группы для инвайтинга из базы данных
        self.app_logger = AppLogger(page=page)  # Инициализация экземпляра класса AppLogger (Логирование)
        self.connect = TGConnect(page=page)  # Инициализация экземпляра класса TGConnect (Подключение)
        self.utils = Utils(page=page)  # Инициализация экземпляра класса Utils (Утилиты)
        self.subscribe = Subscribe(page=page)  # Инициализация экземпляра класса Subscribe (Подписка)
        self.gui_program = GUIProgram(page=page)  # Инициализация экземпляра класса GUIProgram (GUI)
        self.session_string = getting_account()  # Получаем строку сессии из файла базы данных
        self.subscribe_unsubscribe_telegram = SubscribeUnsubscribeTelegram(page=page)

    async def inviting_menu(self):
        """
        Отображает меню инвайтинга с настройками и опциями.

        :return: None
        """
        list_view.controls.clear()  # ✅ Очистка логов перед новым запуском

        self.page.update()  # обновляем страницу, чтобы сразу показать ListView 🔄

        await self.app_logger.log_and_display(
            message=(
                f"Всего подключенных аккаунтов: {len(self.session_string)}\n"
            )
        )
        # Отображение информации о настройках инвайтинга
        await select_records_with_limit(limit=None, app_logger=self.app_logger)

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
                await self.gui_program.show_notification(  # ✅ Показываем уведомление пользователю
                    message="Время должно быть больше 0"
                )
                self.page.go("/inviting")
                return

            time_inviting_2 = TIME_INVITING_2.value
            if time_inviting_2 == "":
                await self.gui_program.show_notification(  # ✅ Показываем уведомление пользователю
                    message="Время должно быть больше 0"
                )
                self.page.go("/inviting")
                return

            start = await self.app_logger.start_time()
            self.page.update()

            limit = get_limit(limits)  # Получаем лимит введенный пользователем

            all_usernames = await load_and_validate_users(
                app_logger=self.app_logger, gui_program=self.gui_program, page=self.page, limit=limit,
                session_string=self.session_string, page_go="/inviting", action_text="Инвайтинга"
            )

            # 🔄 Индекс для отслеживания текущей позиции в списке пользователей
            current_user_index = 0

            for account_number, session_name in enumerate(self.session_string, 1):
                # Проверяем, остались ли пользователи для инвайтинга
                if current_user_index >= len(all_usernames):
                    await self.app_logger.log_and_display(
                        message="✅ Все пользователи обработаны, инвайтинг завершен"
                    )
                    break

                client: TelegramClient = await self.connect.client_connect_string_session(
                    session_name=session_name
                )

                if client is None:
                    await self.app_logger.log_and_display(
                        message=f"⚠️ Пропускаем сессию {session_name} - не удалось подключиться."
                    )
                    continue  # Переходим к следующему аккаунту

                # 📊 Определяем количество пользователей для текущего аккаунта
                if limit:
                    # Если установлен лимит - берем N пользователей
                    users_for_this_account = all_usernames[current_user_index:current_user_index + limit]
                    current_user_index += limit
                else:
                    # Если лимит не установлен - распределяем поровну между аккаунтами
                    remaining_accounts = len(self.session_string) - account_number + 1
                    remaining_users = len(all_usernames) - current_user_index
                    users_per_account = remaining_users // remaining_accounts

                    users_for_this_account = all_usernames[current_user_index:current_user_index + users_per_account]
                    current_user_index += users_per_account

                if not users_for_this_account:
                    await self.app_logger.log_and_display(
                        message=f"⚠️ Для аккаунта {session_name} нет пользователей"
                    )
                    continue

                await self.app_logger.log_and_display(
                    message=f"🔹 Аккаунт #{account_number}: {session_name}\n"
                            f"   Будет обработано пользователей: {len(users_for_this_account)}\n"
                            f"   Диапазон: {current_user_index - len(users_for_this_account) + 1}-{current_user_index}"
                )

                # Подписываемся на группы
                await self.subscribe.subscribe_to_group_or_channel(client=client, groups=links)
                await self.app_logger.log_and_display(message=f"✅ Подписка на группы: {links}")

                # 🎯 Инвайтим ТОЛЬКО пользователей для этого аккаунта
                for idx, username in enumerate(users_for_this_account, 1):
                    await self.app_logger.log_and_display(
                        message=f"   [{idx}/{len(users_for_this_account)}] Приглашение: {username}"
                    )

                    try:
                        await self.add_user_test(
                            client=client,
                            username_group=links,
                            username=username,
                            time_inviting_1=TIME_INVITING_1.value,
                            time_inviting_2=TIME_INVITING_2.value
                        )
                    except KeyboardInterrupt:
                        await self.app_logger.log_and_display(
                            message=translations["ru"]["errors"]["script_stopped"],
                            level="error"
                        )
                        return  # Полностью прерываем работу

                    except ConnectionError as e:
                        await self.app_logger.log_and_display(
                            message=f"⚠️ Клиент отключен: {str(e)}. Переход к следующему аккаунту.",
                            level="warning"
                        )
                        break  # Прерываем цикл обработки пользователей для этого аккаунта

                # Отписываемся от группы после завершения работы аккаунта
                await self.subscribe_unsubscribe_telegram.unsubscribe_from_the_group(
                    client=client,
                    group_link=links
                )
                await self.app_logger.log_and_display(
                    message=f"✅ Аккаунт {session_name} завершил работу. "
                            f"Приглашено: {len(users_for_this_account)} пользователей"
                )
                await client.disconnect()

            await self.app_logger.log_and_display(
                message=f"🎉 Инвайтинг полностью завершен!\n"
                        f"   Всего обработано: {current_user_index} из {len(all_usernames)} пользователей"
            )
            await self.app_logger.end_time(start=start)
            await self.gui_program.show_notification(  # ✅ Показываем уведомление пользователю
                message="🔚 Конец инвайтинга"
            )
            self.page.go("/inviting")

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

            except Exception as e:
                logger.exception(e)

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

            except Exception as e:
                logger.exception(e)

        async def launching_invite_every_day_certain_time(_):
            """
            🚀 Запускает процесс инвайтинга групп и отображает статус в интерфейсе.
            📅 Инвайтинг каждый день. Запуск приглашения участников каждый день в определенное время, выбранное пользователем.
            """
            try:
                async def general_invitation_group_scheduler():
                    await general_invitation_to_the_group(_)

                await self.app_logger.log_and_display(
                    message=f"Скрипт будет запускаться каждый день в {hour.value}:{minutes.value}"
                )
                self.scheduler.daily(dt.time(hour=int(hour.value), minute=int(minutes.value)),
                                     general_invitation_group_scheduler)
                while True:
                    await asyncio.sleep(1)

            except Exception as e:
                logger.exception(e)

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

        # Создаем выпадающий список с названиями групп, для последующего выбора и инвайтинга
        dropdown = ft.Dropdown(
            width=window_width,
            options=[ft.DropdownOption(link) for link in self.links_inviting],
            autofocus=True
        )

        """
        Пользователь вводит время задержки между инвайтингом (приглашениями в группу)
        """

        # Два поля ввода для времени и кнопка сохранить
        TIME_INVITING_1, TIME_INVITING_2 = await self.gui_program.build_time_inputs_with_save_button(
            label_min="Мин. задержка (сек)",
            label_max="Макс. задержка (сек)",
            width=width_tvo_input
        )
        # Два поля ввода для времени и кнопка сохранить
        hour, minutes = await self.gui_program.build_time_inputs_with_save_button(
            label_min="Час запуска (0–23)",
            label_max="Минуты (0–59)",
            width=width_tvo_input
        )

        """
        Пользователь вводит лимит на аккаунт и вводит ссылку для инвайтинга, нечего сохранять не нужно, что бы не 
        усложнять проект.
        """

        # Поле ввода, для ссылок для инвайтинга
        limits = await self.gui_program.build_link_input_with_save_button(
            label_text="Введите лимит на аккаунт",
            width=width_one_input
        )
        link_entry_field = await self.gui_program.build_link_input_with_save_button(
            label_text="Введите ссылку на группу для инвайтинга",
            width=width_one_input
        )

        # Кнопки-переключатели
        inviting_switch = ft.CupertinoSwitch(
            label=translations["ru"]["inviting_menu"]["inviting"],
            value=False,
            disabled=True
        )
        inviting_1_time_per_hour_switch = ft.CupertinoSwitch(
            label=translations["ru"]["inviting_menu"]["invitation_1_time_per_hour"],
            value=False,
            disabled=True
        )
        inviting_at_a_certain_time_switch = ft.CupertinoSwitch(
            label=translations["ru"]["inviting_menu"]["invitation_at_a_certain_time"],
            value=False,
            disabled=True
        )
        inviting_every_day_switch = ft.CupertinoSwitch(label=translations["ru"]["inviting_menu"]["inviting_every_day"],
                                                       value=False, disabled=True)
        ToggleController(
            inviting_switch=inviting_switch,
            inviting_1_time_per_hour_switch=inviting_1_time_per_hour_switch,
            inviting_at_a_certain_time_switch=inviting_at_a_certain_time_switch,
            inviting_every_day_switch=inviting_every_day_switch
        ).element_handler_inviting(self.page)

        start_inviting = await self.gui_program.gui_button(
            text=translations["ru"]["buttons"]["start_inviting"],
            route=start_inviting_grup
        )

        inviting_switch.disabled = False
        inviting_1_time_per_hour_switch.disabled = False
        inviting_at_a_certain_time_switch.disabled = False
        inviting_every_day_switch.disabled = False
        start_inviting.disabled = False

        self.page.views.append(
            ft.View(
                route="/inviting",
                appbar=await self.gui_program.key_app_bar(),  # Кнопка назад
                controls=[
                    await self.gui_program.create_gradient_text(
                        text=translations["ru"]["inviting_menu"]["inviting"]
                    ),
                    list_view,  # Отображение логов 📝
                    ft.Row(
                        [
                            await self.gui_program.compose_time_input_row(
                                min_time_input=TIME_INVITING_1,
                                max_time_input=TIME_INVITING_2,
                            ),
                            await self.gui_program.compose_time_input_row(
                                min_time_input=hour,
                                max_time_input=minutes
                            )
                        ]
                    ),
                    await self.gui_program.diver_castom(),  # Горизонтальная линия
                    ft.Row(
                        [
                            await self.gui_program.compose_link_input_row(
                                link_input=limits,
                            ),
                            await self.gui_program.compose_link_input_row(
                                link_input=link_entry_field,
                            ),
                        ]
                    ),
                    await self.gui_program.diver_castom(),  # Горизонтальная линия
                    ft.Text(value="📂 Выберите группу для инвайтинга"),  # Выбор группы для инвайтинга
                    dropdown,  # Выпадающий список с названиями групп
                    await self.gui_program.diver_castom(),  # Горизонтальная линия
                    ft.Row(
                        [
                            inviting_switch,
                            inviting_1_time_per_hour_switch,
                            inviting_at_a_certain_time_switch,
                            inviting_every_day_switch
                        ]
                    ),
                    ft.Column(  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                        controls=[
                            ft.Row(
                                expand=True,
                                controls=[start_inviting]
                            )
                        ]
                    )
                ]
            )
        )
        self.page.update()  # обновляем страницу после добавления элементов управления 🔄

    async def add_user_test(self, client, username_group, username, time_inviting_1, time_inviting_2):
        """
        Метод для приглашения участников в группу.

        :param client: Экземпляр клиента Telegram
        :param username_group: Ссылка на группу
        :param username: Имя пользователя (username)
        :param time_inviting_1: Начальное время ожидания в секундах
        :param time_inviting_2: Конечное время ожидания в секундах
        :return: None
        """
        try:
            await self.app_logger.log_and_display(message=f"Попытка приглашения {username} в группу {username_group}.")

            # Выполняем приглашение
            await client(InviteToChannelRequest(username_group, [username]))
            await self.app_logger.log_and_display(
                message=f"✅  Участник {username} добавлен, если не состоит в чате {username_group}. Спим от {time_inviting_1} до {time_inviting_2}")
            await self.utils.record_inviting_results(
                time_range_1=time_inviting_1,
                time_range_2=time_inviting_2,
                username=username
            )
        except UserChannelsTooMuchError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["user_channels_too_much"])
            await self.utils.record_inviting_results(
                time_range_1=time_inviting_1,
                time_range_2=time_inviting_2,
                username=username
            )

        except SessionRevokedError as e:
            await self.app_logger.log_and_display(
                message=translations["ru"]["errors"]["invalid_auth_session_terminated"]
            )
            await self.utils.random_dream(
                min_seconds=time_inviting_1,
                max_seconds=time_inviting_2
            )
            logger.error(e)
            raise ConnectionError("Клиент отключен из-за ошибки сеанса")

        except UserBannedInChannelError as e:
            await self.app_logger.log_and_display(
                message=translations["ru"]["errors"]["invalid_auth_session_terminated"]
            )
            await self.utils.random_dream(
                min_seconds=time_inviting_1,
                max_seconds=time_inviting_2
            )
            logger.error(e)
            raise ConnectionError("Клиент отключен из-за ошибки сеанса")

        except AuthKeyDuplicatedError as e:
            await self.app_logger.log_and_display(
                message=translations["ru"]["errors"]["invalid_auth_session_terminated"]
            )
            await self.utils.random_dream(
                min_seconds=time_inviting_1,
                max_seconds=time_inviting_2
            )
            logger.error(e)
            raise ConnectionError("Клиент отключен из-за ошибки сеанса")

        except TypeNotFoundError as e:
            await self.app_logger.log_and_display(
                message=translations["ru"]["errors"]["invalid_auth_session_terminated"]
            )
            await self.utils.random_dream(
                min_seconds=time_inviting_1,
                max_seconds=time_inviting_2
            )
            logger.error(e)
            raise ConnectionError("Клиент отключен из-за ошибки сеанса")

        except ChannelPrivateError as e:
            await self.app_logger.log_and_display(
                message=translations["ru"]["errors"]["invalid_auth_session_terminated"]
            )
            await self.utils.random_dream(
                min_seconds=time_inviting_1,
                max_seconds=time_inviting_2
            )
            logger.error(e)
            raise ConnectionError("Клиент отключен из-за ошибки сеанса")

        except UserNotMutualContactError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["user_not_mutual_contact"])
            await self.utils.record_inviting_results(
                time_range_1=time_inviting_1,
                time_range_2=time_inviting_2,
                username=username
            )
        except (UserKickedError, UserDeactivatedBanError):
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["user_kicked_or_banned"])
            await self.utils.record_inviting_results(
                time_range_1=time_inviting_1,
                time_range_2=time_inviting_2,
                username=username
            )
        except (UserIdInvalidError, UsernameNotOccupiedError, ValueError, UsernameInvalidError):
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["invalid_username"])
            await self.utils.record_inviting_results(
                time_range_1=time_inviting_1,
                time_range_2=time_inviting_2,
                username=username
            )
        except ChatAdminRequiredError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["admin_rights_required"])
            await self.utils.record_inviting_results(
                time_range_1=time_inviting_1,
                time_range_2=time_inviting_2,
                username=username
            )
        except UserPrivacyRestrictedError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["user_privacy_restricted"])
            await self.utils.record_inviting_results(
                time_range_1=time_inviting_1,
                time_range_2=time_inviting_2,
                username=username
            )
        except BotGroupsBlockedError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["bot_group_blocked"])
            await self.utils.record_inviting_results(
                time_range_1=time_inviting_1,
                time_range_2=time_inviting_2,
                username=username)
        except (TypeError, UnboundLocalError):
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["type_or_scope"])
        except BadRequestError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["chat_member_add_failed"])

        # Ошибка инвайтинга прерываем работу
        except ChatWriteForbiddenError:
            await self.app_logger.log_and_display(message=translations["ru"]["errors"]["chat_write_forbidden"])
            await self.utils.record_inviting_results(
                time_range_1=time_inviting_1,
                time_range_2=time_inviting_2,
                username=username
            )
            raise ConnectionError("Клиент отключен из-за того, что запись в чат запрещена")
        except InviteRequestSentError:
            await self.app_logger.log_and_display(
                message=translations["ru"]["errors"]["invite_request_sent"]
            )
            await self.utils.record_inviting_results(
                time_range_1=time_inviting_1,
                time_range_2=time_inviting_2,
                username=username
            )
            raise ConnectionError("Клиент отключен из-за отправки запроса на приглашение")
        except FloodWaitError as e:
            await self.app_logger.log_and_display(
                message=f"{translations["ru"]["errors"]["flood_wait"]}{e}",
                level="error"
            )
            raise ConnectionError("Клиент отключен из-за ограничения Flood Wait")  # ⬅️ НОВОЕ!
        except AuthKeyUnregisteredError:
            await self.app_logger.log_and_display(
                message=translations["ru"]["errors"]["auth_key_unregistered"]
            )
            await self.utils.random_dream(
                min_seconds=time_inviting_1,
                max_seconds=time_inviting_2
            )
            raise ConnectionError("Клиент отключён из-за незарегистрированного ключа аутентификации")
        except PeerFloodError:
            await self.app_logger.log_and_display(
                message=translations["ru"]["errors"]["peer_flood"],
                level="error"
            )
            await self.utils.random_dream(
                min_seconds=time_inviting_1,
                max_seconds=time_inviting_2
            )
            raise ConnectionError("Клиент отключен из-за флуда узла")

        except Exception as e:
            logger.exception(e)
