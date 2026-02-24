# -*- coding: utf-8 -*-
import configparser

"""Настройки программы"""
config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config.read(filenames='user_data/config.ini', encoding='utf-8')
TIME_ACTIVITY_USER_2 = config.get('time_activity_user', 'time_activity_user_2', fallback=None)
# Удалены неиспользуемые переменные TIME_SENDING_MESSAGES_1 и TIME_SENDING_MESSAGES_2
time_subscription_1 = config.get('time_subscription', 'time_subscription_1', fallback=None)
time_subscription_2 = config.get('time_subscription', 'time_subscription_2', fallback=None)
api_id = config.get('telegram_settings', 'id', fallback=None)
api_hash = config.get('telegram_settings', 'hash', fallback=None)

"""Настройки внешнего вида программы"""

PROGRAM_NAME = "TelegramMaster-PRO"  # Имя программы
PROGRAM_VERSION = "2.8.25"  # Версия программы
DATE_OF_PROGRAM_CHANGE = "25.02.2026"  # Дата изменения (обновления)

# Ширина программы / высота программы
window_width = 1050  # Ширина (программы)
window_height = 810  # Высота (программы)

WIDTH_WIDE_BUTTON = int(window_width) - 5  # Ширина кнопки
WIDTH_INPUT_FIELD_AND_BUTTON = int(window_width) / 2 - 27  # Ширина кнопки (окно и поле ввода)
width_one_input = int(window_width) / 2 - 27  # 2 поля ввода (без кнопки сохранить)
width_tvo_input = 245  # 4 поля ввода (без кнопки сохранить)

# Широкая одиночная кнопка
BUTTON_HEIGHT = 30  # Высота (кнопок главного меню)
BUTTON_WIDTH = 400  # Ширина (кнопок главного меню)

"""Путь к папкам"""

# Путь к папке с сообщениями, для рассылки сообщений
path_folder_with_messages = "user_data/message"
# Путь к папке с базой данных
path_folder_database = "user_data/software_database.db"
