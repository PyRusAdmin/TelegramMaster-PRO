# -*- coding: utf-8 -*-
import random

import flet as ft
import requests
from loguru import logger

from src.core.database.database import deleting_an_invalid_proxy, get_proxy_database
from src.gui.gui import AppLogger


class Proxy:
    """
    Класс для проверки работоспособности прокси-серверов и работы с прокси из базы данных.
    """

    def __init__(self, page: ft.Page):
        """
        Инициализация класса для проверки работоспособности прокси-серверов.

        :param page: Страница интерфейса Flet для отображения элементов управления
        """
        self.page = page
        self.app_logger = AppLogger(page=page)

    def reading_proxy_data_from_the_database(self):
        """
        Считывает данные прокси из базы данных.

        :return: Словарь с данными прокси или None при ошибке
        """
        try:
            proxy_random_list = random.choice(get_proxy_database())
            proxy = {'proxy_type': (proxy_random_list[0]), 'addr': proxy_random_list[1],
                     'port': int(proxy_random_list[2]),
                     'username': proxy_random_list[3], 'password': proxy_random_list[4], 'rdns': proxy_random_list[5]}
            return proxy
        except IndexError:
            proxy = None
            return proxy
        except Exception as error:
            logger.exception(error)
            return None

    async def checking_the_proxy_for_work(self) -> None:
        """
        Проверяет работоспособность всех прокси из базы данных.

        :return: None
        """
        try:
            for proxy_dic in get_proxy_database():
                await self.app_logger.log_and_display(message=f"{proxy_dic}")
                # Подключение к proxy с проверкой на работоспособность
                await self.connecting_to_proxy_with_verification(proxy_type=proxy_dic[0],
                                                                 # Тип proxy (например: SOCKS5)
                                                                 addr=proxy_dic[1],  # Адрес (например: 194.67.248.9)
                                                                 port=proxy_dic[2],  # Порт (например: 9795)
                                                                 username=proxy_dic[3],  # Логин (например: username)
                                                                 password=proxy_dic[4],  # Пароль (например: password)
                                                                 rdns=proxy_dic[5])
        except Exception as error:
            logger.exception(error)

    async def connecting_to_proxy_with_verification(self, proxy_type, addr, port, username, password, rdns) -> None:
        """
        Подключается к прокси-серверу с проверкой его работоспособности.

        :param proxy_type: Тип прокси (например: SOCKS5)
        :param addr: Адрес прокси (например: 194.67.248.9)
        :param port: Порт прокси (например: 9795)
        :param username: Логин для аутентификации
        :param password: Пароль для аутентификации
        :param rdns: Параметр rdns
        :return: None
        """
        # Пробуем подключиться по прокси
        try:
            # Указываем параметры прокси
            proxy = {'http': f'{proxy_type}://{username}:{password}@{addr}:{port}'}
            await self.app_logger.log_and_display(
                message=f"Проверяемый прокси: {proxy_type}://{username}:{password}@{addr}:{port}.")
            requests.get('http://example.org', proxies=proxy)
            await self.app_logger.log_and_display(
                message=f"⚠️ Proxy: {proxy_type}://{username}:{password}@{addr}:{port} рабочий!")
        # RequestException исключение возникает при ошибках, которые могут быть вызваны при запросе к веб-серверу.
        # Это может быть из-за недоступности сервера, ошибочного URL или других проблем с соединением.
        except requests.exceptions.RequestException:
            await self.app_logger.log_and_display(message=f"❌ Proxy не рабочий!")
            await deleting_an_invalid_proxy(proxy_type=proxy_type, addr=addr, port=port, username=username,
                                            password=password, rdns=rdns, page=self.page)
        except Exception as error:
            logger.exception(error)
