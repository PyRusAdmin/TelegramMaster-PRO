# -*- coding: utf-8 -*-
import base64

import flet as ft
from loguru import logger

from src.core.config.configs import (BUTTON_HEIGHT)
from src.core.config.configs import (PROGRAM_NAME, PROGRAM_VERSION, DATE_OF_PROGRAM_CHANGE)
from src.core.database.create_database import create_database
from src.gui.menu import Menu
from src.locales.translations_loader import translations

logger.add("user_data/log/log_INFO.log", rotation="500 KB", compression="zip", level="INFO")
logger.add("user_data/log/log_ERROR.log", rotation="500 KB", compression="zip", level="ERROR")


async def main(page: ft.Page):
    """
    Главное меню программы
    :param page: Страница интерфейса Flet для отображения элементов управления.
    """
    create_database()
    page.title = f"{PROGRAM_NAME}: {PROGRAM_VERSION} (Дата изменения {DATE_OF_PROGRAM_CHANGE})"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    menu = Menu(page=page)

    with open("src/gui/image_display/telegram.png", "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode("utf-8")

    img = ft.Image(
        src=f"data:image/png;base64,{img_base64}",
        width=30,
        height=30,
        fit=ft.BoxFit.CONTAIN,
    )

    input = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

    # def minus_click(e):
    #     input.value = str(int(input.value) - 1)
    #
    # def plus_click(e):
    #     input.value = str(int(input.value) + 1)

    # Создаём стиль, имитирующий старый ElevatedButton
    elevated_style = ft.ButtonStyle(elevation=2)

    page.add(
        await menu.gui_program.key_app_bar(),

        ft.Row([
            ft.Column([
                ft.Button(
                    translations["ru"]["inviting_menu"]["inviting"],
                    width=350, height=BUTTON_HEIGHT,
                    on_click=lambda _: page.go("/inviting"),
                    style=elevated_style,
                ),
                ft.Button(
                    translations["ru"]["menu"]["parsing"],
                    width=350, height=BUTTON_HEIGHT,
                    on_click=lambda _: page.go("/parsing"),
                    style=elevated_style,
                ),
                ft.Button(
                    translations["ru"]["menu"]["contacts"],
                    width=350, height=BUTTON_HEIGHT,
                    on_click=lambda _: page.go("/working_with_contacts"),
                    style=elevated_style,
                ),
                ft.Button(
                    translations["ru"]["menu"]["subscribe_unsubscribe"],
                    width=350, height=BUTTON_HEIGHT,
                    on_click=lambda _: page.go("/subscribe_unsubscribe"),
                    style=elevated_style,
                ),
                ft.Button(
                    translations["ru"]["menu"]["account_connect"],
                    width=350, height=BUTTON_HEIGHT,
                    on_click=lambda _: page.go("/account_connection_menu"),
                    style=elevated_style,
                ),
                ft.Button(
                    translations["ru"]["message_sending_menu"]["sending_personal_messages_with_limits"],
                    width=350, height=BUTTON_HEIGHT,
                    on_click=lambda _: page.go("/sending_files_to_personal_account_with_limits"),
                    style=elevated_style,
                ),
                ft.Button(
                    translations["ru"]["menu"]["reactions"],
                    width=350, height=BUTTON_HEIGHT,
                    on_click=lambda _: page.go("/working_with_reactions"),
                    style=elevated_style,
                ),
                ft.Button(
                    translations["ru"]["menu"]["account_check"],
                    width=350, height=BUTTON_HEIGHT,
                    on_click=lambda _: page.go("/account_verification_menu"),
                    style=elevated_style,
                ),
                ft.Button(
                    translations["ru"]["menu"]["create_groups"],
                    width=350, height=BUTTON_HEIGHT,
                    on_click=lambda _: page.go("/creating_groups"),
                    style=elevated_style,
                ),
                ft.Button(
                    translations["ru"]["menu"]["edit_bio"],
                    width=350, height=BUTTON_HEIGHT,
                    on_click=lambda _: page.go("/bio_editing"),
                    style=elevated_style,
                ),
                ft.Button(
                    translations["ru"]["reactions_menu"]["we_are_winding_up_post_views"],
                    width=350, height=BUTTON_HEIGHT,
                    on_click=lambda _: page.go("/viewing_posts_menu"),
                    style=elevated_style,
                ),
                ft.Button(
                    translations["ru"]["message_sending_menu"]["sending_messages_via_chats"],
                    width=350, height=BUTTON_HEIGHT,
                    on_click=lambda _: page.go("/sending_messages_files_via_chats"),
                    style=elevated_style,
                ),
                ft.Button(
                    translations["ru"]["parsing_menu"]["importing_a_list_of_parsed_data"],
                    width=350, height=BUTTON_HEIGHT,
                    on_click=lambda _: page.go("/importing_a_list_of_parsed_data"),
                    style=elevated_style,
                ),
                ft.Button(
                    translations["ru"]["menu"]["settings"],
                    width=350, height=BUTTON_HEIGHT,
                    on_click=lambda _: page.go("/settings"),
                    style=elevated_style,
                ),
            ], scroll=ft.ScrollMode.AUTO),

            # ft.Row(
            #     alignment=ft.MainAxisAlignment.CENTER,
            #     controls=[
            #         ft.IconButton(ft.Icons.REMOVE, on_click=minus_click),
            #         input,
            #         ft.IconButton(ft.Icons.ADD, on_click=plus_click),
            #     ],
            # ),
            ft.Row([
                img,
                ft.Text(
                    disabled=False,
                    spans=[
                        ft.TextSpan(translations["ru"]["main_menu_texts"]["text_1"]),
                        ft.TextSpan(
                            translations["ru"]["main_menu_texts"]["text_link_1"],
                            ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                            url=translations["ru"]["main_menu_texts"]["text_2"],
                        ),
                    ],
                ),
            ]),
            ft.Row([
                img,
                ft.Text(
                    disabled=False,
                    spans=[
                        ft.TextSpan(translations["ru"]["main_menu_texts"]["text_2"]),
                        ft.TextSpan(
                            translations["ru"]["main_menu_texts"]["text_link_2"],
                            ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                            url=translations["ru"]["main_menu_texts"]["text_2"],
                        ),
                    ],
                ),
            ]),
        ])
    )


ft.run(main)

# import flet as ft

# from src.core.config.configs import (PROGRAM_NAME, PROGRAM_VERSION, DATE_OF_PROGRAM_CHANGE, WINDOW_WIDTH,
#                                      WINDOW_HEIGHT, WINDOW_RESIZABLE, TIME_SENDING_MESSAGES_1, TIME_SENDING_MESSAGES_2)

# from src.features.account.account_bio import AccountBIO
# from src.features.account.connect import TGConnect
# from src.features.account.contact import TGContact
# from src.features.account.creating import CreatingGroupsAndChats
# from src.features.account.inviting import InvitingToAGroup
# from src.features.account.parsing import ParsingGroupMembers
# from src.features.account.reactions import WorkingWithReactions
# from src.features.account.sending_messages import SendTelegramMessages
# from src.features.account.subscribe_unsubscribe import SubscribeUnsubscribeTelegram
# from src.features.account.viewing_posts import ViewingPosts
# from src.features.recording.receiving_and_recording import ReceivingAndRecording
# from src.features.settings.setting import SettingPage
#
#
# async def main(page: ft.Page):
#
#     page.window.width = WINDOW_WIDTH
#     page.window.height = WINDOW_HEIGHT
#     page.window.resizable = WINDOW_RESIZABLE
#
#     setting_page = SettingPage(page=page)
#     account_bio = AccountBIO(page=page)
#
#     connect = TGConnect(page=page)
#     creating_groups_and_chats = CreatingGroupsAndChats(page=page)
#     subscribe_unsubscribe_telegram = SubscribeUnsubscribeTelegram(page=page)
#     working_with_reactions = WorkingWithReactions(page=page)
#     parsing_group_members = ParsingGroupMembers(page=page)
#     viewing_posts = ViewingPosts(page=page)
#     receiving_and_recording = ReceivingAndRecording()
#     tg_contact = TGContact(page=page)
#     send_telegram_messages = SendTelegramMessages(page=page)
#
#     def navigate_to(route):
#         """Вспомогательная функция для навигации"""
#         page.go(route)
#
#     async def main_menu_program():
#         """Главное меню программы"""
#         page.views.append(
#             ft.View("/", [
#
#
#                     ft.VerticalDivider(width=20, thickness=2, color=ft.Colors.GREY_400),
#                     ft.Column([
#                         ft.Text(spans=[ft.TextSpan(
#                             f"{PROGRAM_NAME}",
#                             ft.TextStyle(
#                                 size=40,
#                                 weight=ft.FontWeight.BOLD,
#                                 foreground=ft.Paint(
#                                     gradient=ft.PaintLinearGradient(
#                                         (0, 20), (150, 20),
#                                         [ft.Colors.PINK, ft.Colors.PURPLE]
#                                     )
#                                 ),
#                             ),
#                         )]),
#                         ft.Text(
#                             disabled=False,
#                             spans=[ft.TextSpan(text=f"Версия программы: {PROGRAM_VERSION}")],
#                         ),
#                         ft.Text(
#                             disabled=False,
#                             spans=[ft.TextSpan(text=f"Дата выхода: {DATE_OF_PROGRAM_CHANGE}")],
#                         ),
#                 ], vertical_alignment=ft.CrossAxisAlignment.START, expand=True)
#             ])
#         )
#
#     async def route_change(_):
#         page.views.clear()
#         if page.route == "/":
#             await main_menu_program()
#         elif page.route == "/inviting":
#             await InvitingToAGroup(page=page).inviting_menu()
#         elif page.route == "/parsing":
#             await parsing_group_members.account_selection_menu()
#         elif page.route == "/account_verification_menu":
#             await connect.check_menu()
#         elif page.route == "/subscribe_unsubscribe":
#             await subscribe_unsubscribe_telegram.subscribe_and_unsubscribe_menu()
#         elif page.route == "/working_with_reactions":
#             await working_with_reactions.reactions_menu()
#         elif page.route == "/viewing_posts_menu":
#             await viewing_posts.viewing_posts_request()
#         elif page.route == "/importing_a_list_of_parsed_data":
#             await receiving_and_recording.write_data_to_excel(file_name="user_data/parsed_chat_participants.xlsx")
#         elif page.route == "/working_with_contacts":
#             await tg_contact.working_with_contacts_menu()
#         elif page.route == "/account_connection_menu":
#             await connect.account_connection_menu()
#         elif page.route == "/creating_groups":
#             await creating_groups_and_chats.creating_groups_and_chats()
#         elif page.route == "/sending_messages_files_via_chats":
#             await send_telegram_messages.sending_messages_files_via_chats()
#         elif page.route == "/sending_files_to_personal_account_with_limits":
#             await send_telegram_messages.send_files_to_personal_chats()
#         elif page.route == "/bio_editing":
#             await account_bio.bio_editing_menu()
#         elif page.route == "/settings":
#             await menu.settings_menu()
#         elif page.route == "/choice_of_reactions":
#             await setting_page.reaction_gui()
#         elif page.route == "/proxy_entry":
#             await setting_page.creating_the_main_window_for_proxy_data_entry()
#         elif page.route == "/recording_api_id_api_hash":
#             await setting_page.writing_api_id_api_hash()
#         elif page.route == "/message_recording":
#             await setting_page.recording_text_for_sending_messages(
#                 "Введите текст для сообщения",
#                 setting_page.get_unique_filename(base_filename='user_data/message/message')
#             )
#         elif page.route == "/recording_reaction_link":
#             await setting_page.recording_text_for_sending_messages(
#                 "Введите ссылку для реакций",
#                 'user_data/reactions/link_channel.json'
#             )
#         elif page.route == "/recording_the_time_between_messages":
#             await setting_page.create_main_window(
#                 variable="time_sending_messages",
#                 smaller_timex=TIME_SENDING_MESSAGES_1,
#                 larger_timex=TIME_SENDING_MESSAGES_2
#             )
#
#         page.update()
#
#     def view_pop(e):
#         page.views.pop()
#         top_view = page.views[-1]
#         navigate_to(top_view.route)
#
#     page.on_route_change = route_change
#     page.on_view_pop = view_pop
#
#     # Устанавливаем начальный маршрут
#     navigate_to("/")
#
#
# ft.run(main)
