# -*- coding: utf-8 -*-
import flet as ft
from loguru import logger

from src.core.checking_program import CheckingProgram
from src.core.configs import (PROGRAM_NAME, PROGRAM_VERSION, DATE_OF_PROGRAM_CHANGE, WINDOW_WIDTH,
                              WINDOW_HEIGHT, WINDOW_RESIZABLE, TIME_SENDING_MESSAGES_1, time_sending_messages_2)
from src.core.sqlite_working_tools import create_database, open_and_read_data
from src.features.account.account_bio import AccountBIO
from src.features.account.chek import TGChek
from src.features.account.connect import TGConnect
from src.features.account.contact import TGContact
from src.features.account.creating import CreatingGroupsAndChats
from src.features.account.reactions import WorkingWithReactions
from src.features.account.sending_messages import SendTelegramMessages
from src.features.account.viewing_posts import ViewingPosts
from src.features.account.inviting import InvitingToAGroup
from src.features.account.parsing.parsing import ParsingGroupMembers
from src.features.account.subscribe_unsubscribe.subscribe_unsubscribe import SubscribeUnsubscribeTelegram
from src.features.auth.logging_in import SendLog
from src.features.recording.receiving_and_recording import ReceivingAndRecording
from src.features.settings.setting import SettingPage
from src.gui.gui import AppLogger
from src.gui.menu import Menu
from src.gui.notification import show_notification

logger.add("user_data/log/log_ERROR.log", rotation="500 KB", compression="zip", level="ERROR")  # Логирование программы


