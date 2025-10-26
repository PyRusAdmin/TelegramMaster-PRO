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


def get_account_list():
    """Получаем подключенные аккаунты: возвращаем список кортежей (phone, session_string)"""
    accounts = []
    for account in Account.select(Account.phone_number, Account.session_string):
        accounts.append((account.phone_number, account.session_string))
    logger.info(f"Загружено аккаунтов: {len(accounts)}")
    return accounts  # Список аккаунтов
