# -*- coding: utf-8 -*-
import configparser

"""Настройки программы"""
config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config.read(filenames='user_data/config/config.ini', encoding='utf-8')
TIME_ACTIVITY_USER_2 = config.get('time_activity_user', 'time_activity_user_2', fallback=None)
# Удалены неиспользуемые переменные TIME_SENDING_MESSAGES_1 и TIME_SENDING_MESSAGES_2
time_subscription_1 = config.get('time_subscription', 'time_subscription_1', fallback=None)
time_subscription_2 = config.get('time_subscription', 'time_subscription_2', fallback=None)
api_id = config.get('telegram_settings', 'id', fallback=None)
api_hash = config.get('telegram_settings', 'hash', fallback=None)

TIME_SENDING_MESSAGES_1 = config.get('time_inviting', 'time_inviting_1', fallback=None)
TIME_SENDING_MESSAGES_2 = config.get('time_inviting', 'time_inviting_2', fallback=None)

"""Настройки внешнего вида программы"""
config_gui = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config_gui.read(filenames='user_data/config/config_gui.ini', encoding='utf-8')
BUTTON_HEIGHT = config_gui.get('height_button', 'height_button', fallback=None)  # Получение ширины кнопки
PROGRAM_NAME = config_gui.get('program_name', 'program_name', fallback=None)  # Имя программы
PROGRAM_VERSION = config_gui.get('program_version', 'program_version', fallback=None)  # Версия программы
DATE_OF_PROGRAM_CHANGE = config_gui.get('date_of_program_change', 'date_of_program_change',
                                        fallback=None)  # Дата изменения (обновления)

# Ширина программы / высота программы
WINDOW_WIDTH = 1050  # Ширина программы
WINDOW_HEIGHT = 725  # Высота программы

WINDOW_RESIZABLE = config_gui.get('window_resizable', 'window_resizable', fallback=None)  # Ширина программы
WIDTH_WIDE_BUTTON = config_gui.get('line_width_button', 'line_width_button', fallback=None)  # Ширина кнопки
WIDTH_INPUT_FIELD_AND_BUTTON = int(WIDTH_WIDE_BUTTON) / 2 - 5  # Ширина кнопки (окно и поле ввода)
width_one_input = 500  # 2 поля ввода (без кнопки сохранить)
width_tvo_input = 245  # 4 поля ввода (без кнопки сохранить)

"""Путь к папкам"""
config_path = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config_path.read(filenames='user_data/config/config_path.ini', encoding='utf-8')
# Путь к сообщениям
path_folder_with_messages = config_path.get('path_folder_with_messages', 'path_folder_with_messages', fallback=None)

# Путь к папке с базой данных
path_folder_database = config_path.get('path_folder_database', 'path_folder_database', fallback=None)

# Широкая одиночная кнопка
wide_single_button = 300  # Применяется: Инвайтинг
