# -*- coding: utf-8 -*-
import base64

import flet as ft
from loguru import logger

from src.core.config.configs import (
    PROGRAM_NAME, PROGRAM_VERSION, DATE_OF_PROGRAM_CHANGE, window_width, window_height
)
from src.core.database.create_database import create_database
from src.features.account.account_bio import AccountBIO
from src.features.account.connect import TGConnect
from src.features.account.contact import TGContact
from src.features.account.creating import CreatingGroupsAndChats
from src.features.account.inviting import InvitingToAGroup
from src.features.account.parsing import ParsingGroupMembers
from src.features.account.reactions import WorkingWithReactions
from src.features.account.sending_messages import SendTelegramMessages
from src.features.account.subscribe_unsubscribe import SubscribeUnsubscribeTelegram
from src.features.account.viewing_posts import ViewingPosts
from src.features.recording.receiving_and_recording import ReceivingAndRecording
from src.features.settings.setting import SettingPage
from src.gui.buttons import menu_button
from src.gui.gui_elements import GUIProgram
from src.locales.translations_loader import translations

logger.add("user_data/log/log_INFO.log", rotation="500 KB", compression="zip", level="INFO")
logger.add("user_data/log/log_ERROR.log", rotation="500 KB", compression="zip", level="ERROR")


