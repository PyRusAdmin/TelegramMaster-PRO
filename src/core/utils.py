import asyncio
import json
import os
import os.path
import random  # Импортируем модуль random, чтобы генерировать случайное число

from loguru import logger

from src.core.database.database import delete_row_db
from src.gui.gui import AppLogger


class Utils:

    def __init__(self, page):
        self.page = page
        self.app_logger = AppLogger(self.page)

    async def read_json_file(self, filename):
        """
        Чтение данных из файла JSON.

        :param filename: Полный путь к файлу JSON.
        :return: Данные из файла JSON в виде словаря.
        """
        with open(filename, 'r', encoding="utf-8") as file:
            data = json.load(file)
        return data

    async def all_find_files(self, directory_path) -> list:
        """
        Поиск файлов в директории.

        :param directory_path: Путь к директории
        :return list: Список имен найденных файлов
        """
        entities = []  # Создаем список с именами найденных файлов
        for x in os.listdir(directory_path):
            if os.path.isfile(os.path.join(directory_path, x)):  # Проверяем, является ли x файлом
                entities.append(x)  # Добавляем имя файла в список
        return entities  # Возвращаем список файлов

    async def find_files(self, directory_path, extension) -> list:
        """
        Поиск файлов с определенным расширением в директории. Расширение файла должно быть указанно без точки.

        :param directory_path: Путь к директории
        :param extension: Расширение файла (указанное без точки)
        :return list: Список имен найденных файлов
        """
        entities = []  # Создаем словарь с именами найденных аккаунтов в папке user_data/accounts
        for x in os.listdir(directory_path):
            if x.endswith(f".{extension}"):  # Проверяем, заканчивается ли имя файла на заданное расширение
                file = os.path.splitext(x)[0]  # Разделяем имя файла на имя без расширения и расширение
                entities.append([file])  # Добавляем информацию о файле в список

        await self.app_logger.log_and_display(f"🔍 Найденные файлы: {entities}")

        return entities  # Возвращаем список json файлов

    async def record_inviting_results(self, time_range_1: int, time_range_2: int, username: str) -> None:
        """
        Запись результатов inviting, отправка сообщений в базу данных.

        :param time_range_1:  - диапазон времени смены аккаунта
        :param time_range_2:  - диапазон времени смены аккаунта
        :param username: - username аккаунта
        """
        await self.app_logger.log_and_display(f"Удаляем с базы данных username {username}")
        # Открываем базу с аккаунтами и с выставленными лимитами
        delete_row_db(username=username)
        # Смена username через случайное количество секунд
        await self.random_dream(time_range_1, time_range_2)

    async def random_dream(self, min_seconds: int, max_seconds: int):
        """
        Выполняет случайную задержку между операциями. (Рассылка сообщений, инвайтинг, и т.д)
        :param min_seconds: - диапазон времени смены аккаунта
        :param max_seconds: - диапазон времени смены аккаунта
        :return: None
        """
        try:
            time_in_seconds = random.randrange(int(min_seconds), int(max_seconds))
            await self.app_logger.log_and_display(f"Спим {time_in_seconds} секунд...")
            await asyncio.sleep(time_in_seconds)  # Спим 1 секунду
        except Exception as error:
            logger.exception(error)

    async def verifies_time_range_entered_correctly(self, min_seconds, max_seconds):
        """
        Проверяет корректность временного диапазона.
        :return: Кортеж (min, max) как целые числа
        :raises ValueError: При некорректном вводе
        """
        try:
            min_val = int(min_seconds.strip())
            max_val = int(max_seconds.strip())
            if min_val < 0 or max_val < 0:
                raise ValueError("Время не может быть отрицательным")
            if min_val > max_val:
                raise ValueError(f"Минимум ({min_val}) не может быть больше максимума ({max_val})")
            return min_val, max_val
        except (ValueError, AttributeError) as e:
            raise ValueError(
                f"Некорректный ввод времени: {min_seconds!r} – {max_seconds!r}. Введите целые числа.") from e
