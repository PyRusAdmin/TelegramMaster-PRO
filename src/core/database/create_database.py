from src.core.database.account import Account
from src.core.database.database import (
    db, AccountContacts, WritingGroupLinks, GroupsAndChannels, MembersAdmin, LinksInviting, MembersGroups, Contact,
    Proxy, GroupsSendMessages
)


def create_database():
    """Создает все таблицы в базе данных"""
    db.connect()
    db.create_tables([AccountContacts])  # Создаем таблицу для хранения контактов аккаунтов
    db.create_tables([WritingGroupLinks, GroupsAndChannels, MembersAdmin])
    db.create_tables([LinksInviting])  # Создаем таблицу для хранения ссылок для инвайтинга
    db.create_tables([MembersGroups])  # Создаем таблицу для хранения спарсенных пользователей
    db.create_tables([Contact])  # Создаем таблицу для хранения контактов
    db.create_tables([Proxy])  # Создаем таблицу для хранения прокси
    db.create_tables([Account])
    db.create_tables([GroupsSendMessages])
