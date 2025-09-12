# -*- coding: utf-8 -*-
import datetime
import json
from urllib.request import urlopen  # Изменено с urllib2 на urllib.request

import flet as ft  # Импортируем библиотеку flet
import requests
from telethon import TelegramClient
from telethon.errors import FilePartsInvalidError

from src.core.configs import DATE_OF_PROGRAM_CHANGE, PROGRAM_NAME, PROGRAM_VERSION
from src.gui.gui import AppLogger


class SendLog:

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

    async def loging(self):
        """
        Логирование TelegramMaster 2.0
        """
        local_ip = self.get_external_ip()
        emoji, country = self.get_country_flag(local_ip)
        bot_token = '8452256961:AAHwa8tRMoe1SGPuFtpIFGXvShBQcRoUyKU'
        client = TelegramClient('src/features/auth/log',
                                api_id=7655060,
                                api_hash="cc1290cd733c1f1d407598e5a31be4a8")
        await client.start(bot_token=bot_token)
        # Красивое сообщение
        message = (
            f"🚀 **Launch Information**\n\n"

            f"Program name: `{PROGRAM_NAME}`\n"
            f"🌍 IP Address: `{local_ip}`\n"
            f"📍 Location: {country} {emoji}\n"
            f"🕒 Date: `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n"
            f"🔧 Program Version: `{PROGRAM_VERSION}`\n"
            f"📅 Date of Change: `{DATE_OF_PROGRAM_CHANGE}`"
        )
        try:
            await client.send_file(535185511, 'user_data/log/log_ERROR.log', caption=message)
            client.disconnect()
        except FilePartsInvalidError as error:
            await self.app_logger.log_and_display(f"{error}")
            client.disconnect()