async def main(page: ft.Page):
    """
    Главное меню программы
    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.title = f"{PROGRAM_NAME}: {PROGRAM_VERSION}"
    page.adaptive = True
    page.window.width = window_width  # Ширина
    page.window.height = window_height  # Высота

    create_database()

    setting_page = SettingPage(page=page)
    account_bio = AccountBIO(page=page)

    connect = TGConnect(page=page)
    creating_groups_and_chats = CreatingGroupsAndChats(page=page)
    subscribe_unsubscribe_telegram = SubscribeUnsubscribeTelegram(page=page)
    working_with_reactions = WorkingWithReactions(page=page)
    parsing_group_members = ParsingGroupMembers(page=page)
    viewing_posts = ViewingPosts(page=page)
    receiving_and_recording = ReceivingAndRecording()
    tg_contact = TGContact(page=page)
    send_telegram_messages = SendTelegramMessages(page=page)

    gui_program = GUIProgram()

    with open("src/gui/image_display/telegram.png", "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode("utf-8")

    img = ft.Image(
        src=f"data:image/png;base64,{img_base64}",
        width=30,
        height=30,
        fit=ft.BoxFit.CONTAIN,
    )

    # Обработка смены маршрута
    async def route_change(e):
        page.views.clear()

        if page.route == "/":
            pass  # Главное меню уже отображено
        elif page.route == "/inviting":
            await InvitingToAGroup(page=page).inviting_menu()
        elif page.route == "/parsing":
            await parsing_group_members.account_selection_menu()
        elif page.route == "/account_verification_menu":
            await connect.check_menu()
        elif page.route == "/subscribe_unsubscribe":
            await subscribe_unsubscribe_telegram.subscribe_and_unsubscribe_menu()
        elif page.route == "/working_with_reactions":
            await working_with_reactions.reactions_menu()
        elif page.route == "/viewing_posts_menu":
            await viewing_posts.viewing_posts_request()
        elif page.route == "/importing_a_list_of_parsed_data":
            await receiving_and_recording.write_data_to_excel(file_name="user_data/parsed_chat_participants.xlsx")
        elif page.route == "/working_with_contacts":
            await tg_contact.working_with_contacts_menu()
        elif page.route == "/account_connection_menu":
            await connect.account_connection_menu()
        elif page.route == "/creating_groups":
            await creating_groups_and_chats.creating_groups_and_chats()
        elif page.route == "/sending_messages_files_via_chats":
            await send_telegram_messages.sending_messages_files_via_chats()
        elif page.route == "/sending_files_to_personal_account_with_limits":
            await send_telegram_messages.send_files_to_personal_chats()
        elif page.route == "/bio_editing":
            await account_bio.bio_editing_menu()
        elif page.route == "/settings":
            await setting_page.settings_page_menu()

        page.update()

    def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.route = top_view.route
            page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.add(
        await gui_program.key_app_bar(),

        ft.Row(
            controls=[
                # ===== Левая колонка — кнопки =====
                ft.Column(
                    controls=[
                        await menu_button(translations["ru"]["inviting_menu"]["inviting"],
                                          "/inviting", page),
                        await menu_button(translations["ru"]["menu"]["parsing"],
                                          "/parsing", page),
                        await menu_button(translations["ru"]["menu"]["contacts"],
                                          "/working_with_contacts", page),
                        await menu_button(translations["ru"]["menu"]["subscribe_unsubscribe"],
                                          "/subscribe_unsubscribe", page),
                        await menu_button(translations["ru"]["menu"]["account_connect"],
                                          "/account_connection_menu", page),
                        await menu_button(
                            translations["ru"]["message_sending_menu"]["sending_personal_messages_with_limits"],
                            "/sending_files_to_personal_account_with_limits", page),
                        await menu_button(translations["ru"]["menu"]["reactions"],
                                          "/working_with_reactions", page),
                        await menu_button(translations["ru"]["menu"]["account_check"],
                                          "/account_verification_menu", page),
                        await menu_button(translations["ru"]["menu"]["create_groups"],
                                          "/creating_groups", page),
                        await menu_button(translations["ru"]["menu"]["edit_bio"],
                                          "/bio_editing", page),
                        await menu_button(translations["ru"]["reactions_menu"]["we_are_winding_up_post_views"],
                                          "/viewing_posts_menu", page),
                        await menu_button(translations["ru"]["message_sending_menu"]["sending_messages_via_chats"],
                                          "/sending_messages_files_via_chats", page),
                        await menu_button(translations["ru"]["parsing_menu"]["importing_a_list_of_parsed_data"],
                                          "/importing_a_list_of_parsed_data", page),
                        await menu_button(translations["ru"]["menu"]["settings"],
                                          "/settings", page),
                    ],
                ),

                # ===== Правая колонка — надписи =====
                ft.Column(
                    controls=[
                        ft.Text(
                            spans=[
                                ft.TextSpan(
                                    f"{PROGRAM_NAME}",
                                    ft.TextStyle(
                                        size=40,
                                        weight=ft.FontWeight.BOLD,
                                        foreground=ft.Paint(
                                            gradient=ft.PaintLinearGradient(
                                                (0, 20),
                                                (150, 20),
                                                [ft.Colors.PINK, ft.Colors.PURPLE],
                                            )
                                        ),
                                    ),
                                )
                            ]
                        ),

                        ft.Text(f"Версия программы: {PROGRAM_VERSION}"),
                        ft.Text(f"Дата выхода: {DATE_OF_PROGRAM_CHANGE}"),

                        ft.Row(
                            controls=[
                                img,
                                ft.Text(
                                    spans=[
                                        ft.TextSpan(translations["ru"]["main_menu_texts"]["text_1"]),
                                        ft.TextSpan(
                                            translations["ru"]["main_menu_texts"]["text_link_1"],
                                            ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                                            url=translations["ru"]["main_menu_texts"]["text_2"],
                                        ),
                                    ]
                                ),
                            ]
                        ),

                        ft.Row(
                            controls=[
                                img,
                                ft.Text(
                                    spans=[
                                        ft.TextSpan(translations["ru"]["main_menu_texts"]["text_2"]),
                                        ft.TextSpan(
                                            translations["ru"]["main_menu_texts"]["text_link_2"],
                                            ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                                            url=translations["ru"]["main_menu_texts"]["text_2"],
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    expand=True,
                ),
            ],
            expand=True,
        ),
    )


ft.run(main)

# 352
