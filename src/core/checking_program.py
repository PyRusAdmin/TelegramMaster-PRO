# -*- coding: utf-8 -*-
import flet as ft

from src.core.configs import LIMITS
from src.core.sqlite_working_tools import select_records_with_limit
from src.core.utils import Utils
from src.gui.notification import show_notification


class CheckingProgram:
    """⛔ Проверка программы от пользователя"""

    def __init__(self, page: ft.Page):
        """
        Инициализация экземпляра класса CheckingProgram
        :param page: Объект страницы ft.Page
        """
        self.page = page
        self.account_extension = "session"  # Расширение файла аккаунта
        self.file_extension = "json"
        self.utils = Utils(page=page)

    async def check_before_sending_messages_via_chats(self):
        """
        ⛔ Проверка наличия сформированного списка с чатами для рассылки по чатам.
        ⛔ Проверка папки с сообщениями на наличие заготовленных сообщений.
        """
        if len(select_records_with_limit(limit=LIMITS)) == 0:
            await show_notification(page=self.page, message="⛔ Не сформирован список для рассылки по чатам")

    # async def check_before_inviting(page: ft.Page):
    #     """
    #     ⛔ Проверка наличия пользователя в списке участников, наличия аккаунта, наличия ссылки в базе данных
    #     :param page: Страница интерфейса Flet для отображения элементов управления.
    #     """
    #     if len(select_records_with_limit(limit=limits)) == 0:
    #         await show_notification(page, "⛔ В таблице members нет пользователей для инвайтинга")
    #     if len(await select_records_with_limit(table_name="links_inviting", limit=limits)) == 0:
    #         await show_notification(page, "⛔ Не записана группа для инвайтинга")

    # async def checking_sending_messages_via_chats_with_answering_machine(self):
    #     """
    #     ⛔ Проверка наличия аккаунта в папке с аккаунтами (Рассылка сообщений по чатам с автоответчиком)
    #     """
    #     if not self.utils.find_filess(directory_path=path_folder_with_messages, extension=self.file_extension):
    #         await show_notification(page=self.page,
    #                                 message=f"⛔ Нет заготовленных сообщений в папке {path_folder_with_messages}")
    #     if not self.utils.find_filess(directory_path=path_send_message_folder_answering_machine_message,
    #                                   extension=self.file_extension):
    #         await show_notification(
    #             page=self.page,
    #             message=f"⛔ Нет заготовленных сообщений для автоответчика в папке {path_send_message_folder_answering_machine_message}")
    #     if len(await select_records_with_limit(table_name="writing_group_links", limit=LIMITS)) == 0:
    #         await show_notification(
    #             page=self.page, message="⛔ Не сформирован список для рассылки по чатам")
