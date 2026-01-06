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

PROGRAM_NAME = "TelegramMaster-PRO"  # Имя программы
PROGRAM_VERSION = "2.8.4"  # Версия программы
DATE_OF_PROGRAM_CHANGE = "05.01.2026"  # Дата изменения (обновления)

WIDTH_WIDE_BUTTON = 1010  # Ширина кнопки
WIDTH_INPUT_FIELD_AND_BUTTON = int(WIDTH_WIDE_BUTTON) / 2 - 5  # Ширина кнопки (окно и поле ввода)
width_one_input = 500  # 2 поля ввода (без кнопки сохранить)
width_tvo_input = 245  # 4 поля ввода (без кнопки сохранить)

# Широкая одиночная кнопка
wide_single_button = 300  # Применяется: Инвайтинг

BUTTON_HEIGHT = 30  # Высота (кнопок главного меню)
BUTTON_WIDTH = 400  # Ширина (кнопок главного меню)

# Ширина программы / высота программы
window_width = 1050  # Ширина (программы)
window_height = 680  # Высота (программы)

"""Путь к папкам"""
config_path = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config_path.read(filenames='user_data/config/config_path.ini', encoding='utf-8')
# Путь к сообщениям
path_folder_with_messages = config_path.get('path_folder_with_messages', 'path_folder_with_messages', fallback=None)

# Путь к папке с базой данных
path_folder_database = config_path.get('path_folder_database', 'path_folder_database', fallback=None)
