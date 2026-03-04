# -*- coding: utf-8 -*-
import time
import webbrowser
from multiprocessing import Process

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger

# Импорт необходимых переменных и функций
from src.core.configs import (
    PROGRAM_NAME, PROGRAM_VERSION, DATE_OF_PROGRAM_CHANGE, path_folder_database
)
from src.locales.translations_loader import translations

app = FastAPI()

# Указываем путь к статическим файлам
app.mount(path="/static", app=StaticFiles(directory="docs/static"), name="static")
templates = Jinja2Templates(directory="docs/templates")  # Указываем директорию с шаблонами.


@app.get(path="/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница документации"""
    logger.info("Запущена главная страница документации")
    try:
        return templates.TemplateResponse(
            "index.html", {
                "request": request,
                "program_name": PROGRAM_NAME
            }
        )
    except Exception as error:
        logger.exception(error)
        return {"error": "Failed to render template"}


@app.get(path='/message_recording', response_class=HTMLResponse)
async def message_recording(request: Request):
    """Запись сообщений"""
    logger.info("Запущена страница — Запись сообщений")
    return templates.TemplateResponse(
        'message_recording.html', {
            "request": request,
            "program_name": PROGRAM_NAME,
            "message_recording": translations["ru"]["menu_settings"]["message_recording"],
        }
    )


@app.get(path="/menu", response_class=HTMLResponse)
async def menu(request: Request):
    """Меню программы"""
    logger.info("Запущено меню программы")
    return templates.TemplateResponse(
        "menu.html", {
            "request": request,
            "program_name": PROGRAM_NAME,
            "program_version": PROGRAM_VERSION,
            "update_date": DATE_OF_PROGRAM_CHANGE,
            "subscribe_unsubscribe": translations["ru"]["menu"]["subscribe_unsubscribe"],
            "importing_a_list_of_parsed_data": translations["ru"]["parsing_menu"]["importing_a_list_of_parsed_data"],
            "account_connect": translations["ru"]["menu"]["account_connect"]
        }
    )


@app.get(path="/inviting", response_class=HTMLResponse)
async def inviting_page(request: Request):
    """🚀 Инвайтинг"""
    logger.info("Запущена страница инвайтинга")
    return templates.TemplateResponse(
        "inviting.html", {
            "request": request,
            "program_name": PROGRAM_NAME,
            "inviting": translations["ru"]["inviting_menu"]["inviting"],
            "invitation_1_time_per_hour": translations["ru"]["inviting_menu"]["invitation_1_time_per_hour"],
            "invitation_at_a_certain_time": translations["ru"]["inviting_menu"]["invitation_at_a_certain_time"],
            "inviting_every_day": translations["ru"]["inviting_menu"]["inviting_every_day"]
        }
    )


# Рассылка сообщений по чатам, в личку
@app.get(path='/sending_messages', response_class=HTMLResponse)
async def sending_messages(request: Request):
    """💬 Рассылка сообщений"""
    try:
        logger.info("Запущено страница рассылки сообщений")
        return templates.TemplateResponse(
            'sending_messages.html', {
                "request": request,
                "program_name": PROGRAM_NAME,
                "sending_messages_via_chats": translations["ru"]["message_sending_menu"]["sending_messages_via_chats"],
                "sending_personal_messages_with_limits": translations["ru"]["message_sending_menu"][
                    "sending_personal_messages_with_limits"],
            }
        )
    except Exception as error:
        logger.exception(error)


@app.get(path='/editing_bio', response_class=HTMLResponse)
async def editing_bio(request: Request):
    """Редактирование BIO"""
    logger.info("Запущена страница редактирования БИО")
    return templates.TemplateResponse(
        'editing_bio.html', {
            "request": request,
            "program_name": PROGRAM_NAME,
            "changing_the_username": translations["ru"]["edit_bio_menu"]["changing_the_username"],
            "changing_the_photo": translations["ru"]["edit_bio_menu"]["changing_the_photo"],
            "changing_the_description": translations["ru"]["edit_bio_menu"]["changing_the_description"],
            "name_change_n": translations["ru"]["edit_bio_menu"]["name_change_n"],
            "name_change_f": translations["ru"]["edit_bio_menu"]["name_change_f"],
        }
    )


@app.get(path='/working_with_contacts', response_class=HTMLResponse)
async def working_with_contacts(request: Request):
    """
    Работа с контактами

    :param request: Request
    :return: HTMLResponse
    """
    logger.info("Запущена страница работы с контактами")
    return templates.TemplateResponse(
        'working_with_contacts.html', {
            "request": request,
            "program_name": PROGRAM_NAME,
            "creating_a_contact_list": translations["ru"]["contacts_menu"]["creating_a_contact_list"],
            "show_a_list_of_contacts": translations["ru"]["contacts_menu"]["show_a_list_of_contacts"],
            "deleting_contacts": translations["ru"]["contacts_menu"]["deleting_contacts"],
            "adding_contacts": translations["ru"]["contacts_menu"]["adding_contacts"],
            "working_with_contacts_menu": translations["ru"]["menu"]["contacts"],
            "path_folder_database": path_folder_database
        }
    )


@app.get(path='/settings', response_class=HTMLResponse)
async def settings(request: Request):
    """
    ⚙️ Настройки

    :param request: Request
    :return: HTMLResponse
    """
    logger.info("Запущена страница настроек")
    return templates.TemplateResponse(
        'settings.html', {
            "request": request,
            "program_name": PROGRAM_NAME,
            "choice_of_reactions": translations["ru"]["menu_settings"]["choice_of_reactions"],
            "proxy_entry": translations["ru"]["menu_settings"]["proxy_entry"],
            "recording_api_id_api_hash": translations["ru"]["menu_settings"]["recording_api_id_api_hash"],
            "message_recording": translations["ru"]["menu_settings"]["message_recording"],
            "recording_reaction_link": translations["ru"]["menu_settings"]["recording_reaction_link"],
        }
    )


# Работа с реакциями

@app.get(path='/working_with_reactions', response_class=HTMLResponse)
async def working_with_reactions(request: Request):
    """👍 Работа с реакциями"""
    logger.info("Запущена страница работы с реакциями")
    return templates.TemplateResponse(
        'working_with_reactions.html', {
            "request": request,
            "program_name": PROGRAM_NAME,
            "setting_reactions": translations["ru"]["reactions_menu"]["setting_reactions"],
            "we_are_winding_up_post_views": translations["ru"]["reactions_menu"]["we_are_winding_up_post_views"],
            "automatic_setting_of_reactions": translations["ru"]["reactions_menu"]["automatic_setting_of_reactions"],
            "recording_reaction_link": translations["ru"]["menu_settings"]["recording_reaction_link"],
        }
    )


@app.get(path='/we_are_winding_up_post_views', response_class=HTMLResponse)
async def we_are_winding_up_post_views(request: Request):
    """👁️‍🗨️ Накручиваем просмотры постов"""
    logger.info("Запущена страница '👁️‍🗨️ Накручиваем просмотры постов' ")
    return templates.TemplateResponse(
        'we_are_winding_up_post_views.html', {
            "request": request,
            "program_name": PROGRAM_NAME,
            "setting_reactions": translations["ru"]["reactions_menu"]["setting_reactions"],
            "we_are_winding_up_post_views": translations["ru"]["reactions_menu"]["we_are_winding_up_post_views"],
            "automatic_setting_of_reactions": translations["ru"]["reactions_menu"]["automatic_setting_of_reactions"],
        }
    )


@app.get(path='/parsing', response_class=HTMLResponse)
async def parsing(request: Request):
    """🔍 Парсинг"""
    logger.info("Запущена страница парсинга")
    return templates.TemplateResponse(
        'parsing.html', {
            "request": request,
            "program_name": PROGRAM_NAME,
            "parse_single_or_multiple_groups": translations["ru"]["parsing_menu"]["parse_single_or_multiple_groups"],
            "parse_selected_user_subscribed_group": translations["ru"]["parsing_menu"][
                "parse_selected_user_subscribed_group"],
            "parse_active_group_members": translations["ru"]["parsing_menu"]["parse_active_group_members"],
            "parse_account_subscribed_groups_channels": translations["ru"]["parsing_menu"][
                "parse_account_subscribed_groups_channels"],
            "importing_a_list_of_parsed_data": translations["ru"]["parsing_menu"]["importing_a_list_of_parsed_data"]
        }
    )


@app.get(path='/subscribe_unsubscribe', response_class=HTMLResponse)
async def subscribe_unsubscribe(request: Request):
    """Подписка, отписка"""
    logger.info("Запущена страница подписки, отписки")
    return templates.TemplateResponse(
        'subscribe_unsubscribe.html', {
            "request": request,
            "program_name": PROGRAM_NAME,
            "subscription": translations["ru"]["subscribe_unsubscribe_menu"]["subscription"],
            "unsubscribe": translations["ru"]["subscribe_unsubscribe_menu"]["unsubscribe"],
            "subscribe_unsubscribe": translations["ru"]["menu"]["subscribe_unsubscribe"],
        }
    )


@app.get(path='/connect_accounts', response_class=HTMLResponse)
async def connect_accounts(request: Request):
    """Подключение аккаунтов"""
    logger.info("Запущена страница подключения аккаунтов")
    return templates.TemplateResponse(
        'connect_accounts.html', {
            "request": request,
            "program_name": PROGRAM_NAME,
            "connecting_accounts_by_phone_number": translations["ru"]["account_connect_menu"][
                "connecting_accounts_by_phone_number"],
            "connecting_session_accounts": translations["ru"]["account_connect_menu"]["connecting_session_accounts"],
            "delete_connected_accounts": translations["ru"]["account_connect_menu"]["delete_connected_accounts"],
            "account_connect": translations["ru"]["menu"]["account_connect"]
        }
    )


@app.get(path='/account_verification', response_class=HTMLResponse)
async def account_verification(request: Request):
    """Проверка аккаунтов"""
    logger.info("Запущена страница проверки аккаунтов")
    return templates.TemplateResponse(
        'account_verification.html', {
            "request": request,
            "program_name": PROGRAM_NAME
        }
    )


@app.get(path='/creating_groups', response_class=HTMLResponse)
async def creating_groups(request: Request):
    """Создание групп (чатов)"""
    logger.info("Запущена страница создания групп (чатов)")
    return templates.TemplateResponse(
        'creating_groups.html', {
            "request": request,
            "program_name": PROGRAM_NAME,
            "create_groups": translations["ru"]["menu"]["create_groups"],
        }
    )


@app.get(path='/launch_telegrammaster', response_class=HTMLResponse)
async def launch_telegrammaster(request: Request):
    """Запуск TelegramMaster"""
    logger.info("Запущена страница документации, о запуске TelegramMaster-PRO")
    return templates.TemplateResponse(
        'launch_telegrammaster.html', {
            "request": request,
            "program_name": PROGRAM_NAME
        }
    )


@app.get(path='/working_with_errors_telegrammaster', response_class=HTMLResponse)
async def working_with_errors_telegrammaster(request: Request):
    """Работа с ошибками TelegramMaster-PRO"""
    logger.info("Запущена страница документации, о работе с ошибками TelegramMaster-PRO")
    return templates.TemplateResponse(
        'working_with_errors_telegrammaster.html', {
            "request": request,
            "program_name": PROGRAM_NAME
        }
    )


@app.get(path='/install_python_update_pip', response_class=HTMLResponse)
async def install_python_update_pip(request: Request):
    """Установка Python, обновление PIP"""
    logger.info("Запущена страница документации, о установке Python, обновлении PIP")
    return templates.TemplateResponse(
        'install_python_update_pip.html', {
            "request": request,
            "program_name": PROGRAM_NAME
        }
    )


@app.get(path='/preliminary_setting_of_program_installation_of_program_by_default', response_class=HTMLResponse)
async def preliminary_setting_of_program_installation_of_program_by_default(request: Request):
    """Предварительная настройка программы"""
    logger.info(
        "Запущена страница документации, о предварительной настройке программы, установке программы по умолчанию")
    return templates.TemplateResponse(
        'preliminary_setting_of_program_installation_of_program_by_default.html', {
            "request": request,
            "program_name": PROGRAM_NAME
        }
    )


@app.get(path='/registration_api_id_api_hash', response_class=HTMLResponse)
async def registration_api_id_api_hash(request: Request):
    """Получение api и hash"""
    logger.info('Запущена страница, о получении api и hash')
    return templates.TemplateResponse(
        'registration_api_id_api_hash.html', {
            "request": request,
            "program_name": PROGRAM_NAME
        }
    )


@app.get(path='/telegram_limits', response_class=HTMLResponse)
async def telegram_limits(request: Request):
    """Лимиты Telegram"""
    logger.info("Запущена страница документации, о лимитах Telegram")
    return templates.TemplateResponse(
        'telegram_limits.html', {
            "request": request,
            "program_name": PROGRAM_NAME
        }
    )


@app.get(path='/importing_a_list_of_parsed_data', response_class=HTMLResponse)
async def importing_a_list_of_parsed_data(request: Request):
    """📋 Импорт списка от ранее спарсенных данных"""
    logger.info("Запущена страница 📋 Импорт списка от ранее спарсенных данных")
    return templates.TemplateResponse(
        'importing_a_list_of_parsed_data.html', {
            "request": request,
            "program_name": PROGRAM_NAME,
            "importing_a_list_of_parsed_data": translations["ru"]["parsing_menu"]["importing_a_list_of_parsed_data"],
        }
    )


def run_uvicorn():
    """
    Запускает сервер Uvicorn в отдельном процессе.

    """
    logger.info("Запуск сервера FastAPI...")
    uvicorn.run("docs.app:app", host="127.0.0.1", port=8000, reload=True)


def start_app():
    """
    Запускает приложение, включая сервер FastAPI и открывает браузер.
    """
    try:
        server_process = Process(target=run_uvicorn)
        server_process.start()
        time.sleep(10)
        # Открытие браузера после задержки, чтобы сервер успел запуститься.
        webbrowser.open("http://127.0.0.1:8000")
        server_process.join()  # Ждем завершения процесса
    except Exception as error:
        logger.exception(error)

# 446
