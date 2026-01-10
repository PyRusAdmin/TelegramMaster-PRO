# -*- coding: utf-8 -*-
import asyncio
import csv
import os
import os.path
import flet as ft  # Импортируем библиотеку flet
from loguru import logger
from telethon.errors import (
    ApiIdInvalidError, AuthKeyDuplicatedError, AuthKeyNotFound, AuthKeyUnregisteredError, PasswordHashInvalidError,
    PhoneNumberBannedError, SessionPasswordNeededError, TimedOutError, TypeNotFoundError, UserDeactivatedBanError,
    YouBlockedUserError, SessionRevokedError, PhoneCodeInvalidError
)
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from thefuzz import fuzz

from src.gui.buttons import menu_button_fun
from src.core.config.configs import BUTTON_HEIGHT, WIDTH_WIDE_BUTTON, api_id, api_hash
from src.core.database.account import (
    getting_account, write_account_to_db, delete_account_from_db, update_phone_by_session
)
from src.core.utils import Utils
from src.features.proxy.checking_proxy import Proxy
from src.gui.gui import AppLogger, list_view
from src.gui.gui_elements import GUIProgram
from src.gui.notification import show_notification
from src.locales.translations_loader import translations


# Выбор файла
# https://docs.flet.dev/services/filepicker/#flet.FilePicker

