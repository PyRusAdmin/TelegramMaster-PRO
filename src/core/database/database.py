# -*- coding: utf-8 -*-
from datetime import datetime  # Импортируем класс datetime

import flet as ft
import peewee
from loguru import logger
from peewee import (
    SqliteDatabase, Model, CharField, BigIntegerField, TextField, DateTimeField, BooleanField, IntegerField
)

from src.core.configs import path_folder_database
from src.gui.gui import AppLogger

db = SqliteDatabase(path_folder_database)


class WritingGroupLinks(Model):
    """
    Таблица для хранения ссылок на группы в таблице writing_group_links
    """
    writing_group_links = CharField(unique=True)  # уникальность для защиты от дубликатов

    class Meta:
        database = db
        table_name = 'writing_group_links'


def write_writing_group_links_to_db(data_to_save):
    """
    Запись данных writing_group_links в базу данных. Добавлена проверка на уникальность ссылки. Дубликаты игнорируются и не
    записываются.
    """
    writing_group_links = data_to_save.get("writing_group_links", [])

    with db.atomic():
        for link in writing_group_links:
            try:
                WritingGroupLinks.get_or_create(writing_group_links=link)
            except peewee.IntegrityError:
                logger.warning(f"Ссылка уже существует в базе: {link}")


def get_writing_group_links():
    """Получаем ссылки на группы из таблицы writing_group_links"""
    writing_group_links = []
    for link in WritingGroupLinks.select(WritingGroupLinks.writing_group_links):
        writing_group_links.append(link.writing_group_links)
    logger.warning(writing_group_links)
    return writing_group_links


class GroupsSendMessages(Model):
    """Группы для рассылки сообщений"""

    # Основная информация
    link = CharField()  # Исходная ссылка на группу
    telegram_id = BigIntegerField(null=True)  # ID канала/группы в Telegram
    title = CharField(null=True)  # Название группы
    username = CharField(null=True)  # Username группы (без @)
    about = TextField(null=True)  # Описание группы

    # Статистика участников
    participants_count = IntegerField(null=True)  # Количество участников
    participants_hidden = TextField(null=True)  # Участники скрыты

    # Тип группы
    # is_broadcast = BooleanField(default=False)  # Является ли канал broadcast
    type_display = TextField(null=True)  # Является ли мегагруппой
    level = IntegerField(null=True)  # Уровень группы

    # Настройки сообщений
    slowmode_seconds = IntegerField(null=True)  # Задержка между сообщениями (slowmode)

    # Права на отправку (из default_banned_rights)
    can_send_messages = BooleanField(default=True)  # Можно отправлять текстовые сообщения
    can_send_media = BooleanField(default=True)  # Можно отправлять медиа
    can_send_photos = BooleanField(default=True)  # Можно отправлять фото
    can_send_videos = BooleanField(default=True)  # Можно отправлять видео
    can_send_docs = BooleanField(default=True)  # Можно отправлять документы
    can_send_audios = BooleanField(default=True)  # Можно отправлять аудио
    can_send_voices = BooleanField(default=True)  # Можно отправлять голосовые
    can_send_roundvideos = BooleanField(default=True)  # Можно отправлять видео-кружки
    can_send_stickers = BooleanField(default=True)  # Можно отправлять стикеры
    can_send_gifs = BooleanField(default=True)  # Можно отправлять GIF
    can_send_polls = BooleanField(default=True)  # Можно отправлять опросы
    can_embed_links = BooleanField(default=True)  # Можно вставлять ссылки
    can_invite_users = BooleanField(default=True)  # Можно приглашать пользователей

    # Реакции
    reactions_limit = IntegerField(null=True)  # Лимит реакций на сообщение
    available_reactions = TextField(null=True)  # JSON со списком доступных реакций

    # Платные функции
    paid_media_allowed = BooleanField(default=False)  # Разрешены платные медиа
    paid_reactions_available = BooleanField(default=False)  # Доступны платные реакции
    paid_messages_available = BooleanField(default=False)  # Доступны платные сообщения
    stargifts_available = BooleanField(default=False)  # Доступны звездные подарки
    stargifts_count = IntegerField(null=True)  # Количество звездных подарков

    # Дополнительные функции
    antispam = BooleanField(default=False)  # Включен антиспам
    translations_disabled = BooleanField(default=False)  # Отключен автоперевод
    linked_chat_id = BigIntegerField(null=True)  # ID связанного чата

    # Метаданные
    last_checked = DateTimeField(default=datetime.now)  # Время последней проверки
    is_active = BooleanField(default=True)  # Активна ли группа

    class Meta:
        database = db
        table_name = "group_send_messages"