async def main(page: ft.Page):
    """
    Главное меню программы

    Аргументы:
    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    await SendLog(page=page).loging()

    create_database()  # Создание базы данных

    page.title = f"{PROGRAM_NAME}: {PROGRAM_VERSION} (Дата изменения {DATE_OF_PROGRAM_CHANGE})"
    page.window.width = WINDOW_WIDTH  # Ширина окна
    page.window.height = WINDOW_HEIGHT  # Высота окна
    page.window.resizable = WINDOW_RESIZABLE  # Разрешение изменения размера окна
    app_logger = AppLogger(page=page)
    setting_page = SettingPage(page=page)
    account_bio = AccountBIO(page=page)
    menu = Menu(page=page)

    async def route_change(_):
        page.views.clear()
        # ______________________________________________________________________________________________________________
        await menu.main_menu_program()  # Главное меню программы
        # ______________________________________________________________________________________________________________
        if page.route == "/inviting":  # Меню "🚀 Инвайтинг"
            # TODO миграция на Peewee. вернуть проверку на наличие аккаунтов, username, ссылки на инвайтинг
            await InvitingToAGroup(page=page).inviting_menu()
        # __________________________________________________________________________________________________________
        elif page.route == "/account_verification_menu":  # "Проверка аккаунтов"
            await TGChek(page=page).account_verification_menu()
        # __________________________________________________________________________________________________________
        elif page.route == "/subscribe_unsubscribe":  # Меню "Подписка и отписка"
            await SubscribeUnsubscribeTelegram(page=page).subscribe_and_unsubscribe_menu()
        # __________________________________________________________________________________________________________
        elif page.route == "/working_with_reactions":  # Меню "Работа с реакциями"
            await menu.reactions_menu()
        elif page.route == "/setting_reactions":  # Ставим реакции
            start = await app_logger.start_time()
            logger.info("▶️ Начало Проставления реакций")
            await WorkingWithReactions(page=page).send_reaction_request(page=page)
            logger.info("🔚 Конец Проставления реакций")
            await app_logger.end_time(start)
        elif page.route == "/automatic_setting_of_reactions":  # Автоматическое выставление реакций
            start = await app_logger.start_time()
            logger.info("▶️ Начало Автоматического выставления реакций")
            await WorkingWithReactions(page=page).setting_reactions()
            logger.info("🔚 Конец Автоматического выставления реакций")
            await app_logger.end_time(start)
        # __________________________________________________________________________________________________________
        elif page.route == "/viewing_posts_menu":  # ️‍🗨️ Накручиваем просмотры постов
            await ViewingPosts(page=page).viewing_posts_request()
        # __________________________________________________________________________________________________________
        elif page.route == "/parsing":  # Меню "Парсинг"
            await ParsingGroupMembers(page=page).account_selection_menu()
        # __________________________________________________________________________________________________________
        elif page.route == "/importing_a_list_of_parsed_data":  # 📋 Импорт списка от ранее спарсенных данных
            await ReceivingAndRecording().write_data_to_excel(file_name="user_data/parsed_chat_participants.xlsx")
        # __________________________________________________________________________________________________________
        elif page.route == "/working_with_contacts":  # Меню "Работа с контактами"
            await menu.working_with_contacts_menu()
        elif page.route == "/creating_contact_list":  # Формирование списка контактов
            start = await app_logger.start_time()
            logger.info("▶️ Начало Формирования списка контактов")
            open_and_read_data(table_name="contact")  # Удаление списка с контактами
            # TODO миграция на PEEWEE
            await setting_page.output_the_input_field(page=page, table_name="contact",
                                                      column_name="contact", route="/working_with_contacts",
                                                      into_columns="contact")
            logger.info("🔚 Конец Формирования списка контактов")
            await app_logger.end_time(start)
        elif page.route == "/show_list_contacts":  # Показать список контактов
            start = await app_logger.start_time()
            logger.info("▶️ Начало Показа списка контактов")
            await TGContact(page=page).show_account_contact_list()
            logger.info("🔚 Конец Показа списка контактов")
            await app_logger.end_time(start)
        elif page.route == "/deleting_contacts":  # Удаление контактов
            start = await app_logger.start_time()
            logger.info("▶️ Начало Удаления контактов")
            await TGContact(page=page).delete_contact()
            logger.info("🔚 Конец Удаления контактов")
            await app_logger.end_time(start)
        elif page.route == "/adding_contacts":  # Добавление контактов
            start = await app_logger.start_time()
            logger.info("▶️ Начало Добавления контактов")
            await TGContact(page=page).inviting_contact()
            logger.info("🔚 Конец Добавления контактов")
            await app_logger.end_time(start)
        # __________________________________________________________________________________________________________
        elif page.route == "/account_connection_menu":  # Подключение аккаунтов 'меню'.
            await TGConnect(page=page).account_connection_menu()
        # __________________________________________________________________________________________________________
        elif page.route == "/creating_groups":  # Создание групп (чатов)
            await CreatingGroupsAndChats(page=page).creating_groups_and_chats()
        # __________________________________________________________________________________________________________
        elif page.route == "/sending_messages_files_via_chats":  # 💬 Рассылка сообщений по чатам
            await CheckingProgram(page=page).check_before_sending_messages_via_chats()
            await SendTelegramMessages(page=page).sending_messages_files_via_chats()

        elif page.route == "/sending_files_to_personal_account_with_limits":  # Отправка сообщений в личку
            await SendTelegramMessages(page=page).send_files_to_personal_chats()
        # __________________________________________________________________________________________________________
        elif page.route == "/bio_editing":  # Меню "Редактирование_BIO"
            await menu.bio_editing_menu()
        elif page.route == "/edit_description":  # Изменение описания
            await account_bio.change_bio_profile_gui()
        elif page.route == "/name_change":  # Изменение имени профиля Telegram
            await account_bio.change_name_profile_gui()
        elif page.route == "/change_surname":  # Изменение фамилии
            await account_bio.change_last_name_profile_gui()
        elif page.route == "/edit_photo":  # Изменение фото
            await account_bio.change_photo_profile_gui()
            await show_notification(page=page, message="🔚 Фото изменено")  # Выводим уведомление пользователю
        elif page.route == "/changing_username":  # Изменение username
            await account_bio.change_username_profile_gui()
        # __________________________________________________________________________________________________________
        elif page.route == "/settings":  # Меню "Настройки TelegramMaster"
            await menu.settings_menu()
        elif page.route == "/choice_of_reactions":  # 👍 Выбор реакций
            await setting_page.reaction_gui()
        elif page.route == "/proxy_entry":  # 🔐 Запись proxy
            await setting_page.creating_the_main_window_for_proxy_data_entry()
        elif page.route == "/recording_api_id_api_hash":  # 📝 Запись api_id, api_hash
            await setting_page.writing_api_id_api_hash()
        elif page.route == "/message_recording":  # ✉️ Запись сообщений
            await setting_page.recording_text_for_sending_messages("Введите текст для сообщения",
                                                                   setting_page.get_unique_filename(
                                                                       base_filename='user_data/message/message'))
        elif page.route == "/recording_reaction_link":  # Запись ссылки для реакций
            await setting_page.recording_text_for_sending_messages("Введите ссылку для реакций",
                                                                   'user_data/reactions/link_channel.json')
        elif page.route == "/recording_the_time_between_messages":  # Запись времени между сообщениями
            await setting_page.create_main_window(variable="time_sending_messages",
                                                  smaller_timex=TIME_SENDING_MESSAGES_1,
                                                  larger_timex=time_sending_messages_2)
        page.update()

    def view_pop(_):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


if __name__ == '__main__':
    ft.app(target=main)
