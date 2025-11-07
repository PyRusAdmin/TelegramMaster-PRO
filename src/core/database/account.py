# -*- coding: utf-8 -*-
from peewee import (Model, CharField)
from loguru import logger
from src.core.database.database import db

"""Работа с аккаунтами"""


class Account(Model):
    """Модель аккаунта"""
    session_string = CharField(unique=True)  # уникальность для защиты от дубликатов
    phone_number = CharField()  # номер телефона аккаунта

    class Meta:
        database = db
        table_name = 'account'


def write_account_to_db(session_string, phone_number):
    """
    Запись аккаунта в базу данных
    :param phone_number: Номер телефона аккаунта
    :param session_string: Строка сессии
    """
    Account.insert(session_string=session_string, phone_number=phone_number).on_conflict(action='IGNORE').execute()


def getting_account():
    """
    Получение аккаунтов из базы данных
    :return: Список аккаунтов из базы данных
    """

    records = []
    for record in Account.select(Account.session_string):
        records.append(record.session_string)

    logger.warning(records)
    return records


async def delete_account_from_db(session_string: str, app_logger) -> None:
    """
    Удаляет аккаунт из таблицы 'account' по session_string.
    Перед удалением извлекает и логирует номер телефона.

    :param session_string: Строка сессии аккаунта
    :param app_logger: Объект логгера для вывода сообщений
    :return: None
    """
    try:
        # Ищем аккаунт по session_string
        account = Account.get(Account.session_string == session_string)
        phone_number = account.phone_number

        await app_logger.log_and_display(message=f"Найден аккаунт для удаления: {phone_number}")

        # Удаляем запись
        account.delete_instance()

        await app_logger.log_and_display(message=f"Аккаунт {phone_number} успешно удалён из базы данных.")

    except Account.DoesNotExist:
        await app_logger.log_and_display(message=f"Аккаунт с session_string='{session_string}' не найден в базе.")
    except Exception as e:
        logger.exception("Ошибка при удалении аккаунта")
        await app_logger.log_and_display(message=f"Ошибка при удалении аккаунта: {e}")


def get_account_list():
    """Получаем подключенные аккаунты: возвращаем список кортежей (phone, session_string)"""
    accounts = []
    for account in Account.select(Account.phone_number, Account.session_string):
        accounts.append((account.phone_number, account.session_string))
    logger.info(f"Загружено аккаунтов: {len(accounts)}")
    return accounts  # Список аккаунтов