def update_group_send_messages_table(link, telegram_id, title, username, about, participants_count,
                                     participants_hidden, type_display, level, slowmode_seconds,
                                     can_send_messages, can_send_media, can_send_photos, can_send_videos, can_send_docs,
                                     can_send_audios, can_send_voices, can_send_roundvideos, can_send_stickers,
                                     can_send_gifs, can_send_polls, can_embed_links, can_invite_users, reactions_limit,
                                     available_reactions, paid_media_allowed, paid_reactions_available,
                                     paid_messages_available, stargifts_available, stargifts_count, antispam,
                                     translations_disabled, linked_chat_id, last_checked, is_active):
    # Ищем запись по ссылке
    group = GroupsSendMessages.get_or_none(GroupsSendMessages.link == link)

    if group:
        group.telegram_id = telegram_id  # ID канала/группы в Telegram
        group.title = title  # Название группы
        group.username = username  # Username группы (без @)
        group.about = about  # Описание группы
        group.participants_count = participants_count  # Количество участников
        group.participants_hidden = participants_hidden  # Участники скрыты

        # group.is_broadcast = is_broadcast  # Является ли канал broadcast
        group.type_display = type_display  # Является ли мегагруппой

        group.level = level  # Уровень группы

        group.slowmode_seconds = slowmode_seconds  # Задержка между сообщениями (slowmode)
        group.can_send_messages = can_send_messages  # Можно отправлять текстовые сообщения

        group.can_send_media = can_send_media  # Можно отправлять медиа
        group.can_send_photos = can_send_photos  # Можно отправлять фото
        group.can_send_videos = can_send_videos  # Можно отправлять видео
        group.can_send_docs = can_send_docs  # Можно отправлять документы
        group.can_send_audios = can_send_audios  # Можно отправлять аудио
        group.can_send_voices = can_send_voices  # Можно отправлять голосовые
        group.can_send_roundvideos = can_send_roundvideos  # Можно отправлять видео-кружки
        group.can_send_stickers = can_send_stickers  # Можно отправлять стикеры
        group.can_send_gifs = can_send_gifs  # Можно отправлять GIF
        group.can_send_polls = can_send_polls  # Можно отправлять опросы
        group.can_embed_links = can_embed_links  # Можно вставлять ссылки
        group.can_invite_users = can_invite_users  # Можно приглашать пользователей

        # Реакции
        group.reactions_limit = reactions_limit  # Лимит реакций на сообщение
        group.available_reactions = available_reactions  # JSON со списком доступных реакций

        # Платные функции
        group.paid_media_allowed = paid_media_allowed  # Разрешены платные медиа
        group.paid_reactions_available = paid_reactions_available  # Доступны платные реакции
        group.paid_messages_available = paid_messages_available  # Доступны платные сообщения
        group.stargifts_available = stargifts_available  # Доступны звездные подарки
        group.stargifts_count = stargifts_count  # Количество звездных подарков

        # Дополнительные функции
        group.antispam = antispam  # Включен антиспам
        group.translations_disabled = translations_disabled  # Отключен автоперевод
        group.linked_chat_id = linked_chat_id  # ID связанного чата

        # Метаданные
        group.last_checked = last_checked  # Время последней проверки
        group.is_active = is_active  # Активна ли группа

        group.save()
        print(f"Обновлён telegram_id для {link}: {telegram_id}")
    else:
        print(f"Запись с ссылкой {link} не найдена в базе")


