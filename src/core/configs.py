# -*- coding: utf-8 -*-
import configparser

config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config.read(filenames='user_data/config/config.ini', encoding='utf-8')
time_changing_accounts_1 = config.get('time_changing_accounts', 'time_changing_accounts_1', fallback=None)
time_changing_accounts_2 = config.get('time_changing_accounts', 'time_changing_accounts_2', fallback=None)

config_gui = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config_gui.read(filenames='user_data/config/config_gui.ini', encoding='utf-8')
BUTTON_HEIGHT = config_gui.get('height_button', 'height_button', fallback=None)  # Получение ширины кнопки
PROGRAM_NAME = config_gui.get('program_name', 'program_name', fallback=None)  # Имя программы
PROGRAM_VERSION = config_gui.get('program_version', 'program_version', fallback=None)  # Версия программы
DATE_OF_PROGRAM_CHANGE = config_gui.get('date_of_program_change', 'date_of_program_change',
                                        fallback=None)  # Дата изменения (обновления)
WINDOW_WIDTH = config_gui.get('window_width', 'window_width', fallback=None)  # Ширина программы
WINDOW_HEIGHT = config_gui.get('window_height', 'window_height', fallback=None)  # Высота программы
WINDOW_RESIZABLE = config_gui.get('window_resizable', 'window_resizable', fallback=None)  # Ширина программы


class ConfigReader:

    def __init__(self):
        self.config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
        self.config.read(filenames='user_data/config/config.ini', encoding='utf-8')

        self.config_path = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
        self.config_path.read(filenames='user_data/config/config_path.ini', encoding='utf-8')

    def get_time_subscription(self):
        return (self.config.getint('time_subscription', 'time_subscription_1', fallback=None),
                self.config.getint('time_subscription', 'time_subscription_2', fallback=None))

    def get_time_inviting(self):
        return (self.config.getint('time_inviting', 'time_inviting_1', fallback=None),
                self.config.getint('time_inviting', 'time_inviting_2', fallback=None))

    def time_activity_user_2(self):
        """   """
        return self.config.get('time_activity_user', 'time_activity_user_2', fallback=None)

    def get_api_id_data_api_hash_data(self):
        return (self.config.get('telegram_settings', 'id', fallback=None),
                self.config.get('telegram_settings', 'hash', fallback=None))

    def path_folder_with_messages(self) -> str | None:
        """
        Путь к папке с сообщениями (путь к config файлу user_data/config/config_path.ini)
        """
        return self.config_path.get('path_folder_with_messages',
                                    'path_folder_with_messages', fallback=None)

    def path_folder_database(self) -> str | None:
        """
        Путь к папке с базой данных (путь к config файлу user_data/config/config_path.ini)
        """
        return self.config_path.get('path_folder_database',
                                    'path_folder_database', fallback=None)


# TODO - Все переменные должны быть с главных буквы
"""Размеры кнопок WIDTH_WIDE_BUTTON - Ширина широкой кнопки"""
WIDTH_WIDE_BUTTON = config_gui.get('line_width_button', 'line_width_button', fallback=None)  # Ширина кнопки

WIDTH_INPUT_FIELD_AND_BUTTON = int(WIDTH_WIDE_BUTTON) / 2 - 5  # Ширина кнопки (окно и поле ввода)

"""Путь к папкам"""
path_folder_with_messages = ConfigReader().path_folder_with_messages()  # Путь к папке с сообщениями
path_folder_database = ConfigReader().path_folder_database()  # Путь к папке с базой данных

"""Настройки времени, лимитов и прочего"""
TIME_ACTIVITY_USER_2 = ConfigReader().time_activity_user_2()
TIME_SENDING_MESSAGES_1, time_sending_messages_2 = ConfigReader().get_time_inviting()  # Время между сообщениями
time_subscription_1, time_subscription_2 = ConfigReader().get_time_subscription()

"""Настройки внешнего вида программы"""

width_one_input = 500  # 2 поля ввода (без кнопки сохранить)
width_tvo_input = 245  # 4 поля ввода (без кнопки сохранить)

# 117
