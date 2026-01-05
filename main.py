# -*- coding: utf-8 -*-
import base64
import asyncio
import flet as ft
from loguru import logger

from src.core.config.configs import (PROGRAM_NAME, PROGRAM_VERSION, DATE_OF_PROGRAM_CHANGE)
from src.core.config.configs import (TIME_SENDING_MESSAGES_1, TIME_SENDING_MESSAGES_2)
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
from src.gui.menu import Menu
from src.locales.translations_loader import translations

logger.add("user_data/log/log_INFO.log", rotation="500 KB", compression="zip", level="INFO")
logger.add("user_data/log/log_ERROR.log", rotation="500 KB", compression="zip", level="ERROR")

BUTTON_HEIGHT = 30  # Высота
BUTTON_WIDTH = 400  # Ширина


async def menu_button(text: str, route: str, page: ft.Page):
    """
    :param text: Текст, отображаемый на кнопке меню.
    :type text: str
    :param route: Путь маршрута (например: "/parsing", "/settings"), на который будет выполнен переход при нажатии.
    :type route: str
    :param page: Экземпляр страницы Flet, используемый для навигации.
    :type page: ft.Page
    :return: Контейнер с кнопкой меню, готовый для добавления в layout (`Column`, `Row`, `View`).
    :rtype: ft.Container https://docs.flet.dev/controls/container/
    """
    return ft.Container(
        content=ft.Button(
            text,
            width=BUTTON_WIDTH,
            height=BUTTON_HEIGHT,
            on_click=lambda _: asyncio.create_task(page.push_route(route)),
        )
    )


