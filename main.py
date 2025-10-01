# -*- coding: utf-8 -*-
import flet as ft
from loguru import logger

from src.core.checking_program import CheckingProgram
from src.core.configs import (PROGRAM_NAME, PROGRAM_VERSION, DATE_OF_PROGRAM_CHANGE, WINDOW_WIDTH,
                              WINDOW_HEIGHT, WINDOW_RESIZABLE, TIME_SENDING_MESSAGES_1, time_sending_messages_2)
from src.core.sqlite_working_tools import create_database
from src.features.account.account_bio import AccountBIO
from src.features.account.connect import TGConnect
from src.features.account.contact import TGContact
from src.features.account.creating import CreatingGroupsAndChats
from src.features.account.inviting import InvitingToAGroup
from src.features.account.parsing.parsing import ParsingGroupMembers
from src.features.account.reactions import WorkingWithReactions
from src.features.account.sending_messages import SendTelegramMessages
from src.features.account.subscribe_unsubscribe.subscribe_unsubscribe import SubscribeUnsubscribeTelegram
from src.features.account.viewing_posts import ViewingPosts
from src.features.auth.logging_in import SendLog
from src.features.recording.receiving_and_recording import ReceivingAndRecording
from src.features.settings.setting import SettingPage
from src.gui.gui import AppLogger
from src.gui.menu import Menu

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
    connect = TGConnect(page=page)
    creating_groups_and_chats = CreatingGroupsAndChats(page=page)
    subscribe_unsubscribe_telegram = SubscribeUnsubscribeTelegram(page=page)
    working_with_reactions = WorkingWithReactions(page=page)
    parsing_group_members = ParsingGroupMembers(page=page)
    viewing_posts = ViewingPosts(page=page)
    receiving_and_recording = ReceivingAndRecording()
    tg_contact = TGContact(page=page)
    send_telegram_messages = SendTelegramMessages(page=page)
    checking_program = CheckingProgram(page=page)

    async def route_change(_):
        page.views.clear()
        # ______________________________________________________________________________________________________________
        await menu.main_menu_program()  # Главное меню программы
        # ______________________________________________________________________________________________________________
        if page.route == "/inviting":  # Меню "🚀 Инвайтинг"
            # TODO миграция на Peewee. вернуть проверку на наличие аккаунтов, username, ссылки на инвайтинг
            await InvitingToAGroup(page=page).inviting_menu()
        # ______________________________________________________________________________________________________________
        elif page.route == "/account_verification_menu":  # 🔍 Проверка аккаунтов
            await menu.check_menu()
        elif page.route == "/checking_for_spam_bots":  # 🤖 Проверка через спам бот
            await connect.check_for_spam()
        elif page.route == "/validation_check":  # ✅ Проверка на валидность
            await connect.validation_check()
        elif page.route == "/renaming_accounts":  # ✏️ Переименование аккаунтов
            await connect.renaming_accounts()
        elif page.route == "/full_verification":  # 🔍 Полная проверка
            await connect.full_verification()
        # ______________________________________________________________________________________________________________
        elif page.route == "/subscribe_unsubscribe":  # Меню "Подписка и отписка"
            await subscribe_unsubscribe_telegram.subscribe_and_unsubscribe_menu()
        # ______________________________________________________________________________________________________________
        elif page.route == "/working_with_reactions":  # Меню "Работа с реакциями"
            await menu.reactions_menu()
        elif page.route == "/setting_reactions":  # Ставим реакции
            start = await app_logger.start_time()
            logger.info("▶️ Начало Проставления реакций")
            await working_with_reactions.send_reaction_request(page=page)
            logger.info("🔚 Конец Проставления реакций")
            await app_logger.end_time(start)
        elif page.route == "/automatic_setting_of_reactions":  # Автоматическое выставление реакций
            start = await app_logger.start_time()
            logger.info("▶️ Начало Автоматического выставления реакций")
            await working_with_reactions.setting_reactions()
            logger.info("🔚 Конец Автоматического выставления реакций")
            await app_logger.end_time(start)
        # ______________________________________________________________________________________________________________
        elif page.route == "/viewing_posts_menu":  # ️‍🗨️ Накручиваем просмотры постов
            await viewing_posts.viewing_posts_request()
        # ______________________________________________________________________________________________________________
        elif page.route == "/parsing":  # Меню "Парсинг"
            await parsing_group_members.account_selection_menu()
        # ______________________________________________________________________________________________________________
        elif page.route == "/importing_a_list_of_parsed_data":  # 📋 Импорт списка от ранее спарсенных данных
            await receiving_and_recording.write_data_to_excel(file_name="user_data/parsed_chat_participants.xlsx")
        # ______________________________________________________________________________________________________________
        elif page.route == "/working_with_contacts":  # Меню "Работа с контактами"
            await tg_contact.working_with_contacts_menu()
        # ______________________________________________________________________________________________________________
        elif page.route == "/account_connection_menu":  # Подключение аккаунтов 'меню'.
            await connect.account_connection_menu()
        # ______________________________________________________________________________________________________________
        elif page.route == "/creating_groups":  # Создание групп (чатов)
            await creating_groups_and_chats.creating_groups_and_chats()
        # ______________________________________________________________________________________________________________
        elif page.route == "/sending_messages_files_via_chats":  # 💬 Рассылка сообщений по чатам
            await checking_program.check_before_sending_messages_via_chats()
            await send_telegram_messages.sending_messages_files_via_chats()
        elif page.route == "/sending_files_to_personal_account_with_limits":  # Отправка сообщений в личку
            await send_telegram_messages.send_files_to_personal_chats()
        # ______________________________________________________________________________________________________________
        elif page.route == "/bio_editing":  # Меню "Редактирование_BIO"
            await account_bio.bio_editing_menu()
        # ______________________________________________________________________________________________________________
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
    # 192
