# -*- coding: utf-8 -*-
import os
import os.path
import sqlite3
import time

from loguru import logger
from telethon import TelegramClient
from telethon.errors import AuthKeyDuplicatedError, PhoneNumberBannedError, UserDeactivatedBanError, TimedOutError, \
    AuthKeyNotFound, TypeNotFoundError, AuthKeyUnregisteredError
from telethon.errors import YouBlockedUserError
from telethon.tl.functions.users import GetFullUserRequest
from thefuzz import fuzz

from system.account_actions.TGConnect import TGConnect
from system.auxiliary_functions.auxiliary_functions import find_files, working_with_accounts
from system.auxiliary_functions.global_variables import ConfigReader
from system.proxy.checking_proxy import checking_the_proxy_for_work


async def renaming_a_session(client, phone_old, phone, directory_path) -> None:
    """
    Переименование session файлов
    :param client: клиент для работы с Telegram
    :param phone_old: номер телефона для переименования
    :param phone: номер телефона для переименования
    :param directory_path: путь к каталогу с файлами
    """
    await client.disconnect()  # Отключаемся от аккаунта для освобождения session файла
    try:
        # Переименование session файла
        os.rename(f"{directory_path}/{phone_old}.session", f"{directory_path}/{phone}.session", )
    except FileExistsError:
        # Если файл существует, то удаляем дубликат
        os.remove(f"{directory_path}/{phone_old}.session")


async def account_name(client, name_account, directory_path, session):
    """
    Показываем имя аккаунта с которого будем взаимодействовать
    :param client: клиент для работы с Telegram
    :param name_account: имя аккаунта для проверки аккаунта
    :param directory_path: путь к файлу
    :param session: имя session файла
    """
    try:
        full = await client(GetFullUserRequest(name_account))
        for user in full.users:
            first_name = user.first_name if user.first_name else ""
            last_name = user.last_name if user.last_name else ""
            phone = user.phone if user.phone else ""
            return first_name, last_name, phone
    except TypeNotFoundError:
        await client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
        logger.error(f"⛔ Битый файл или аккаунт забанен {session.split('/')[-1]}.session, возможно запущен под другим ip")
        working_with_accounts(account_folder=f"{directory_path}/{session.split('/')[-1]}.session",
                              new_account_folder=f"user_settings/accounts/invalid_account/{session.split('/')[-1]}.session")
    except AuthKeyUnregisteredError:
        await client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
        logger.error(f"⛔ Битый файл или аккаунт забанен {session.split('/')[-1]}.session, возможно запущен под другим ip")
        working_with_accounts(account_folder=f"{directory_path}/{session.split('/')[-1]}.session",
                              new_account_folder=f"user_settings/accounts/invalid_account/{session.split('/')[-1]}.session")


async def account_verification_for_telegram(directory_path, extension) -> None:
    """
    Проверка аккаунтов Telegram
    :param directory_path: путь к каталогу с аккаунтами
    :param extension: расширение файла с аккаунтами
    """
    logger.info(f"Запуск проверки аккаунтов Telegram из папки 📁: {directory_path}")
    account_verification = AccountVerification()
    tg_connect = TGConnect()
    await checking_the_proxy_for_work()  # Проверка proxy

    # Сканирование каталога с аккаунтами
    entities = find_files(directory_path, extension)
    for entities in entities:
        logger.info(f"⚠️ Проверяемый аккаунт {directory_path}/{entities[0]}")

        # Проверка аккаунтов
        proxy = await tg_connect.reading_proxies_from_the_database()
        await account_verification.account_verification(directory_path, entities[0], proxy)

        # Получение данных аккаунта
        client = await tg_connect.connect_to_telegram(file=entities, directory_path=directory_path)
        try:
            first_name, last_name, phone = await account_name(client, name_account="me", directory_path=directory_path,
                                                              session=entities[0])
            # Выводим результат полученного имени и номера телефона
            logger.info(f"📔 Данные аккаунта {first_name} {last_name} {phone}")

            # Переименовываем сессию
            await renaming_a_session(client, entities[0], phone, directory_path)
        except TypeError as e:
            logger.error(f"TypeError: {e}")  # Ошибка

    logger.info(f"Окончание проверки аккаунтов Telegram из папки 📁: {directory_path}")


