# -*- coding: utf-8 -*-
import configparser
import io
import json
import os
import sys

import flet as ft  # Импортируем библиотеку flet
from loguru import logger

from src.core.config.configs import BUTTON_HEIGHT, WIDTH_WIDE_BUTTON
from src.core.database.database import save_proxy_data_to_db
from src.gui.buttons import menu_button_fun
from src.gui.gui import AppLogger, list_view
from src.gui.gui_elements import GUIProgram
from src.gui.notification import show_notification
from src.locales.translations_loader import translations

config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config.read("user_data/config.ini")

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class SettingPage:

    def __init__(self, page: ft.Page):
        """
        Инициализация класса для управления настройками приложения.

        :param page: Страница интерфейса Flet для отображения элементов управления
        """
        self.page = page
        self.app_logger = AppLogger(page=page)
        self.gui_program = GUIProgram()
        self.page = page
        self.gui_program = GUIProgram()

    def get_unique_filename(self, base_filename) -> str:
        """
        Генерирует уникальное имя файла, добавляя индекс к базовому имени.

        :param base_filename: Базовое имя файла
        :return: Уникальное имя файла
        """
        index = 1
        while True:
            new_filename = f"{base_filename}_{index}.json"
            if not os.path.isfile(new_filename):
                return new_filename
            index += 1

    async def settings_page_menu(self):
        """
        Основное меню страницы настроек

        Меню настройки
        """
        try:

            async def reaction_gui():
                """
                Создает графический интерфейс для выбора реакций.
                :return: None
                """
                try:
                    t = ft.Text(value='Выберите реакцию')  # Создает текстовое поле (t).

                    # Создаем все чекбоксы единожды и сохраняем их в списке
                    checkboxes = [
                        ft.Checkbox(label="😀"), ft.Checkbox(label="😎"), ft.Checkbox(label="😍"),
                        ft.Checkbox(label="😂"), ft.Checkbox(label="😡"), ft.Checkbox(label="😱"),
                        ft.Checkbox(label="😭"), ft.Checkbox(label="👍"), ft.Checkbox(label="👎"),
                        ft.Checkbox(label="❤"), ft.Checkbox(label="🔥"), ft.Checkbox(label="🎉"),
                        ft.Checkbox(label="😁"), ft.Checkbox(label="😢"), ft.Checkbox(label="💩"),
                        ft.Checkbox(label="👏"), ft.Checkbox(label="🤷‍♀️"), ft.Checkbox(label="🤷"),
                        ft.Checkbox(label="🤷‍♂️"), ft.Checkbox(label="👾"), ft.Checkbox(label="🙊"),
                        ft.Checkbox(label="💊"), ft.Checkbox(label="😘"), ft.Checkbox(label="🦄"),
                        ft.Checkbox(label="💘"), ft.Checkbox(label="🆒"), ft.Checkbox(label="🗿"),
                        ft.Checkbox(label="🤪"), ft.Checkbox(label="💅"), ft.Checkbox(label="☃️"),
                        ft.Checkbox(label="🎄"), ft.Checkbox(label="🎅"), ft.Checkbox(label="🤗"),
                        ft.Checkbox(label="🤬"), ft.Checkbox(label="🤮"), ft.Checkbox(label="🤡"),
                        ft.Checkbox(label="🥴"), ft.Checkbox(label="💯"), ft.Checkbox(label="🌭"),
                        ft.Checkbox(label="⚡️"), ft.Checkbox(label="🍌"), ft.Checkbox(label="🖕"),
                        ft.Checkbox(label="💋"), ft.Checkbox(label="👀"), ft.Checkbox(label="🤝"),
                        ft.Checkbox(label="🍾"), ft.Checkbox(label="🏆"), ft.Checkbox(label="🥱"),
                        ft.Checkbox(label="🕊"), ft.Checkbox(label="😭")
                    ]

                    async def button_clicked(_) -> None:
                        """Выбранная реакция"""
                        selected_reactions = [checkbox.label for checkbox in checkboxes if
                                              checkbox.value]  # Получаем только выбранные реакции
                        self.write_data_to_json_file(reactions=selected_reactions,
                                                     path_to_the_file='user_data/reactions/reactions.json')

                        await show_notification(page=self.page, message="Данные успешно записаны!")
                        self.page.go("/settings")  # Переход к странице настроек

                    # Добавляем элементы на страницу
                    self.page.views.append(
                        ft.View(
                            route="/settings",
                            appbar=await self.gui_program.key_app_bar(page=self.page),  # Кнопка назад
                            controls=[
                                # Кнопка для перехода на главную страницу
                                t,
                                ft.Column(
                                    [ft.Row(checkboxes[i:i + 9]) for i in range(0, len(checkboxes), 9)]),
                                # Чекбоксы в колонках
                                ft.Button(
                                    content=translations["ru"]["buttons"]["done"],
                                    width=WIDTH_WIDE_BUTTON,
                                    height=BUTTON_HEIGHT,
                                    on_click=button_clicked),  # Кнопка "Готово"
                            ]
                        )
                    )
                except Exception as e:
                    logger.exception(e)

            async def creating_the_main_window_for_proxy_data_entry() -> None:
                """
                Создает интерфейс для ввода данных прокси-сервера.

                :return: None
                """
                try:
                    # self.page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝

                    list_view.controls.append(ft.Text(f"Введите данные для записи"))  # отображаем сообщение в ListView

                    proxy_type = ft.TextField(label="Введите тип прокси, например SOCKS5: ", multiline=True,
                                              max_lines=19)
                    addr_type = ft.TextField(label="Введите ip адрес, например 194.67.248.9: ", multiline=True,
                                             max_lines=19)
                    port_type = ft.TextField(label="Введите порт прокси, например 9795: ", multiline=True, max_lines=19)
                    username_type = ft.TextField(label="Введите username, например NnbjvX: ", multiline=True,
                                                 max_lines=19)
                    password_type = ft.TextField(label="Введите пароль, например ySfCfk: ", multiline=True,
                                                 max_lines=19)

                    async def btn_click(_) -> None:
                        proxy = {
                            "proxy_type": proxy_type.value,
                            "addr": addr_type.value,
                            "port": port_type.value,
                            "username": username_type.value,
                            "password": password_type.value,
                            "rdns": "True"
                        }
                        save_proxy_data_to_db(proxy=proxy)
                        await show_notification(self.page, "Данные успешно записаны!")
                        self.page.go("/settings")  # Изменение маршрута в представлении существующих настроек
                        self.page.update()

                    await self.add_view_with_fields_and_button(
                        [proxy_type, addr_type, port_type, username_type, password_type],
                        btn_click)
                except Exception as e:
                    logger.exception(e)

            async def writing_api_id_api_hash():
                """
                Создает интерфейс для записи API ID и API Hash.
                :return: None
                """
                try:
                    # self.page.controls.append(list_view)  # добавляем ListView на страницу для отображения логов 📝
                    list_view.controls.append(ft.Text(f"Введите данные для записи"))  # отображаем сообщение в ListView
                    api_id_data = ft.TextField(label="Введите api_id", multiline=True, max_lines=19)
                    api_hash_data = ft.TextField(label="Введите api_hash", multiline=True, max_lines=19)

                    def btn_click(_) -> None:
                        config.get("telegram_settings", "id")
                        config.set("telegram_settings", "id", api_id_data.value)
                        config.get("telegram_settings", "hash")
                        config.set("telegram_settings", "hash", api_hash_data.value)
                        self.writing_settings_to_a_file(config)
                        self.page.go("/settings")  # Изменение маршрута в представлении существующих настроек
                        self.page.update()

                    await self.add_view_with_fields_and_button([api_id_data, api_hash_data], btn_click)
                except Exception as e:
                    logger.exception(e)

            async def recording_text_for_sending_messages(label, unique_filename) -> None:
                """
                Создает интерфейс для записи текста в JSON-файл для отправки сообщений в Telegram.

                :param label: Текст для отображения в поле ввода
                :param unique_filename: Имя файла для записи данных
                :return: None
                """
                try:
                    list_view.controls.clear()  # ✅ Очистка логов перед новым запуском
                    list_view.controls.append(ft.Text(f"Введите данные для записи"))  # отображаем сообщение в ListView
                    text_to_send = ft.TextField(
                        label=label,  # ✅ Текстовая метка поля ввода (например, "Введите сообщение")
                        multiline=True,  # ✅ Разрешает ввод нескольких строк (многострочный режим)
                        max_lines=19,  # ✅ Ограничивает отображение максимум 19 строками
                        width=WIDTH_WIDE_BUTTON  # ✅ Устанавливает ширину поля ввода
                    )

                    async def btn_click(_) -> None:
                        self.write_data_to_json_file(  # Сохраняем данные в файл
                            reactions=text_to_send.value,
                            path_to_the_file=unique_filename
                        )
                        await show_notification(
                            page=self.page,
                            message="Данные успешно записаны!"
                        )
                        self.page.go("/settings")  # Изменение маршрута в представлении существующих настроек
                        self.page.update()

                    await self.add_view_with_fields_and_button(
                        fields=[text_to_send],
                        btn_click=btn_click
                    )
                except Exception as e:
                    logger.exception(e)

            async def message_recording():
                await recording_text_for_sending_messages(
                    label="Введите текст для сообщения",
                    unique_filename=self.get_unique_filename(base_filename='user_data/message/message')
                )

            async def recording_reaction_link():
                await recording_text_for_sending_messages(
                    label="Введите ссылку для реакций",
                    unique_filename='user_data/reactions/link_channel.json'
                )

            self.page.views.append(
                ft.View(
                    route="/settings",
                    appbar=await self.gui_program.key_app_bar(page=self.page),  # Кнопка назад
                    controls=[
                        ft.Text(
                            spans=[
                                ft.TextSpan(
                                    translations["ru"]["menu"]["settings"],
                                    ft.TextStyle(
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        foreground=ft.Paint(
                                            gradient=ft.PaintLinearGradient(
                                                (
                                                    0,
                                                    20
                                                ),
                                                (
                                                    150,
                                                    20
                                                ),
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

                        ft.Column(
                            controls=[  # Добавляет все чекбоксы и кнопку на страницу (page) в виде колонок.
                                await menu_button_fun(  # 👍 Выбор реакций
                                    text=translations["ru"]["menu_settings"]["choice_of_reactions"],
                                    width=WIDTH_WIDE_BUTTON,
                                    height=BUTTON_HEIGHT,
                                    on_click=reaction_gui
                                ),
                                await menu_button_fun(  # 🔐 Запись proxy
                                    text=translations["ru"]["menu_settings"]["proxy_entry"],
                                    width=WIDTH_WIDE_BUTTON,
                                    height=BUTTON_HEIGHT,
                                    on_click=creating_the_main_window_for_proxy_data_entry
                                ),
                                await menu_button_fun(  # 📝 Запись api_id, api_hash
                                    text=translations["ru"]["menu_settings"]["recording_api_id_api_hash"],
                                    width=WIDTH_WIDE_BUTTON,
                                    height=BUTTON_HEIGHT,
                                    on_click=writing_api_id_api_hash
                                ),
                                await menu_button_fun(  # ✉️ Запись сообщений
                                    text=translations["ru"]["menu_settings"]["message_recording"],
                                    width=WIDTH_WIDE_BUTTON,
                                    height=BUTTON_HEIGHT,
                                    on_click=message_recording
                                ),
                                await menu_button_fun(  # 🔗 Запись ссылки для реакций
                                    text=translations["ru"]["menu_settings"]["recording_reaction_link"],
                                    width=WIDTH_WIDE_BUTTON,
                                    height=BUTTON_HEIGHT,
                                    on_click=recording_reaction_link
                                ),
                            ]
                        )
                    ]
                )
            )
        except Exception as e:
            logger.exception(e)

    async def add_view_with_fields_and_button(self, fields: list, btn_click) -> None:
        """
        Добавляет представление с заданными текстовыми полями и кнопкой.

        :param fields: Список текстовых полей для добавления
        :param btn_click: Функция-обработчик для кнопки
        :return: None
        """

        # Создание View с элементами
        self.page.views.append(
            ft.View(
                route="/settings",
                appbar=await self.gui_program.key_app_bar(page=self.page),  # Кнопка назад
                controls=[
                    list_view,  # отображение логов 📝
                    ft.Column(
                        controls=fields + [
                            ft.Button(
                                content=translations["ru"]["buttons"]["done"],
                                width=WIDTH_WIDE_BUTTON,  # Ширина
                                height=BUTTON_HEIGHT,  # Высота
                                on_click=btn_click
                            ),
                        ]
                    )
                ]
            )
        )

    def writing_settings_to_a_file(self, config) -> None:
        """
        Записывает конфигурационные данные в файл.

        :param config: Объект конфигурации для записи
        :return: None
        """
        with open("user_data/config.ini", "w") as setup:  # Открываем файл в режиме записи
            config.write(setup)  # Записываем данные в файл

    async def recording_limits_file(self, time_1, time_2, variable: str) -> configparser.ConfigParser:
        """
        Записывает временные лимиты в конфигурационный файл.

        :param time_1: Начальное время в секундах
        :param time_2: Конечное время в секундах
        :param variable: Название переменной в файле config.ini
        :return: Объект конфигурации
        """
        try:
            config.get(f"{variable}", f"{variable}_1")
            config.set(f"{variable}", f"{variable}_1", time_1)
            config.get(f"{variable}", f"{variable}_2")
            config.set(f"{variable}", f"{variable}_2", time_2)
        except configparser.NoSectionError as error:
            await self.app_logger.log_and_display(
                message=f"❌ Не удалось получить значение переменной: {error}. Проверьте TelegramMaster/user_data/config.ini")
        return config

    def write_data_to_json_file(self, reactions, path_to_the_file):
        """
        Записывает данные в JSON-файл.

        :param reactions: Данные для записи
        :param path_to_the_file: Путь к файлу для записи
        :return: None
        """
        with open(path_to_the_file, 'w', encoding='utf-8') as file:
            json.dump(reactions, file, ensure_ascii=False, indent=4)
