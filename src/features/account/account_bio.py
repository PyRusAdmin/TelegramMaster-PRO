import flet as ft  # Импортируем библиотеку flet
from loguru import logger  # Импортируем библиотеку loguru
from telethon import functions  # Импортируем библиотеку telethon
from telethon.errors import (
    AuthKeyUnregisteredError, UsernameInvalidError, UsernameOccupiedError, UsernamePurchaseAvailableError
)

from src.core.configs import WIDTH_WIDE_BUTTON, BUTTON_HEIGHT, WIDTH_INPUT_FIELD_AND_BUTTON
from src.core.database.account import getting_account, get_account_list
from src.core.utils import Utils
from src.features.account.connect import TGConnect
from src.gui.gui_elements import GUIProgram
from src.gui.gui import AppLogger, list_view
from src.locales.translations_loader import translations


class AccountBIO:
    """
    Класс для управления изменениями данных аккаунта Telegram через графический интерфейс Flet.
    """

    def __init__(self, page: ft.Page):
        """
        Инициализация класса AccountBIO.
        :param page: Объект страницы ft.Page
        """
        self.page = page  # Сохраняем объект страницы ft.Page
        self.connect = TGConnect(page=page)  # Создаем экземпляр класса TGConnect
        self.app_logger = AppLogger(page=page)  # Создаем экземпляр класса AppLogger
        self.utils = Utils(page=page)  # Создаем экземпляр класса Utils
        self.gui_program = GUIProgram(page=page)  # Создаем экземпляр класса GUIProgram
        self.session_string = getting_account()  # Получаем строку сессии из файла базы данных
        self.account_data = get_account_list()  # Получаем список аккаунтов из базы данных

    async def bio_editing_menu(self):
        """
        Меню ✏️ Редактирование_BIO
        """
        list_view.controls.clear()  # Очистка list_view для отображения новых элементов и недопущения дублирования

        account_drop_down_list = self.gui_program.create_account_dropdown(self.account_data)

        profile_description_input_field = ft.TextField(
            label="Введите описание профиля, не более 70 символов: ",
            multiline=True,
            width=WIDTH_INPUT_FIELD_AND_BUTTON,
            max_lines=19
        )
        input_field_username_change = ft.TextField(
            label="Введите username профиля (не более 32 символов): ",
            multiline=True,
            width=WIDTH_INPUT_FIELD_AND_BUTTON,
            max_lines=19
        )
        profile_name_input_field = ft.TextField(
            label="Введите имя профиля, не более 64 символов: ",
            multiline=True,
            width=WIDTH_INPUT_FIELD_AND_BUTTON,
            max_lines=19
        )
        profile_last_name_input_field = ft.TextField(
            label="Введите фамилию профиля, не более 64 символов: ",
            multiline=True,
            width=WIDTH_INPUT_FIELD_AND_BUTTON,
            max_lines=19
        )

        async def change_username_profile_gui(_) -> None:
            """
             Изменение username профиля Telegram профиля Telegram в графическое окно Flet
            """
            try:
                await self.app_logger.log_and_display(message=f"{account_drop_down_list.value}")
                client = await self.connect.client_connect_string_session(session_name=account_drop_down_list.value)
                try:
                    await client(
                        functions.account.UpdateUsernameRequest(username=input_field_username_change.value)
                    )
                    await self.gui_program.show_notification(  # ✅ Показываем уведомление пользователю
                        message="Работа окончена"
                    )
                except AuthKeyUnregisteredError:
                    await self.app_logger.log_and_display(
                        message=translations["ru"]["errors"]["auth_key_unregistered"]
                    )
                except (UsernamePurchaseAvailableError, UsernameOccupiedError):
                    await self.gui_program.show_notification(  # ✅ Показываем уведомление пользователю
                        message="❌ Никнейм уже занят"
                    )
                except UsernameInvalidError:
                    await self.gui_program.show_notification(  # ✅ Показываем уведомление пользователю
                        message="❌ Неверный никнейм"
                    )
            except Exception as e:
                logger.exception(e)

        async def change_bio_profile(_) -> None:
            """Изменение описания профиля Telegram аккаунта."""
            try:
                await self.app_logger.log_and_display(message="Запуск смены описания профиля.")
                await self.app_logger.log_and_display(message=f"{account_drop_down_list.value}")
                client = await self.connect.client_connect_string_session(session_name=account_drop_down_list.value)
                if len(profile_description_input_field.value) > 70:
                    await self.gui_program.show_notification(  # ✅ Показываем уведомление пользователю
                        f"❌ Описание профиля превышает 70 символов ({len(profile_description_input_field.value)})."
                    )
                    return
                try:
                    result = await client(
                        functions.account.UpdateProfileRequest(
                            about=profile_description_input_field.value
                        )
                    )
                    await self.app_logger.log_and_display(message=f"{result}\nПрофиль успешно обновлен!")
                except AuthKeyUnregisteredError:
                    await self.app_logger.log_and_display(
                        message=translations["ru"]["errors"]["auth_key_unregistered"])
            except Exception as e:
                logger.exception(e)
            await self.gui_program.show_notification(  # ✅ Показываем уведомление пользователю
                message="Работа окончена"
            )

        async def change_name_profile_gui(_) -> None:
            """
            Изменение имени профиля. Изменение био профиля Telegram в графическое окно Flet
            """
            try:
                await self.app_logger.log_and_display(message=f"{account_drop_down_list.value}")
                client = await self.connect.client_connect_string_session(session_name=account_drop_down_list.value)
                try:
                    result = await client(
                        functions.account.UpdateProfileRequest(
                            first_name=profile_name_input_field.value
                        )
                    )
                    await self.app_logger.log_and_display(message=f"{result}\nИмя успешно обновлено!")
                except AuthKeyUnregisteredError:
                    await self.app_logger.log_and_display(
                        message=translations["ru"]["errors"]["auth_key_unregistered"])
                await self.gui_program.show_notification(  # ✅ Показываем уведомление пользователю
                    message="Работа окончена"
                )
            except Exception as e:
                logger.exception(e)

        async def change_last_name_profile_gui(_) -> None:
            """
            Изменение фамилии профиля. Изменение био профиля Telegram в графическое окно Flet
            """
            try:
                await self.app_logger.log_and_display(message=f"{account_drop_down_list.value}")
                client = await self.connect.client_connect_string_session(session_name=account_drop_down_list.value)

                try:
                    result = await client(
                        functions.account.UpdateProfileRequest(
                            last_name=profile_last_name_input_field.value
                        )
                    )
                    await self.app_logger.log_and_display(message=f"{result}\nФамилия успешно обновлена!")
                except AuthKeyUnregisteredError:
                    await self.app_logger.log_and_display(
                        message=translations["ru"]["errors"]["auth_key_unregistered"]
                    )
                await self.gui_program.show_notification(  # ✅ Показываем уведомление пользователю
                    message="Работа окончена"
                )
            except Exception as e:
                logger.exception(e)

        async def change_photo_profile_gui(_) -> None:
            """
            Изменение фото профиля Telegram через интерфейс Flet.
            """
            try:
                await self.app_logger.log_and_display(message=f"{account_drop_down_list.value}")
                client = await self.connect.client_connect_string_session(session_name=account_drop_down_list.value)
                for photo_file in await self.utils.find_files(directory_path="user_data/bio", extension='jpg'):
                    try:
                        await client(
                            functions.photos.UploadProfilePhotoRequest(
                                file=await client.upload_file(f"user_data/bio/{photo_file[0]}.jpg")
                            )
                        )
                    except AuthKeyUnregisteredError:
                        await self.app_logger.log_and_display(
                            message=translations["ru"]["errors"]["auth_key_unregistered"])
            except Exception as e:
                logger.exception(e)
            await self.gui_program.show_notification(  # ✅ Показываем уведомление пользователю
                message="Работа окончена"
            )

        self.page.views.append(
            ft.View(
                route="/bio_editing",  # Маршрут для этого представления
                appbar=await self.gui_program.key_app_bar(),  # Кнопка назад
                controls=[
                    await self.gui_program.create_gradient_text(
                        text=translations["ru"]["menu"]["edit_bio"]
                    ),
                    list_view,  # Отображение логов 📝
                    account_drop_down_list,  # Выпадающий список с аккаунтами
                    ft.Column(  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                        [
                            ft.Row(
                                [
                                    input_field_username_change,  # Поле для ввода username Telegram
                                    # 🔄 Изменение username
                                    ft.Button(
                                        content=translations["ru"]["edit_bio_menu"]["changing_the_username"],
                                        width=WIDTH_INPUT_FIELD_AND_BUTTON,
                                        height=BUTTON_HEIGHT,
                                        on_click=change_username_profile_gui),
                                ]
                            ),
                            await self.gui_program.diver_castom(),  # Горизонтальная линия
                            ft.Row(
                                [
                                    profile_description_input_field,  # Поле для ввода описания профиля Telegram
                                    # ✏️ Изменение описания
                                    ft.Button(
                                        content=translations["ru"]["edit_bio_menu"]["changing_the_description"],
                                        width=WIDTH_INPUT_FIELD_AND_BUTTON, height=BUTTON_HEIGHT,
                                        on_click=change_bio_profile
                                    ),
                                ]
                            ),
                            await self.gui_program.diver_castom(),  # Горизонтальная линия
                            ft.Row(
                                [
                                    profile_name_input_field,  # Поле для ввода имени профиля Telegram
                                    # 📝 Изменение имени
                                    ft.Button(
                                        content=translations["ru"]["edit_bio_menu"]["name_change_n"],
                                        width=WIDTH_INPUT_FIELD_AND_BUTTON, height=BUTTON_HEIGHT,
                                        on_click=change_name_profile_gui
                                    ),
                                ]
                            ),
                            await self.gui_program.diver_castom(),  # Горизонтальная линия
                            ft.Row(
                                [
                                    profile_last_name_input_field,
                                    # 📝 Изменение фамилии
                                    ft.Button(
                                        content=translations["ru"]["edit_bio_menu"]["name_change_f"],
                                        width=WIDTH_INPUT_FIELD_AND_BUTTON,
                                        height=BUTTON_HEIGHT,
                                        on_click=change_last_name_profile_gui
                                    ),
                                ]
                            ),
                            await self.gui_program.diver_castom(),  # Горизонтальная линия
                            # 🖼️ Изменение фото
                            ft.Button(
                                content=translations["ru"]["edit_bio_menu"]["changing_the_photo"],
                                width=WIDTH_WIDE_BUTTON,
                                height=BUTTON_HEIGHT,
                                on_click=change_photo_profile_gui
                            ),
                        ]
                    )
                ]
            )
        )

# 244
