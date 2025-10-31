# -*- coding: utf-8 -*-
import json
from urllib.request import urlopen  # Изменено с urllib2 на urllib.request

import flet as ft  # Импортируем библиотеку flet
import requests

from src.gui.gui import AppLogger


class IPInfoService:

    def __init__(self, page: ft.Page):
        self.page = page
        self.app_logger = AppLogger(page)

    def get_country_flag(self, ip_address):
        """
        Определение страны по ip адресу на основе сервиса https://ipwhois.io/ru/documentation.
        Возвращает флаг и название страны.
        :param ip_address: IP адрес
        :return: флаг и название страны
        """
        try:
            ipwhois = json.load(urlopen(f'https://ipwho.is/{ip_address}'))
            return ipwhois['flag']['emoji'], ipwhois['country']
        except KeyError:
            return "🏳️", "🌍"

    def get_external_ip(self):
        """Получение внешнего ip адреса"""
        try:
            response = requests.get('https://httpbin.org/ip')
            response.raise_for_status()
            return response.json().get("origin")
        except requests.RequestException as _:
            return None