class AccountVerification:
    """Проверка аккаунтов Telegram"""

    def __init__(self):
        self.config_reader = ConfigReader()
        self.api_id_api_hash = self.config_reader.get_api_id_data_api_hash_data()
        self.tg_connect = TGConnect()

    async def account_verification(self, directory_path, session, proxy) -> None:
        """
        Проверка и сортировка аккаунтов
        :param directory_path: путь к каталогу с аккаунтами
        :param session: имя аккаунта для проверки аккаунта
        :param proxy: прокси
        """
        # TODO: Рассмотреть использование функции connecting_to_telegram() или объединение с классом TGConnect
        api_id = self.api_id_api_hash[0]
        api_hash = self.api_id_api_hash[1]
        logger.info(f"Проверка аккаунта {session}. Используемые: api_id {api_id}, api_hash {api_hash}")
        client = TelegramClient(f"{directory_path}/{session}", api_id=api_id, api_hash=api_hash,
                                system_version="4.16.30-vxCUSTOM", proxy=proxy)
        try:
            await client.connect()  # Подсоединяемся к Telegram аккаунта
            if not await client.is_user_authorized():  # Если аккаунт не авторизирован, то удаляем сессию
                await client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
                working_with_accounts(account_folder=f"{directory_path}/{session.split('/')[-1]}.session",
                                      new_account_folder=f"user_settings/accounts/invalid_account/{session.split('/')[-1]}.session")
                time.sleep(1)
                return  # Возвращаемся из функции, так как аккаунт не авторизован
            await client.disconnect()  # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
        except AttributeError as e:
            logger.info(f"{e}")
        except (PhoneNumberBannedError, UserDeactivatedBanError, AuthKeyNotFound, sqlite3.DatabaseError,
                AuthKeyUnregisteredError, AuthKeyDuplicatedError):
            client.disconnect()  # Разрываем соединение Telegram, для удаления session файла
            logger.error(
                f"⛔ Битый файл или аккаунт забанен {session.split('/')[-1]}.session, возможно запущен под другим ip")
            working_with_accounts(account_folder=f"{directory_path}/{session.split('/')[-1]}.session",
                                  new_account_folder=f"user_settings/accounts/invalid_account/{session.split('/')[-1]}.session")
        except TimedOutError as e:
            logger.exception(e)
            time.sleep(2)

    async def check_account_for_spam(self, folders) -> None:
        """
        Проверка аккаунта на спам через @SpamBot
        :param folders: папка с аккаунтами
        """
        entities = find_files(directory_path=f"user_settings/accounts/{folders}", extension='session')
        for file in entities:
            client = await self.tg_connect.connect_to_telegram(file, directory_path=f"user_settings/accounts/{folders}")
            try:
                await client.send_message('SpamBot', '/start')  # Находим спам бот, и вводим команду /start
                message_bot = await client.get_messages('SpamBot')
                for message in message_bot:
                    logger.info(f"{file} {message.message}")
                    similarity_ratio_ru: int = fuzz.ratio(f"{message.message}",
                                                          "Очень жаль, что Вы с этим столкнулись. К сожалению, "
                                                          "иногда наша антиспам-система излишне сурово реагирует на "
                                                          "некоторые действия. Если Вы считаете, что Ваш аккаунт "
                                                          "ограничен по ошибке, пожалуйста, сообщите об этом нашим "
                                                          "модераторам. Пока действуют ограничения, Вы не сможете "
                                                          "писать тем, кто не сохранил Ваш номер в список контактов, "
                                                          "а также приглашать таких пользователей в группы или каналы. "
                                                          "Если пользователь написал Вам первым, Вы сможете ответить, "
                                                          "несмотря на ограничения.")
                    if similarity_ratio_ru >= 97:
                        logger.info('⛔ Аккаунт в бане')
                        await client.disconnect()  # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
                        logger.info(f"Проверка аккаунтов через SpamBot. {file[0]}: {message.message}")
                        # Перенос Telegram аккаунта в папку banned, если Telegram аккаунт в бане
                        working_with_accounts(account_folder=f"user_settings/accounts/{folders}/{file[0]}.session",
                                              new_account_folder=f"user_settings/accounts/banned/{file[0]}.session")
                    similarity_ratio_en: int = fuzz.ratio(f"{message.message}",
                                                          "I’m very sorry that you had to contact me. Unfortunately, "
                                                          "some account_actions can trigger a harsh response from our "
                                                          "anti-spam systems. If you think your account was limited by "
                                                          "mistake, you can submit a complaint to our moderators. While "
                                                          "the account is limited, you will not be able to send messages "
                                                          "to people who do not have your number in their phone contacts "
                                                          "or add them to groups and channels. Of course, when people "
                                                          "contact you first, you can always reply to them.")
                    if similarity_ratio_en >= 97:
                        logger.info('⛔ Аккаунт в бане')
                        await client.disconnect()  # Отключаемся от аккаунта, что бы session файл не был занят другим процессом
                        logger.error(f"Проверка аккаунтов через SpamBot. {file[0]}: {message.message}")
                        # Перенос Telegram аккаунта в папку banned, если Telegram аккаунт в бане
                        logger.info(file[0])
                        working_with_accounts(account_folder=f"user_settings/accounts/{folders}/{file[0]}.session",
                                              new_account_folder=f"user_settings/accounts/banned/{file[0]}.session")
                    logger.error(f"Проверка аккаунтов через SpamBot. {file[0]}: {message.message}")
            except YouBlockedUserError:
                continue  # Записываем ошибку в software_database.db и продолжаем работу
            except AttributeError as e:
                logger.error(e)  # Отправляем сообщение в лог
                continue  # Записываем ошибку в software_database.db и продолжаем работу
            except AuthKeyUnregisteredError as e:
                logger.error(e)  # Отправляем сообщение в лог

