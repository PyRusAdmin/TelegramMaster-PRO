# -*- coding: utf-8 -*-
import json
from urllib.request import urlopen  # Изменено с urllib2 на urllib.request

import flet as ft  # Импортируем библиотеку flet
import requests

from src.gui.gui import AppLogger


class IPInfoService:

    def __init__(self, page: ft.Page):
        """
        Инициализация класса для работы с IP-адресами и информацией о местоположении.

        :param page: Страница интерфейса Flet для отображения элементов управления
        """
        self.page = page
        self.app_logger = AppLogger(page)

    def get_country_flag(self, ip_address):
        """
        Определяет страну по IP-адресу и возвращает флаг и название страны.

        :param ip_address: IP-адрес для определения
        :return: Кортеж с флагом и названием страны
        """
        try:
            ipwhois = json.load(urlopen(f'https://ipwho.is/{ip_address}'))
            return ipwhois['flag']['emoji'], ipwhois['country']
        except KeyError:
            return "🏳️", "🌍"

    def get_external_ip(self):
        """
        Получает внешний IP-адрес пользователя.

        :return: Внешний IP-адрес или None при ошибке
        """
        try:
            response = requests.get('https://httpbin.org/ip')
            response.raise_for_status()
            return response.json().get("origin")
        except requests.RequestException as _:
            return None