def write_group_send_message_table(chat_input):
    chat_input = chat_input.strip()
    logger.info(f"Записываем данные: {chat_input}")

    # Разделяем по строкам и фильтруем пустые значения
    links = [link.strip() for link in chat_input.splitlines() if link.strip()]

    logger.info(f"Найдено ссылок: {len(links)}")
    for link in links:
        logger.debug(f"Сохраняем ссылку: {link}")
        group = GroupsSendMessages(link=link)
        group.save()


def get_links_table_group_send_messages():
    writing_group_links = []
    for link in GroupsSendMessages.select(GroupsSendMessages.link):
        writing_group_links.append(link.link)
    logger.warning(writing_group_links)
    return writing_group_links


class GroupsAndChannels(Model):
    """
    Список групп и каналов в таблице groups_and_channels
    """
    id = IntegerField(primary_key=True)
    title = CharField(max_length=255)
    about = TextField(null=True)
    link = CharField(max_length=255, null=True)
    members_count = IntegerField(default=0)
    parsing_time = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        table_name = 'groups_and_channels'


class MembersAdmin(Model):
    """
    Таблица для хранения данных администраторов групп в таблице members_admin
    """
    username = CharField(max_length=255, null=True)
    user_id = IntegerField(unique=True)
    access_hash = BigIntegerField(null=True)
    first_name = CharField(max_length=255, null=True)
    last_name = CharField(max_length=255, null=True)
    phone = CharField(max_length=255, null=True)
    online_at = DateTimeField(null=True)
    photo_status = CharField(max_length=255, null=True)
    premium_status = BooleanField(default=False)
    user_status = CharField(max_length=255, null=True)
    bio = TextField(null=True)
    group_name = CharField(max_length=255, null=True)

    class Meta:
        database = db
        table_name = 'members_admin'


class AccountContacts(Model):
    """
    Таблица для хранения контактов аккаунтов в таблице account_contacts
    """
    username = CharField(max_length=255, null=True)
    user_id = IntegerField(unique=True)
    access_hash = BigIntegerField(null=True)
    first_name = CharField(max_length=255, null=True)
    last_name = CharField(max_length=255, null=True)
    phone = CharField(max_length=255, null=True)
    online_at = DateTimeField(null=True)
    photo_status = CharField(max_length=255, null=True)
    premium_status = BooleanField(default=False)

    class Meta:
        database = db
        table_name = 'account_contacts'


