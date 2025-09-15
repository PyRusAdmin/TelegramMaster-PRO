# -*- coding: utf-8 -*-
import flet as ft  # Импортируем библиотеку flet
from loguru import logger  # Импортируем библиотеку loguru
from telethon import functions  # Импортируем библиотеку telethon
from telethon.errors import (AuthKeyUnregisteredError, UsernameInvalidError, UsernameOccupiedError,
                             UsernamePurchaseAvailableError)

from src.core.configs import WIDTH_WIDE_BUTTON, BUTTON_HEIGHT, path_accounts_folder
from src.core.utils import Utils
from src.features.account.connect import TGConnect
from src.features.account.parsing.gui_elements import GUIProgram
from src.gui.gui import AppLogger
from src.gui.notification import show_notification
from src.locales.translations_loader import translations


class AccountBIO:
    """
    Класс для управления изменениями данных аккаунта Telegram через графический интерфейс Flet.
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.connect = TGConnect(page=page)
        self.app_logger = AppLogger(page=page)
        self.utils = Utils(page=page)

    async def change_bio_profile(self, user_input):
        """
        Изменение описания профиля Telegram аккаунта.

        :param user_input - новое описание профиля Telegram
        :return: None
        """
        try:
            await self.app_logger.log_and_display(f"Запуск смены  описания профиля")
            for session_name in self.utils.find_filess(directory_path=path_accounts_folder, extension='session'):
                await self.app_logger.log_and_display(f"{session_name}")

                client = await self.connect.client_connect_string_session(session_name=session_name)

                await client.connect()
                if len(user_input) > 70:
                    await show_notification(self.page, f"❌ Описание профиля превышает 70 символов ({len(user_input)}).")
                    return
                try:
                    result = await client(functions.account.UpdateProfileRequest(about=user_input))
                    await self.app_logger.log_and_display(f"{result}\nПрофиль успешно обновлен!")
                except AuthKeyUnregisteredError:
                    await self.app_logger.log_and_display(translations["ru"]["errors"]["auth_key_unregistered"])
                finally:
                    await client.disconnect()

        except Exception as error:
            logger.exception(error)

        await show_notification(self.page, "Работа окончена")  # Выводим уведомление пользователю
        self.page.go("/bio_editing")  # переходим к основному меню изменения описания профиля 🏠

    async def change_name_profile(self, user_input):
        """
        Изменение имени профиля

        :param user_input - новое имя пользователя
        """
        try:
            for session_name in self.utils.find_filess(directory_path=path_accounts_folder, extension='session'):
                await self.app_logger.log_and_display(f"{session_name}")
                client = await self.connect.client_connect_string_session(session_name=session_name)
                await client.connect()
                try:
                    result = await client(functions.account.UpdateProfileRequest(first_name=user_input))
                    await self.app_logger.log_and_display(f"{result}\nИмя успешно обновлено!")
                except AuthKeyUnregisteredError:
                    await self.app_logger.log_and_display(translations["ru"]["errors"]["auth_key_unregistered"])
                finally:
                    await client.disconnect()
                await show_notification(self.page, "Работа окончена")  # Выводим уведомление пользователю
                self.page.go("/bio_editing")  # переходим к основному меню изменения имени профиля 🏠
        except Exception as error:
            logger.exception(error)

    async def bio_editing_menu(self):
        """
        Меню ✏️ Редактирование_BIO
        """

        profile_description_input_field = ft.TextField(label="Введите описание профиля, не более 70 символов: ",
                                                       multiline=True,
                                                       max_lines=19)

        async def btn_click(_) -> None:
            """Изменение описания профиля Telegram."""
            await self.change_bio_profile(user_input=profile_description_input_field.value)
            self.page.go("/bio_editing")  # Изменение маршрута
            self.page.update()

        profile_name_input_field = ft.TextField(label="Введите имя профиля, не более 64 символов: ",
                                                multiline=True,
                                                max_lines=19)

        async def change_name_profile_gui(_) -> None:
            """
            Изменение био профиля Telegram в графическое окно Flet
            """
            await self.change_name_profile(user_input=profile_name_input_field)
            self.page.go("/bio_editing")  # Изменение маршрута
            self.page.update()

        self.page.views.append(
            ft.View("/bio_editing",
                    [await GUIProgram().key_app_bar(),
                     ft.Text(spans=[ft.TextSpan(
                         translations["ru"]["menu"]["edit_bio"],
                         ft.TextStyle(
                             size=20, weight=ft.FontWeight.BOLD,
                             foreground=ft.Paint(
                                 gradient=ft.PaintLinearGradient((0, 20), (150, 20), [ft.Colors.PINK,
                                                                                      ft.Colors.PURPLE])), ), ), ], ),
                     ft.Column([  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                         # 🔄 Изменение username
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["edit_bio_menu"]["changing_the_username"],
                                           on_click=lambda _: self.page.go("/changing_username")),
                         # 🖼️ Изменение фото
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["edit_bio_menu"]["changing_the_photo"],
                                           on_click=lambda _: self.page.go("/edit_photo")),

                         profile_description_input_field,  # Поле для ввода описания профиля Telegram

                         # ✏️ Изменение описания
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["edit_bio_menu"]["changing_the_description"],
                                           on_click=btn_click),

                         profile_name_input_field,  # Поле для ввода имени профиля Telegram

                         # 📝 Изменение имени
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["edit_bio_menu"]["name_change_n"],
                                           on_click=change_name_profile_gui),

                         # 📝 Изменение фамилии
                         ft.ElevatedButton(width=WIDTH_WIDE_BUTTON, height=BUTTON_HEIGHT,
                                           text=translations["ru"]["edit_bio_menu"]["name_change_f"],
                                           on_click=lambda _: self.page.go("/change_surname")),
                     ])]))

    async def change_photo_profile_gui(self) -> None:
        """
        Изменение фото профиля Telegram через интерфейс Flet.
        """
        await self.change_photo_profile()

    async def change_username_profile_gui(self) -> None:
        """
        Изменение био профиля Telegram в графическое окно Flet
        """
        await self.create_profile_gui(self.change_username_profile,
                                      label="Введите username профиля (не более 32 символов):")

    async def change_last_name_profile_gui(self) -> None:
        """
        Изменение био профиля Telegram в графическое окно Flet
        """
        await self.create_profile_gui(self.change_last_name_profile,
                                      label="Введите фамилию профиля, не более 64 символов: ")

    # class AccountActions:
    #     """
    #     Класс, отвечающий за выполнение действий над аккаунтом Telegram.
    #     """
    #
    #     def __init__(self, directory_path, extension, tg_connect, page: ft.Page):
    #         self.page = page  # Страница интерфейса Flet
    #         self.directory_path = directory_path  # путь к папке с аккаунтами Telegram
    #         self.extension = extension  # расширение файла с аккаунтом Telegram (session)
    #         self.connect = tg_connect  # объект класса TelegramConnect (подключение к Telegram аккаунту)
    #         self.app_logger = AppLogger(page=page)
    #         self.utils = Utils(page=page)

    async def change_username_profile(self, user_input) -> None:
        """
        Изменение username профиля Telegram

        :param user_input  - новое имя пользователя
        """
        try:
            for session_name in self.utils.find_filess(directory_path=path_accounts_folder, extension='session'):
                await self.app_logger.log_and_display(f"{session_name}")
                client = await self.connect.client_connect_string_session(session_name=session_name)
                await client.connect()
                try:
                    await client(functions.account.UpdateUsernameRequest(username=user_input))
                    await show_notification(self.page, f'Работа окончена')  # Выводим уведомление пользователю
                except AuthKeyUnregisteredError:
                    await self.app_logger.log_and_display(translations["ru"]["errors"]["auth_key_unregistered"])
                except (UsernamePurchaseAvailableError, UsernameOccupiedError):
                    await show_notification(self.page, "❌ Никнейм уже занят")  # Выводим уведомление пользователю
                except UsernameInvalidError:
                    await show_notification(self.page, "❌ Неверный никнейм")  # Выводим уведомление пользователю
                finally:
                    await client.disconnect()
        except Exception as error:
            logger.exception(error)

    async def change_last_name_profile(self, user_input):
        """
        Изменение фамилии профиля

        :param user_input - новое имя пользователя Telegram
        """
        try:
            for session_name in self.utils.find_filess(directory_path=path_accounts_folder, extension='session'):
                await self.app_logger.log_and_display(f"{session_name}")
                client = await self.connect.client_connect_string_session(session_name=session_name)
                await client.connect()
                try:
                    result = await client(functions.account.UpdateProfileRequest(last_name=user_input))
                    await self.app_logger.log_and_display(f"{result}\nФамилия успешно обновлена!")
                except AuthKeyUnregisteredError:
                    await self.app_logger.log_and_display(translations["ru"]["errors"]["auth_key_unregistered"])
                finally:
                    await client.disconnect()
                await show_notification(self.page, "Работа окончена")  # Выводим уведомление пользователю
        except Exception as error:
            logger.exception(error)

    async def change_photo_profile(self):
        """Изменение фото профиля.
        """
        try:
            for session_name in self.utils.find_filess(directory_path=path_accounts_folder, extension='session'):
                await self.app_logger.log_and_display(message=f"{session_name}")
                client = await self.connect.client_connect_string_session(session_name=session_name)
                for photo_file in await self.utils.find_files(directory_path="user_data/bio", extension='jpg'):
                    try:
                        await client.connect()
                        await client(functions.photos.UploadProfilePhotoRequest(
                            file=await client.upload_file(f"user_data/bio/{photo_file[0]}.jpg")))
                    except AuthKeyUnregisteredError:
                        await self.app_logger.log_and_display(translations["ru"]["errors"]["auth_key_unregistered"])
                    finally:
                        await client.disconnect()
        except Exception as error:
            logger.exception(error)

        await show_notification(page=self.page, message="Работа окончена")  # Выводим уведомление пользователю
        self.page.go("/bio_editing")  # переходим к основному меню изменения описания профиля 🏠