class TGConnect:

    def __init__(self, page: ft.Page):
        self.page = page  # Страница интерфейса Flet для отображения элементов управления.
        self.app_logger = AppLogger(page)
        self.utils = Utils(page=page)
        self.proxy = Proxy(page=page)
        self.gui_program = GUIProgram()
        self.session_string = getting_account()  # Получаем строку сессии из файла базы данных
        self.pick_files_dialog: ft.FilePicker | None = None

    async def check_menu(self):
        """
        Меню 🔍 Проверка аккаунтов
        """

        list_view.controls.clear()  # Очистка list_view для отображения новых элементов и недопущения дублирования

        async def check_for_spam(_) -> None:
            """
            Проверка аккаунта на спам через @SpamBot
            """
            try:
                start = await self.app_logger.start_time()  # Запуск таймера
                session_string = getting_account()
                for session_name in session_string:
                    client: TelegramClient = await self.client_connect_string_session(session_name=session_name)
                    try:
                        await client.send_message(entity='SpamBot',
                                                  message='/start')  # Находим спам бот, и вводим команду /start
                        for message in await client.get_messages('SpamBot'):
                            await self.app_logger.log_and_display(message=f"{session_name} {message.message}")
                            similarity_ratio_ru: int = fuzz.ratio(f"{message.message}",
                                                                  "Очень жаль, что Вы с этим столкнулись. К сожалению, "
                                                                  "иногда наша антиспам-система излишне сурово реагирует на "
                                                                  "некоторые действия. Если Вы считаете, что Ваш аккаунт "
                                                                  "ограничен по ошибке, пожалуйста, сообщите об этом нашим "
                                                                  "модераторам. Пока действуют ограничения, Вы не сможете "
                                                                  "писать тем, кто не сохранил Ваш номер в список контактов, "
                                                                  "а также приглашать таких пользователей в группы или каналы. "
                                                                  "Если пользователь написал Вам первым, Вы сможете ответить, "
                                                                  "несмотря на ограничения.")
                            if similarity_ratio_ru >= 97:
                                await self.app_logger.log_and_display(message=f"⛔ Аккаунт заблокирован")
                                await client.disconnect()  # Отключаемся от аккаунта, для освобождения процесса session файла.
                                await self.app_logger.log_and_display(
                                    message=f"Проверка аккаунтов через SpamBot. {session_name}: {message.message}")

                            similarity_ratio_en: int = fuzz.ratio(f"{message.message}",
                                                                  "I’m very sorry that you had to contact me. Unfortunately, "
                                                                  "some account_actions can trigger a harsh response from our "
                                                                  "anti-spam systems. If you think your account was limited by "
                                                                  "mistake, you can submit a complaint to our moderators. While "
                                                                  "the account is limited, you will not be able to send messages "
                                                                  "to people who do not have your number in their phone contacts "
                                                                  "or add them to groups and channels. Of course, when people "
                                                                  "contact you first, you can always reply to them.")
                            if similarity_ratio_en >= 97:
                                await self.app_logger.log_and_display(message=f"⛔ Аккаунт заблокирован")
                                await client.disconnect()  # Отключаемся от аккаунта, для освобождения процесса session файла.
                                await self.app_logger.log_and_display(
                                    message=f"Проверка аккаунтов через SpamBot. {session_name}: {message.message}"
                                )
                                # Перенос Telegram аккаунта в папку banned, если Telegram аккаунт в бане
                                await self.app_logger.log_and_display(
                                    message=f"{session_name}"
                                )
                            await self.app_logger.log_and_display(
                                message=f"Проверка аккаунтов через SpamBot. {session_name}: {message.message}"
                            )
                            await client.disconnect()  # Отключаемся от аккаунта, для освобождения процесса session файла.

                    except (AttributeError, AuthKeyUnregisteredError, YouBlockedUserError) as e:
                        await self.app_logger.log_and_display(message=f"❌ Ошибка: {e}")

                    except SessionRevokedError as e:
                        await self.handle_banned_account(telegram_client=client, session_name=session_name, exception=e)

                await self.app_logger.end_time(start)
                await show_notification(
                    page=self.page,
                    message="🔚 Проверка аккаунтов завершена"
                )
            except Exception as error:
                logger.exception(error)

        async def validation_check(_) -> None:
            """
            Проверяет все аккаунты Telegram из базы данных user_data/software_database.db.
            """
            try:
                start = await self.app_logger.start_time()  # Измеряет начало старта функции
                await self.proxy.checking_the_proxy_for_work()  # Проверка proxy
                session_string = getting_account()
                for session_name in session_string:
                    await self.app_logger.log_and_display(message=f"⚠️ Проверяемый аккаунт: {session_name}")
                    # Проверка аккаунтов
                    await self.verify_account(session_name=session_name)
                await self.app_logger.log_and_display(message=f"Окончание проверки аккаунтов Telegram 📁")
                await self.app_logger.end_time(start)
                await show_notification(self.page, "🔚 Проверка аккаунтов завершена")
            except Exception as error:
                logger.exception(error)

        async def renaming_accounts(_):
            """
            Получает информацию о Telegram аккаунте.

            """
            try:
                start = await self.app_logger.start_time()
                await self.proxy.checking_the_proxy_for_work()  # Проверка proxy
                # Сканирование каталога с аккаунтами
                for session_name in self.session_string:  # Перебор всех сессий
                    await self.app_logger.log_and_display(message=f"⚠️ Переименовываемый аккаунт: {session_name}")
                    # Переименовывание аккаунтов
                    client = await self.client_connect_string_session(session_name=session_name)
                    try:
                        me = await client.get_me()
                        await update_phone_by_session(
                            session_string=session_name,
                            new_phone=me.phone,
                            app_logger=self.app_logger
                        )
                    except AttributeError:  # Если в get_me приходит NoneType (None)
                        pass
                    except TypeNotFoundError as e:
                        await client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
                        await self.app_logger.log_and_display(
                            message=f"⛔ Битый файл или аккаунт banned: {session_name}.session. Возможно, запущен под другим IP")
                        await self.handle_banned_account(telegram_client=client, session_name=session_name, exception=e)
                    except AuthKeyUnregisteredError as e:
                        await client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
                        await self.app_logger.log_and_display(
                            message=translations["ru"]["errors"]["auth_key_unregistered"])
                        await self.handle_banned_account(telegram_client=client, session_name=session_name, exception=e)

                await self.app_logger.end_time(start)
                await show_notification(page=self.page, message="🔚 Проверка аккаунтов завершена")
            except Exception as error:
                logger.exception(error)

        async def full_verification(_) -> None:
            """
            Выполняет полную проверку аккаунтов.
            :param _: Ссылка на объект, переданный в качестве параметра.
            :return: None
            """
            try:
                start = await self.app_logger.start_time()
                await validation_check(_)  # Проверка валидности аккаунтов
                await renaming_accounts(_)  # Переименование аккаунтов
                await check_for_spam(_)  # Проверка на спам ботов
                await self.app_logger.end_time(start)
                await show_notification(page=self.page, message="🔚 Проверка аккаунтов завершена")
            except Exception as error:
                logger.exception(error)

        self.page.views.append(
            ft.View(
                route="/account_verification_menu",  # Маршрут для этого представления
                appbar=await self.gui_program.key_app_bar(page=self.page),  # Кнопка назад
                controls=[
                    ft.Text(
                        spans=[
                            ft.TextSpan(
                                translations["ru"]["menu"]["account_check"],
                                ft.TextStyle(
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    foreground=ft.Paint(
                                        gradient=ft.PaintLinearGradient(
                                            (0, 20),
                                            (150, 20),
                                            [
                                                ft.Colors.PINK,
                                                ft.Colors.PURPLE
                                            ]
                                        )
                                    ),
                                ),
                            ),
                        ],
                    ),
                    list_view,
                    ft.Column(
                        [  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                            # 🤖 Проверка через спам бот
                            ft.Button(
                                content=translations["ru"]["account_verification"]["spam_check"],
                                width=WIDTH_WIDE_BUTTON,
                                height=BUTTON_HEIGHT,
                                on_click=check_for_spam
                            ),
                            # ✅ Проверка на валидность
                            ft.Button(
                                content=translations["ru"]["account_verification"]["validation"],
                                width=WIDTH_WIDE_BUTTON,
                                height=BUTTON_HEIGHT,
                                on_click=validation_check
                            ),
                            # ✏️ Переименование аккаунтов
                            ft.Button(
                                content=translations["ru"]["account_verification"]["renaming"],
                                width=WIDTH_WIDE_BUTTON,
                                height=BUTTON_HEIGHT,
                                on_click=renaming_accounts
                            ),
                            # 🔍 Полная проверка
                            ft.Button(
                                content=translations["ru"]["account_verification"]["full_verification"],
                                width=WIDTH_WIDE_BUTTON,
                                height=BUTTON_HEIGHT,
                                on_click=full_verification
                            ),
                        ]
                    )
                ]))

    async def client_connect_string_session(self, session_name: str) -> TelegramClient | None:
        """
        Подключение к Telegram аккаунту через StringSession

        :param session_name: Имя аккаунта для подключения (файл .session)
        :return: Клиент Telegram или None, если подключение не удалось
        """
        # Создаем клиент, используя StringSession и вашу строку
        client = TelegramClient(
            StringSession(session_name),
            api_id=api_id,
            api_hash=api_hash,
            proxy=self.proxy.reading_proxy_data_from_the_database(),
            system_version="4.16.30-vxCUSTOM"
        )
        try:
            await client.connect()

            if not await client.is_user_authorized():
                logger.error("❌ Сессия недействительна или аккаунт не авторизован!")
                await self.write_csv(data=session_name)
                try:
                    await client.disconnect()
                except ValueError:
                    logger.error("❌ Сессия недействительна или аккаунт не авторизован!")
                return None  # Не возвращаем клиента

            me = await client.get_me()
            phone = me.phone or ""
            logger.info(f"🧾 Аккаунт: | ID: {me.id} | Phone: {phone}")
            await self.app_logger.log_and_display(message=f"🧾 Аккаунт: | ID: {me.id} | Phone: {phone}")
            return client

        except AuthKeyDuplicatedError:
            logger.error(
                "❌ AuthKeyDuplicatedError: Повторный ввод ключа авторизации (на данный момент сеесия используется в другом месте)")
            await client.disconnect()
            return None  # Не возвращаем клиента

    async def write_csv(self, data):
        """
        Запись данных в CSV файл. (Аккаунты Telegram)
        Все данные будут записаны в одну строку.
        :param data: Список значений (например, список аккаунтов)
        :return:
        """
        with open('file.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Записываем данные как одну строку с одним элементом
            writer.writerow([data])  # Оборачиваем в список, чтобы строка не разбилась по символам

    async def read_csv(self):
        """
        Чтение данных из CSV файла. (Аккаунты Telegram)
        :return:
        """
        with open('file.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                print(row)  # каждая строка — список значений

    async def verify_account(self, session_name) -> None:
        """
        Проверяет и сортирует аккаунты.

        :param session_name: Имя аккаунта для проверки
        :return: None
        """
        try:
            await self.app_logger.log_and_display(message=f"Проверка аккаунта {session_name}")
            client: TelegramClient = await self.client_connect_string_session(session_name=session_name)
            try:
                if not await client.is_user_authorized():  # Если аккаунт не авторизирован
                    await client.disconnect()
                    await asyncio.sleep(5)

                    await delete_account_from_db(session_string=session_name, app_logger=self.app_logger)
                    await self.write_csv(data=session_name)

                else:
                    await self.app_logger.log_and_display(message=f"Аккаунт {session_name} авторизован")
                    await client.disconnect()  # Отключаемся после проверки
            except (PhoneNumberBannedError, UserDeactivatedBanError, AuthKeyNotFound,
                    AuthKeyUnregisteredError, AuthKeyDuplicatedError) as e:

                await delete_account_from_db(session_string=session_name, app_logger=self.app_logger)
            except TimedOutError as error:
                await self.app_logger.log_and_display(message=f"❌ Ошибка таймаута: {error}")
                await asyncio.sleep(2)
            except AttributeError:
                pass
        except Exception as error:
            logger.exception(error)

    async def handle_banned_account(self, telegram_client, session_name, exception):
        """
        Обработка banned аккаунтов.
        telegram_client.disconnect() - Отключение от Telegram.
        working_with_accounts() - Перемещение файла. Исходный путь к файлу - account_folder. Путь к новой папке,
        куда нужно переместить файл - new_account_folder

        :param telegram_client: Экземпляр клиента Telegram
        :param session_name: Имя аккаунта (session string)
        :param exception: Исключение, вызвавшее бан
        :return: None
        """
        await self.app_logger.log_and_display(message=f"⛔ Аккаунт banned: {session_name}. {str(exception)}")
        await telegram_client.disconnect()
        await delete_account_from_db(session_string=session_name, app_logger=self.app_logger)

    async def account_connection_menu(self):
        """
        Меню подключения аккаунтов (по телефону и по session)
        """

        list_view.controls.clear()

        # Создаем текстовый элемент и добавляем его на страницу
        phone_number = ft.TextField(label="Введите номер телефона:", multiline=False, max_lines=1)

        async def connecting_number_accounts(_) -> None:
            """Подключение аккаунта Telegram по номеру телефона"""
            phone_number_value = phone_number.value
            await self.app_logger.log_and_display(message=f"Номер телефона: {phone_number_value}")

            # Дальнейшая обработка после записи номера телефона
            client = TelegramClient(f"{phone_number_value}", api_id=api_id, api_hash=api_hash,
                                    system_version="4.16.30-vxCUSTOM",
                                    proxy=self.proxy.reading_proxy_data_from_the_database())
            await client.connect()  # Подключаемся к Telegram

            if not await client.is_user_authorized():
                await self.app_logger.log_and_display(message=f"Пользователь не авторизован")
                await client.send_code_request(phone_number_value)  # Отправка кода на телефон
                await asyncio.sleep(2)
                passww = ft.TextField(label="Введите код telegram:", multiline=True, max_lines=1)

                async def btn_click_code(_) -> None:
                    try:
                        await self.app_logger.log_and_display(message=f"Код telegram: {passww.value}")
                        await client.sign_in(phone_number_value, passww.value)  # Авторизация с кодом
                        client.disconnect()
                        self.page.go("/")  # Перенаправление в настройки, если 2FA не требуется
                        self.page.update()
                    except SessionPasswordNeededError:  # Если аккаунт защищен паролем, запрашиваем пароль
                        await self.app_logger.log_and_display(
                            message=translations["ru"]["errors"]["two_factor_required"])
                        pass_2fa = ft.TextField(label="Введите пароль telegram:", multiline=False, max_lines=1)

                        async def btn_click_password(_) -> None:
                            await self.app_logger.log_and_display(message=f"Пароль telegram: {pass_2fa.value}")
                            try:
                                await client.sign_in(password=pass_2fa.value)
                                await self.app_logger.log_and_display(message=f"Успешная авторизация.")
                                client.disconnect()
                                self.page.go("/")  # Изменение маршрута в представлении существующих настроек
                                self.page.update()
                            except PasswordHashInvalidError:
                                await self.app_logger.log_and_display(message=f"❌ Неверный пароль.")
                                await show_notification(self.page, f"⚠️ Неверный пароль. Попробуйте еще раз.")
                                self.page.go("/")  # Изменение маршрута в представлении существующих настроек

                        button_password = ft.Button(
                            content=translations["ru"]["buttons"]["done"],
                            width=WIDTH_WIDE_BUTTON,
                            height=BUTTON_HEIGHT,
                            on_click=btn_click_password
                        )  # Кнопка "Готово"
                        self.page.views.append(ft.View(controls=[pass_2fa, button_password]))
                        self.page.update()  # Обновляем страницу, чтобы интерфейс отобразился
                    except PhoneCodeInvalidError:
                        await self.app_logger.log_and_display(message=f"❌ Неверный код.")
                        await client.disconnect()  # Отключаемся от Telegram
                    except ApiIdInvalidError:
                        await self.app_logger.log_and_display(message=f"[!] Неверные API ID или API Hash.")
                        await client.disconnect()  # Отключаемся от Telegram
                    except Exception as error:
                        logger.exception(error)
                        await client.disconnect()  # Отключаемся от Telegram

                self.page.views.append(
                    ft.View(
                        controls=[
                            passww,
                            ft.Button(
                                content=translations["ru"]["buttons"]["done"],
                                width=WIDTH_WIDE_BUTTON,
                                height=BUTTON_HEIGHT,
                                on_click=btn_click_code
                            )
                        ]
                    )
                )  # Кнопка "Готово"
                self.page.update()  # Обновляем страницу, чтобы отобразился интерфейс для ввода кода
            self.page.update()

        # Поле для отображения выбранного файла
        selected_files = ft.Text(value="Session файл не выбран", size=12)

        async def handle_get_directory_path(e: ft.Event[ft.Button]):
            """
            Обработчик события выбора session файлов

            Открывает диалоговое окно для выбора session файлов и подключает их к базе данных.
            :param e: Событие нажатия на кнопку
            """
            try:
                # Открываем диалог выбора файлов
                file_picker = ft.FilePicker()
                files = await file_picker.pick_files(
                    allow_multiple=True,
                    allowed_extensions=["session"]
                )

                if not files:
                    selected_files.value = "Выбор файла отменен"
                    selected_files.update()
                    return

                # Обрабатываем каждый выбранный файл
                for file in files:
                    file_name = file.name
                    file_path = file.path

                    # Проверяем расширение файла
                    if not file_name.endswith(".session"):
                        await self.app_logger.log_and_display(
                            message=f"⚠️ Файл {file_name} не является session файлом, пропускаем"
                        )
                        continue

                    await self.app_logger.log_and_display(
                        message=f"📁 Обработка session файла: {file_name}"
                    )
                    selected_files.value = f"Обрабатывается: {file_name}"
                    selected_files.update()

                    # Получаем путь без расширения
                    session_path = os.path.splitext(file_path)[0]

                    # Создаем клиент с обычной сессией
                    client = TelegramClient(
                        session=session_path,
                        api_id=api_id,
                        api_hash=api_hash,
                        system_version="4.16.30-vxCUSTOM"
                    )

                    try:
                        await client.connect()

                        # Преобразуем в StringSession
                        session_string = StringSession.save(client.session)
                        await client.disconnect()

                        # Переподключаемся через StringSession
                        client = TelegramClient(
                            StringSession(session_string),
                            api_id=api_id,
                            api_hash=api_hash,
                            system_version="4.16.30-vxCUSTOM"
                        )

                        await client.connect()
                        me = await client.get_me()

                        if not me:
                            await show_notification(
                                page=self.page,
                                message=f"❌ Аккаунт {file_name} не валидный"
                            )
                            await self.app_logger.log_and_display(
                                message=f"❌ Аккаунт {file_name} не валидный"
                            )
                            await client.disconnect()
                            continue

                        phone = me.phone or ""
                        logger.info(f"🧾 Аккаунт: | ID: {me.id} | Phone: {phone}")
                        await self.app_logger.log_and_display(
                            message=f"✅ Аккаунт добавлен: | ID: {me.id} | Phone: {phone}"
                        )
                        # Записываем в базу данных
                        write_account_to_db(
                            session_string=session_string,
                            phone_number=phone
                        )
                        await client.disconnect()

                    except Exception as error:
                        logger.exception(f"Ошибка при обработке {file_name}: {error}")
                        await self.app_logger.log_and_display(
                            message=f"❌ Ошибка при обработке {file_name}: {str(error)}"
                        )
                        try:
                            await client.disconnect()
                        except:
                            pass

                # Обновляем интерфейс после обработки всех файлов
                selected_files.value = f"✅ Обработано файлов: {len(files)}"
                selected_files.update()
                self.page.update()

                await show_notification(
                    page=self.page,
                    message=f"✅ Успешно обработано {len(files)} session файлов"
                )

            except Exception as error:
                logger.exception(error)
                await self.app_logger.log_and_display(
                    message=f"❌ Ошибка при выборе файлов: {str(error)}"
                )

        self.page.views.append(
            ft.View(
                route="/account_connection_menu",  # Маршрут для этого представления
                appbar=await self.gui_program.key_app_bar(page=self.page),  # Кнопка назад
                controls=[
                    ft.Text(
                        spans=[
                            ft.TextSpan(
                                "Подключение аккаунта Telegram по номеру телефона.",
                                ft.TextStyle(
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    foreground=ft.Paint(
                                        gradient=ft.PaintLinearGradient(
                                            (0, 20),
                                            (150, 20),
                                            [
                                                ft.Colors.PINK,
                                                ft.Colors.PURPLE
                                            ]
                                        )
                                    )
                                )
                            )
                        ]
                    ),
                    list_view,  # Отображение логов 📝
                    phone_number,
                    # 📞 Подключение аккаунтов по номеру телефона
                    ft.Button(
                        content="Получить код",
                        width=WIDTH_WIDE_BUTTON,
                        height=BUTTON_HEIGHT,
                        on_click=connecting_number_accounts
                    ),
                    await self.gui_program.diver_castom(),  # Горизонтальная линия
                    ft.Text(
                        spans=[
                            ft.TextSpan(
                                "Подключение session аккаунтов Telegram",
                                ft.TextStyle(
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    foreground=ft.Paint(
                                        gradient=ft.PaintLinearGradient(
                                            (0, 20),
                                            (150, 20), [
                                                ft.Colors.PINK,
                                                ft.Colors.PURPLE
                                            ]
                                        )
                                    )
                                )
                            )
                        ]
                    ),
                    ft.Text(f"Выберите session файл\n", size=15),
                    selected_files,  # Поле для отображения выбранного файла
                    ft.Column(
                        [  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                            # 🔑 Подключение session аккаунтов

                            await menu_button_fun(
                                text=translations["ru"]["create_groups_menu"]["choose_session_files"],
                                width=WIDTH_WIDE_BUTTON,
                                height=BUTTON_HEIGHT,
                                on_click=handle_get_directory_path
                            ),  # Кнопка выбора файла
                            directory_path := ft.Text(),
                        ]
                    )
                ]
            )
        )
# 486