def write_to_database_contacts_accounts(data):
    """
    Запись или обновление данных контакта в таблице account_contacts
    :param data: словарь с данными контакта
    """
    AccountContacts.insert(
        user_id=data["user_id"],
        username=data["username"],
        access_hash=data["access_hash"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone=data["phone"],
        online_at=data["online_at"],
        photo_status=data["photo_status"],
        premium_status=bool(data["premium_status"]),  # убедитесь, что bool
    ).on_conflict(
        conflict_target=[AccountContacts.user_id],
        preserve=[
            AccountContacts.username,
            AccountContacts.access_hash,
            AccountContacts.first_name,
            AccountContacts.last_name,
            AccountContacts.phone,
            AccountContacts.online_at,
            AccountContacts.photo_status,
            AccountContacts.premium_status,
        ]
    ).execute()


""""Работа с таблицей contact (телефонная книга аккаунта Telegram)"""


class Contact(Model):
    """
    Таблица для хранения номеров телефонов в таблице contact
    """
    phone = CharField(unique=True)

    class Meta:
        database = db
        table_name = 'contact'


def write_contact_db(phone: str):
    """Запись контакта в базу данных (игнорирует дубликаты)"""
    Contact.insert(phone=phone).on_conflict(action='IGNORE').execute()


def getting_contacts_from_database():
    """Получение контактов (номеров телефонов) из базы данных"""
    records = []
    for record in Contact.select(Contact.phone):
        records.append(record.phone)
    logger.warning(records)
    return records


def delete_contact_db(phone: str):
    """Удаление контакта из базы данных"""
    Contact.delete().where(Contact.phone == phone).execute()


# TODO добавить все используемые таблицы
# def cleaning_db(table_name):
#     """
#     Очистка базы данных
#     :param table_name: Название таблицы, данные из которой требуется очистить.
#     """
#     if table_name == 'members':  # Удаляем все записи из таблицы members
#         MembersGroups.delete().execute()
#     if table_name == 'contact':  # Удаляем все записи из таблицы contact
#         Contact.delete().execute()
#     if table_name == 'writing_group_links':  # Удаляем все записи из таблицы writing_group_links
#         WritingGroupLinks.delete().execute()
#     if table_name == 'links_inviting':  # Удаляем все записи из таблицы links_inviting
#         LinksInviting.delete().execute()


"""Работа с таблицей members"""


class MembersGroups(Model):
    """
    Таблица для хранения данных администраторов групп в таблице members_admin
    """
    username = CharField(max_length=255, null=True)
    user_id = BigIntegerField(unique=True)
    access_hash = BigIntegerField(null=True)
    first_name = CharField(max_length=255, null=True)
    last_name = CharField(max_length=255, null=True)
    user_phone = CharField(max_length=255, null=True)
    online_at = DateTimeField(null=True)
    photos_id = CharField(max_length=255, null=True)
    user_premium = BooleanField(default=False)

    class Meta:
        database = db
        table_name = 'members'


async def select_records_with_limit(limit, app_logger):
    """
    Возвращает список usernames и user_id из таблицы members
    :param limit: Количество записей для возврата
    :param app_logger: Экземпляр класса AppLogger для логирования
    """
    usernames = []
    query = MembersGroups.select(MembersGroups.username, MembersGroups.user_id)
    for row in query:
        if row.username == "":
            # logger.info(f"У пользователя User ID: {row.user_id} нет username", )
            pass
        else:
            # logger.info(f"Username: {row.username}, User ID: {row.user_id}", )
            usernames.append(row.username)

    await app_logger.log_and_display(message=f"Всего username: {len(usernames)}")

    if limit is None:  # Если limit не указан, возвращаем все записи
        return usernames
    return usernames[:limit]  # Возвращаем первые limit записей, если указан


def read_parsed_chat_participants_from_db():
    """
    Чтение данных из базы данных.
    """
    data = []
    query = MembersGroups.select(
        MembersGroups.username, MembersGroups.user_id, MembersGroups.access_hash, MembersGroups.first_name,
        MembersGroups.last_name, MembersGroups.user_phone, MembersGroups.online_at, MembersGroups.photos_id,
        MembersGroups.user_premium
    )
    for row in query:
        data.append((
            row.username, row.user_id, row.access_hash, row.first_name, row.last_name,
            row.user_phone, row.online_at, row.photos_id, row.user_premium
        ))
    return data


def add_member_to_db(log_data):
    """
    Добавляет нового участника в базу данных или обновляет существующие данные.

    :param log_data: Словарь с информацией о пользователе
    """
    # Проверка существования пользователя в БД и атомарная запись новых данных
    with db.atomic():
        MembersGroups.get_or_create(
            user_id=log_data["user_id"],
            defaults={
                "username": log_data["username"],
                "access_hash": log_data["access_hash"],
                "first_name": log_data["first_name"],
                "last_name": log_data["last_name"],
                "user_phone": log_data["user_phone"],
                "online_at": log_data["online_at"],
                "photos_id": log_data["photos_id"],
                "user_premium": log_data["user_premium"],
            }
        )


def write_data_to_db(writing_group_links) -> None:
    """
    Запись действий аккаунта в базу данных

    :param writing_group_links: Ссылка на группу
    """
    MembersGroups.delete().where(WritingGroupLinks.writing_group_links == writing_group_links).execute()


def delete_row_db(username) -> None:
    """
    Удаляет строку из таблицы

    :param username: Имя пользователя
    """
    MembersGroups.delete().where(MembersGroups.username == username).execute()


"""Работа с таблицей proxy"""


class Proxy(Model):
    """
    Таблица для хранения прокси в таблице proxy
    """
    proxy_type = CharField(max_length=255)
    addr = CharField(max_length=255)
    port = CharField(max_length=255)
    username = CharField(max_length=255)
    password = CharField(max_length=255)
    rdns = CharField(max_length=255)

    class Meta:
        database = db
        table_name = 'proxy'


def save_proxy_data_to_db(proxy) -> None:
    """Запись данных proxy в базу данных"""
    with db.atomic():
        Proxy.get_or_create(
            proxy_type=proxy["proxy_type"],
            addr=proxy["addr"],
            port=proxy["port"],
            username=proxy["username"],
            password=proxy["password"],
            rdns=proxy["rdns"],
        )


async def deleting_an_invalid_proxy(proxy_type, addr, port, username, password, rdns, page: ft.Page) -> None:
    """
    Удаляем не рабочий proxy с software_database.db, таблица proxy

    :param page: Объект класса Page, который будет использоваться для отображения данных.
    :param proxy_type: Тип proxy
    :param addr: адрес
    :param port: порт
    :param username: имя пользователя
    :param password: пароль
    :param rdns: прокси
    """
    query = Proxy.delete().where(
        (Proxy.proxy_type == proxy_type) &
        (Proxy.addr == addr) &
        (Proxy.port == port) &
        (Proxy.username == username) &
        (Proxy.password == password) &
        (Proxy.rdns == rdns)
    )
    deleted_count = query.execute()
    app_logger = AppLogger(page)
    await app_logger.log_and_display(f"{deleted_count} rows deleted")


def get_proxy_database():
    """Получает прокси из базы данных"""
    proxy_data = []
    for proxy in Proxy.select(Proxy.proxy_type, Proxy.addr, Proxy.port, Proxy.username, Proxy.password, Proxy.rdns):
        proxy_data.append((
            proxy.proxy_type,
            proxy.addr,
            proxy.port,
            proxy.username,
            proxy.password,
            proxy.rdns
        ))
    logger.warning(proxy_data)
    return proxy_data


def open_and_read_data():
    pass


"""Запись ссылки для инвайтинга"""


class LinksInviting(Model):
    links_inviting = CharField(unique=True)

    class Meta:
        database = db
        table_name = 'links_inviting'


def get_links_inviting():
    """Получаем ссылки на группы из таблицы links_inviting"""
    links_inviting = []
    for link in LinksInviting.select(LinksInviting.links_inviting):
        links_inviting.append(link.links_inviting)
    logger.warning(links_inviting)
    return links_inviting


def save_links_inviting(data) -> None:
    """
    Запись данных links_inviting в базу данных. Добавлена проверка на уникальность ссылки. Дубликаты игнорируются и не
    записываются.
    """
    links = data.get("links_inviting", [])

    with db.atomic():
        for link in links:
            try:
                LinksInviting.get_or_create(links_inviting=link)
            except peewee.IntegrityError:
                logger.warning(f"Ссылка уже существует в базе: {link}")


def save_group_channel_info(dialog, title, about, link, participants_count):
    """
    Cохраняет или обновляет информацию о группе или канале в базе данных.

    :param dialog: Объект диалогового окна Telegram API
    :param title: заголовок группы или канала
    :param about: описание группы или канала
    :param link: ссылка на группу или канал
    :param participants_count: количество участников группы или канала
    """
    with db.atomic():
        GroupsAndChannels.insert(
            id=dialog.id,
            title=title,
            about=about,
            link=link,
            members_count=participants_count,
            parsing_time=datetime.datetime.now()
        ).on_conflict(
            conflict_target=[GroupsAndChannels.id],
            preserve=[GroupsAndChannels.id],
            update={
                GroupsAndChannels.title: title,
                GroupsAndChannels.about: about,
                GroupsAndChannels.link: link,
                GroupsAndChannels.members_count: participants_count,
                GroupsAndChannels.parsing_time: datetime.datetime.now(),
            }
        ).execute()


def administrators_entries_in_database(log_data):
    """Запись в базу данных всех администраторов."""
    with db.atomic():
        MembersAdmin.create(
            username=log_data["username"],
            user_id=log_data["user_id"],
            access_hash=log_data["access_hash"],
            first_name=log_data["first_name"],
            last_name=log_data["last_name"],
            phone=log_data["phone"],
            online_at=log_data["online_at"],
            photo_status=log_data["photo_status"],
            premium_status=log_data["premium_status"],
            user_status=log_data["user_status"],
            bio=log_data["bio"],
            group_name=log_data["group"],
        )

# 458