async def main(page: ft.Page):
    """
    Главное меню программы
    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    page.title = f"{PROGRAM_NAME}: {PROGRAM_VERSION}"

    # ❗ НИКАКИХ sleep
    page.update()

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

    menu = Menu(page=page)

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
        # route = page.route

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
            await menu.settings_menu()
        elif page.route == "/choice_of_reactions":
            await setting_page.reaction_gui()
        elif page.route == "/proxy_entry":
            await setting_page.creating_the_main_window_for_proxy_data_entry()
        elif page.route == "/recording_api_id_api_hash":
            await setting_page.writing_api_id_api_hash()
        elif page.route == "/message_recording":
            await setting_page.recording_text_for_sending_messages(
                "Введите текст для сообщения",
                setting_page.get_unique_filename(base_filename='user_data/message/message')
            )
        elif page.route == "/recording_reaction_link":
            await setting_page.recording_text_for_sending_messages(
                "Введите ссылку для реакций",
                'user_data/reactions/link_channel.json'
            )
        elif page.route == "/recording_the_time_between_messages":
            await setting_page.create_main_window(
                variable="time_sending_messages",
                smaller_timex=TIME_SENDING_MESSAGES_1,
                larger_timex=TIME_SENDING_MESSAGES_2
            )

        page.update()

    def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.route = top_view.route
            page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.views.append(
        ft.View(
            route="/",
            controls=[
                await menu.gui_program.key_app_bar(),

                ft.Row([
                    ft.Column([
                        await menu_button(translations["ru"]["inviting_menu"]["inviting"], "/inviting", page),
                        await menu_button(translations["ru"]["menu"]["parsing"], "/parsing", page),
                        await menu_button(translations["ru"]["menu"]["contacts"], "/working_with_contacts", page),
                        await menu_button(translations["ru"]["menu"]["subscribe_unsubscribe"], "/subscribe_unsubscribe",
                                          page),
                        await menu_button(translations["ru"]["menu"]["account_connect"], "/account_connection_menu",
                                          page),

                        await menu_button(translations["ru"]["message_sending_menu"]["sending_personal_messages_with_limits"], "/sending_files_to_personal_account_with_limits",
                                          page),

                        # ft.Container(
                        #     content=ft.Button(
                        #         content=translations["ru"]["message_sending_menu"][
                        #             "sending_personal_messages_with_limits"],
                        #         width=BUTTON_WIDTH,
                        #         height=BUTTON_HEIGHT,
                        #         on_click=lambda _: page.push_route(
                        #             "/sending_files_to_personal_account_with_limits"),
                        #     ),
                        # ),

                        await menu_button(
                            translations["ru"]["menu"]["reactions"],
                            "/working_with_reactions",
                            page),

                        # ft.Container(
                        #     content=ft.Button(
                        #         content=translations["ru"]["menu"]["reactions"],
                        #         width=BUTTON_WIDTH,
                        #         height=BUTTON_HEIGHT,
                        #         on_click=lambda _: page.push_route("/working_with_reactions"),
                        #     ),
                        # ),
                        await menu_button(
                            translations["ru"]["menu"]["account_check"],
                            "/account_verification_menu",
                            page),

                        # ft.Container(
                        #     content=ft.Button(
                        #         content=translations["ru"]["menu"]["account_check"],
                        #         width=BUTTON_WIDTH,
                        #         height=BUTTON_HEIGHT,
                        #         on_click=lambda _: page.push_route("/account_verification_menu"),
                        #     ),
                        # ),

                        ft.Container(
                            content=ft.Button(
                                content=translations["ru"]["menu"]["create_groups"],
                                width=BUTTON_WIDTH,
                                height=BUTTON_HEIGHT,
                                on_click=lambda _: page.push_route("/creating_groups"),
                            ),
                        ),

                        ft.Container(
                            content=ft.Button(
                                content=translations["ru"]["menu"]["edit_bio"],
                                width=BUTTON_WIDTH,
                                height=BUTTON_HEIGHT,
                                on_click=lambda _: page.push_route("/bio_editing"),
                            ),
                        ),

                        ft.Container(
                            content=ft.Button(
                                content=translations["ru"]["reactions_menu"]["we_are_winding_up_post_views"],
                                width=BUTTON_WIDTH,
                                height=BUTTON_HEIGHT,
                                on_click=lambda _: page.push_route("/viewing_posts_menu"),
                            ),
                        ),

                        ft.Container(
                            content=ft.Button(
                                content=translations["ru"]["message_sending_menu"]["sending_messages_via_chats"],
                                width=BUTTON_WIDTH,
                                height=BUTTON_HEIGHT,
                                on_click=lambda _: page.push_route("/sending_messages_files_via_chats"),
                            ),
                        ),

                        ft.Container(
                            content=ft.Button(
                                content=translations["ru"]["parsing_menu"]["importing_a_list_of_parsed_data"],
                                width=BUTTON_WIDTH,
                                height=BUTTON_HEIGHT,
                                on_click=lambda _: page.push_route("/importing_a_list_of_parsed_data"),
                            ),
                        ),

                        ft.Container(
                            content=ft.Button(
                                content=translations["ru"]["menu"]["settings"],
                                width=BUTTON_WIDTH,
                                height=BUTTON_HEIGHT,
                                on_click=lambda _: page.push_route("/settings"),
                            ),
                        ),
                    ],
                    ),

                    ft.Column([ft.Text(spans=[ft.TextSpan(
                        f"{PROGRAM_NAME}",
                        ft.TextStyle(size=40, weight=ft.FontWeight.BOLD,
                                     foreground=ft.Paint(gradient=ft.PaintLinearGradient(
                                         (0, 20), (150, 20),
                                         [ft.Colors.PINK, ft.Colors.PURPLE])), ), )]),

                        ft.Text(spans=[ft.TextSpan(text=f"Версия программы: {PROGRAM_VERSION}")]),
                        ft.Text(spans=[ft.TextSpan(text=f"Дата выхода: {DATE_OF_PROGRAM_CHANGE}")]),

                        ft.Container(height=20),

                        ft.Row([img, ft.Text(disabled=False, spans=[
                            ft.TextSpan(translations["ru"]["main_menu_texts"]["text_1"]),
                            ft.TextSpan(translations["ru"]["main_menu_texts"]["text_link_1"],
                                        ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                                        url=translations["ru"]["main_menu_texts"]["text_2"], ), ], ), ]),

                        ft.Row([img, ft.Text(disabled=False, spans=[
                            ft.TextSpan(translations["ru"]["main_menu_texts"]["text_2"]),
                            ft.TextSpan(translations["ru"]["main_menu_texts"]["text_link_2"],
                                        ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                                        url=translations["ru"]["main_menu_texts"]["text_2"], ), ], ), ]),

                    ], horizontal_alignment=ft.CrossAxisAlignment.START, expand=True),
                ])
            ]
        )
    )


ft.run(main)

# 352
