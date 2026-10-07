import asyncio
import base64
import webbrowser

import flet as ft
from loguru import logger
from packaging.version import parse

from src.core.configs import (
    BUTTON_HEIGHT,
    BUTTON_WIDTH,
    DATE_OF_PROGRAM_CHANGE,
    PROGRAM_NAME,
    PROGRAM_VERSION,
    width_one_input,
    width_tvo_input,
)
from src.core.database.account import getting_account
from src.core.database.database import (
    get_links_inviting,
    get_links_table_group_send_messages,
    getting_members,
)
from src.core.utils import Utils
from src.features.settings.setting import SettingPage
from src.gui.gui import list_view
from src.gui.gui_elements import GUIProgram
from src.locales.translations_loader import translations


def sync(coro):
    """Преобразует асинхронные конструкторы GUI в синхронные для Flet компонентов."""
    try:
        return coro.send(None)
    except StopIteration as e:
        return e.value
    except AttributeError:
        return coro


def create_menu_button(icon, text, route):
    """Создает современную кнопку меню с подсветкой активного маршрута."""
    is_active = ft.is_route_active(route, exact=(route == "/"))
    
    return ft.Container(
        padding=ft.Padding(4, 2, 4, 2),
        border_radius=8,
        bgcolor=ft.Colors.PRIMARY_CONTAINER if is_active else None,
        content=ft.Button(
            icon=icon,
            content=text,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
            ),
            width=BUTTON_WIDTH,
            height=BUTTON_HEIGHT,
            on_click=lambda _: ft.context.page.navigate(route),
        )
    )


def make_stat_card(title: str, value: str, icon, color):
    """Современная карточка метрики на главной странице."""
    return ft.Container(
        expand=True,
        padding=16,
        border_radius=12,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(title, size=13, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500),
                        ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color=color),
                    ],
                ),
                ft.Container(
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    content=ft.Icon(icon, color=color, size=24),
                ),
            ],
        ),
    )


# ---------------------------------------------------------------------------
# Главная страница (HomeContent) — Полноценный Dashboard
# ---------------------------------------------------------------------------


@ft.component
def HomeContent():
    page = ft.context.page
    gui_program = GUIProgram(page=page)
    utils = Utils(page=page)

    version_info_container = ft.Column(
        spacing=4,
        controls=[
            ft.Text(f"Текущая версия: {PROGRAM_VERSION}", size=13, color=ft.Colors.ON_SURFACE_VARIANT),
            ft.Text(f"Дата выхода: {DATE_OF_PROGRAM_CHANGE}", size=12, color=ft.Colors.OUTLINE),
        ]
    )

    async def check_version_task():
        try:
            latest_tag = await utils.check_github_update()
            if latest_tag and parse(latest_tag) > parse(PROGRAM_VERSION):
                version_info_container.controls = [
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.NEW_RELEASES, color=ft.Colors.AMBER, size=20),
                            ft.Text(f"Доступно обновление: {latest_tag}", weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                        ]
                    ),
                    ft.TextButton(
                        content=ft.Text("👉 Обновиться до новой версии", color=ft.Colors.PRIMARY, weight=ft.FontWeight.BOLD),
                        on_click=lambda _: webbrowser.open("https://t.me/+8LO09QUNtvJkYmJi")
                    ),
                ]
                version_info_container.update()
        except Exception as e:
            logger.warning(f"Ошибка при сравнении версий: {e}")

    asyncio.create_task(check_version_task())

    try:
        with open("src/gui/image_display/telegram.png", "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode("utf-8")
        img = ft.Image(
            src=f"data:image/png;base64,{img_base64}",
            width=24,
            height=24,
            fit=ft.BoxFit.CONTAIN,
        )
    except Exception:
        img = ft.Icon(ft.Icons.TELEGRAM, size=24, color=ft.Colors.PRIMARY)

    session_string = getting_account()
    usernames = getting_members()
    writing_group_links = get_links_table_group_send_messages()
    links_inviting = get_links_inviting()

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=20,
        controls=[
            # Шапка панели
            ft.Container(
                padding=20,
                border_radius=16,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                    colors=[ft.Colors.SURFACE_CONTAINER_HIGHEST, ft.Colors.SURFACE_CONTAINER_HIGH],
                ),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=6,
                            controls=[
                                sync(gui_program.create_gradient_text(text=PROGRAM_NAME)),
                                ft.Text("Панель управления Telegram-маркетингом", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                            ],
                        ),
                        version_info_container,
                    ],
                ),
            ),

            # Полезные ссылки
            ft.Container(
                padding=12,
                border_radius=10,
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                content=ft.Row(
                    spacing=20,
                    controls=[
                        ft.Row(
                            controls=[
                                img,
                                ft.Text(
                                    spans=[
                                        ft.TextSpan(translations["ru"]["main_menu_texts"]["text_1"] + " "),
                                        ft.TextSpan(
                                            translations["ru"]["main_menu_texts"]["text_link_1"],
                                            ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE, color=ft.Colors.PRIMARY),
                                            url=translations["ru"]["main_menu_texts"]["text_2"],
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ],
                ),
            ),

            # Карточки метрик (KPI Analytics Grid)
            ft.Text("📊 Обзор активности и ресурсов", size=16, weight=ft.FontWeight.BOLD),
            ft.Row(
                spacing=12,
                controls=[
                    make_stat_card("Подключено аккаунтов", len(session_string), ft.Icons.ACCOUNT_CIRCLE, ft.Colors.BLUE_400),
                    make_stat_card("Групп для рассылки", len(writing_group_links), ft.Icons.CHAT_BUBBLE_OUTLINE, ft.Colors.GREEN_400),
                ],
            ),
            ft.Row(
                spacing=12,
                controls=[
                    make_stat_card("Групп для инвайтинга", len(links_inviting), ft.Icons.GROUP_ADD, ft.Colors.PURPLE_400),
                    make_stat_card("Всего Username в базе", len(usernames), ft.Icons.PEOPLE_ALT_OUTLINED, ft.Colors.ORANGE_400),
                ],
            ),
        ]
    )


# ---------------------------------------------------------------------------
# Компонент Настроек (Settings)
# ---------------------------------------------------------------------------


@ft.component
def SettingsPageMenu():
    """Компонент настроек программы"""
    page = ft.context.page
    gui_program = GUIProgram(page=page)
    setting_page = SettingPage(page=page)

    async def set_light_theme(_):
        page.theme_mode = ft.ThemeMode.LIGHT
        page.update()
        await gui_program.show_notification(message="Установлена светлая тема ☀️")

    async def set_dark_theme(_):
        page.theme_mode = ft.ThemeMode.DARK
        page.update()
        await gui_program.show_notification(message="Установлена тёмная тема 🌙")

    async def save_api_credentials(_):
        if setting_page.api_id_data.value and setting_page.api_hash_data.value:
            await gui_program.show_notification(message="Данные API успешно сохранены! ✅")
        else:
            await gui_program.show_notification(message="Заполните API ID и API Hash! ⚠️")

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=20,
        controls=[
            sync(gui_program.create_gradient_text(
                text=translations["ru"]["menu"]["settings"]
            )),
            
            # Секция 1: Тема
            ft.Container(
                padding=16,
                border_radius=12,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                content=ft.Column(
                    spacing=12,
                    controls=[
                        ft.Text("🎨 Тема оформления", size=16, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            controls=[
                                ft.Button(
                                    content=translations["ru"]["menu_settings"]["light_theme"],
                                    icon=ft.Icons.LIGHT_MODE,
                                    on_click=lambda e: asyncio.create_task(set_light_theme(e)),
                                ),
                                ft.Button(
                                    content=translations["ru"]["menu_settings"]["dark_theme"],
                                    icon=ft.Icons.DARK_MODE,
                                    on_click=lambda e: asyncio.create_task(set_dark_theme(e)),
                                ),
                            ]
                        ),
                    ]
                )
            ),

            # Секция 2: API ключи
            ft.Container(
                padding=16,
                border_radius=12,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                content=ft.Column(
                    spacing=12,
                    controls=[
                        ft.Text("🔑 Настройки Telegram API", size=16, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            controls=[
                                setting_page.api_id_data,
                                setting_page.api_hash_data,
                            ]
                        ),
                        ft.Button(
                            content="Сохранить API ключи",
                            icon=ft.Icons.SAVE,
                            on_click=lambda e: asyncio.create_task(save_api_credentials(e)),
                        ),
                    ]
                )
            ),

            # Секция 3: Прокси
            ft.Container(
                padding=16,
                border_radius=12,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                content=ft.Column(
                    spacing=12,
                    controls=[
                        ft.Text("🌐 Настройки Прокси", size=16, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            controls=[
                                setting_page.proxy_type,
                                setting_page.addr_type,
                                setting_page.port_type,
                            ]
                        ),
                        ft.Row(
                            controls=[
                                setting_page.username_type,
                                setting_page.password_type,
                            ]
                        ),
                    ]
                )
            ),
        ]
    )


# ---------------------------------------------------------------------------
# Компонент Проверки обновлений (CheckUpdatesMenu)
# ---------------------------------------------------------------------------


@ft.component
def CheckUpdatesMenu():
    """Компонент проверки обновлений приложения."""
    page = ft.context.page
    gui_program = GUIProgram(page=page)
    utils = Utils(page=page)

    status_container = ft.Column(
        spacing=10,
        controls=[
            ft.Row(
                controls=[
                    ft.ProgressRing(width=20, height=20, stroke_width=2),
                    ft.Text("Проверка наличия обновлений на GitHub...", color=ft.Colors.ON_SURFACE_VARIANT),
                ]
            )
        ]
    )

    async def perform_check(_=None):
        status_container.controls = [
            ft.Row(
                controls=[
                    ft.ProgressRing(width=20, height=20, stroke_width=2),
                    ft.Text("Проверка наличия обновлений...", color=ft.Colors.ON_SURFACE_VARIANT),
                ]
            )
        ]
        status_container.update()

        try:
            latest_tag = await utils.check_github_update()
            if latest_tag and parse(latest_tag) > parse(PROGRAM_VERSION):
                status_container.controls = [
                    ft.Container(
                        padding=16,
                        border_radius=12,
                        bgcolor=ft.Colors.GREEN_CONTAINER,
                        content=ft.Column(
                            spacing=8,
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.NEW_RELEASES, color=ft.Colors.GREEN_900, size=24),
                                        ft.Text(f"Доступна новая версия: {latest_tag}", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900),
                                    ]
                                ),
                                ft.Text(f"Текущая версия программы: {PROGRAM_VERSION}", color=ft.Colors.GREEN_900),
                                ft.Button(
                                    content="👉 Скачать новую версию (Telegram)",
                                    icon=ft.Icons.DOWNLOAD,
                                    on_click=lambda _: webbrowser.open("https://t.me/+8LO09QUNtvJkYmJi"),
                                ),
                            ]
                        )
                    )
                ]
            else:
                status_container.controls = [
                    ft.Container(
                        padding=16,
                        border_radius=12,
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=24),
                                ft.Text(f"У вас установлена актуальная версия ({PROGRAM_VERSION})!", size=15, weight=ft.FontWeight.W_500),
                            ]
                        )
                    )
                ]
        except Exception as e:
            status_container.controls = [
                ft.Text(f"Ошибка проверки обновлений: {e}", color=ft.Colors.RED)
            ]
        status_container.update()

    asyncio.create_task(perform_check())

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=20,
        controls=[
            sync(gui_program.create_gradient_text(text="Проверка обновлений")),
            ft.Container(
                padding=16,
                border_radius=12,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text(f"Программа: {PROGRAM_NAME}", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Текущая версия: {PROGRAM_VERSION}", size=14),
                        ft.Text(f"Дата релиза: {DATE_OF_PROGRAM_CHANGE}", size=13, color=ft.Colors.OUTLINE),
                        ft.Button(
                            content="Проверить снова",
                            icon=ft.Icons.REFRESH,
                            on_click=lambda e: asyncio.create_task(perform_check(e)),
                        ),
                    ]
                )
            ),
            status_container,
        ]
    )


# ---------------------------------------------------------------------------
# Компонент «Об авторе» (AboutAuthorMenu)
# ---------------------------------------------------------------------------


@ft.component
def AboutAuthorMenu():
    """Компонент информации об авторе и приложении."""
    page = ft.context.page
    gui_program = GUIProgram(page=page)

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=20,
        controls=[
            sync(gui_program.create_gradient_text(text="Об авторе и проекте")),
            ft.Container(
                padding=20,
                border_radius=16,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                content=ft.Column(
                    spacing=14,
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.ACCOUNT_BOX, size=40, color=ft.Colors.PRIMARY),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text("PyRusAdmin", size=20, weight=ft.FontWeight.BOLD),
                                        ft.Text("Разработчик TelegramMaster-PRO", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                                    ]
                                )
                            ]
                        ),
                        sync(gui_program.diver_castom()),
                        ft.Text(
                            "TelegramMaster-PRO — многофункциональный комбайн для автоматизации маркетинга, "
                            "инвайтинга, рассылок, парсинга и работы с аккаунтами Telegram.",
                            size=14,
                        ),
                        ft.Row(
                            spacing=12,
                            controls=[
                                ft.Button(
                                    content="Telegram Канал / Сообщество",
                                    icon=ft.Icons.TELEGRAM,
                                    on_click=lambda _: webbrowser.open("https://t.me/+8LO09QUNtvJkYmJi"),
                                ),
                                ft.Button(
                                    content="GitHub Репозиторий",
                                    icon=ft.Icons.CODE,
                                    on_click=lambda _: webbrowser.open("https://github.com/PyRusAdmin/TelegramMaster-PRO"),
                                ),
                            ]
                        ),
                    ]
                )
            ),
        ]
    )


# ---------------------------------------------------------------------------
# Разделы программы
# ---------------------------------------------------------------------------


@ft.component
def InvitingMenu():
    page = ft.context.page
    gui_program = GUIProgram(page=page)

    time_inviting_1, time_inviting_2 = sync(gui_program.build_time_inputs_with_save_button(
        label_min="Мин. задержка (сек)",
        label_max="Макс. задержка (сек)",
        width=width_tvo_input
    ))
    hour, minutes = sync(gui_program.build_time_inputs_with_save_button(
        label_min="Час запуска (0–23)",
        label_max="Минуты (0–59)",
        width=width_tvo_input
    ))

    limits = sync(gui_program.build_link_input_with_save_button(
        label_text="Введите лимит на аккаунт",
        width=width_one_input
    ))
    link_entry_field = sync(gui_program.build_link_input_with_save_button(
        label_text="Введите ссылку на группу для инвайтинга",
        width=width_one_input
    ))

    return ft.Column(
        spacing=16,
        controls=[
            sync(gui_program.create_gradient_text(
                text=translations["ru"]["inviting_menu"]["inviting"]
            )),
            list_view,

            ft.Row(
                [
                    sync(gui_program.compose_time_input_row(
                        min_time_input=time_inviting_1,
                        max_time_input=time_inviting_2,
                    )),
                    sync(gui_program.compose_time_input_row(
                        min_time_input=hour,
                        max_time_input=minutes
                    ))
                ]
            ),
            sync(gui_program.diver_castom()),
            ft.Row(
                [
                    sync(gui_program.compose_link_input_row(
                        link_input=limits,
                    )),
                    sync(gui_program.compose_link_input_row(
                        link_input=link_entry_field,
                    )),
                ]
            ),
        ]
    )


@ft.component
def ParsingMenu():
    page = ft.context.page
    gui_program = GUIProgram(page=page)
    return ft.Column([sync(gui_program.create_gradient_text(text=translations["ru"]["menu"]["parsing"])), list_view])


@ft.component
def ContactsMenu():
    page = ft.context.page
    gui_program = GUIProgram(page=page)
    return ft.Column([sync(gui_program.create_gradient_text(text=translations["ru"]["menu"]["contacts"])), list_view])


@ft.component
def SubscribeUnsubscribeMenu():
    page = ft.context.page
    gui_program = GUIProgram(page=page)
    return ft.Column([sync(gui_program.create_gradient_text(text=translations["ru"]["menu"]["subscribe_unsubscribe"])), list_view])


@ft.component
def AccountConnectionMenu():
    page = ft.context.page
    gui_program = GUIProgram(page=page)
    return ft.Column([sync(gui_program.create_gradient_text(text=translations["ru"]["menu"]["account_connect"])), list_view])


@ft.component
def ReactionsMenu():
    page = ft.context.page
    gui_program = GUIProgram(page=page)
    return ft.Column([sync(gui_program.create_gradient_text(text=translations["ru"]["menu"]["reactions"])), list_view])


@ft.component
def AccountVerificationMenu():
    page = ft.context.page
    gui_program = GUIProgram(page=page)
    return ft.Column([sync(gui_program.create_gradient_text(text=translations["ru"]["menu"]["account_check"])), list_view])


@ft.component
def CreatingGroupsMenu():
    page = ft.context.page
    gui_program = GUIProgram(page=page)
    return ft.Column([sync(gui_program.create_gradient_text(text=translations["ru"]["menu"]["create_groups"])), list_view])


@ft.component
def BioEditingMenu():
    page = ft.context.page
    gui_program = GUIProgram(page=page)
    return ft.Column([sync(gui_program.create_gradient_text(text=translations["ru"]["menu"]["edit_bio"])), list_view])


@ft.component
def ViewingPostsMenu():
    page = ft.context.page
    gui_program = GUIProgram(page=page)
    return ft.Column([sync(gui_program.create_gradient_text(text=translations["ru"]["reactions_menu"]["we_are_winding_up_post_views"])), list_view])


@ft.component
def SendingMessagesMenu():
    page = ft.context.page
    gui_program = GUIProgram(page=page)
    return ft.Column([sync(gui_program.create_gradient_text(text=translations["ru"]["message_sending_menu"]["sending_messages_via_chats"])), list_view])


@ft.component
def ImportingParsedDataMenu():
    page = ft.context.page
    gui_program = GUIProgram(page=page)
    return ft.Column([sync(gui_program.create_gradient_text(text=translations["ru"]["parsing_menu"]["importing_a_list_of_parsed_data"])), list_view])


# ---------------------------------------------------------------------------
# Root Layout (Современный макет приложения)
# ---------------------------------------------------------------------------


@ft.component
def RootLayout():
    """Основной макет приложения — красивое боковое меню + зона контента."""
    outlet = ft.use_route_outlet()
    page = ft.context.page
    gui_program = GUIProgram(page=page)

    return ft.View(
        route="/",
        can_pop=False,
        controls=[
            ft.Row(
                [
                    # Левое меню с красивой структурой
                    ft.Container(
                        padding=8,
                        border_radius=12,
                        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                        content=ft.Column(
                            scroll=ft.ScrollMode.AUTO,
                            controls=[
                                create_menu_button(
                                    icon=ft.Icons.HOME,
                                    text=translations["ru"]["menu"]["main"],
                                    route="/",
                                ),
                                create_menu_button(
                                    icon=ft.Icons.INSERT_INVITATION,
                                    text=translations["ru"]["inviting_menu"]["inviting"],
                                    route="/inviting",
                                ),
                                create_menu_button(
                                    icon=ft.Icons.SEND,
                                    text=translations["ru"]["message_sending_menu"]["sending_messages_via_chats"],
                                    route="/sending_messages_files_via_chats",
                                ),
                                create_menu_button(
                                    icon=ft.Icons.FAVORITE,
                                    text=translations["ru"]["menu"]["reactions"],
                                    route="/working_with_reactions",
                                ),
                                create_menu_button(
                                    icon=ft.Icons.REMOVE_RED_EYE,
                                    text=translations["ru"]["reactions_menu"]["we_are_winding_up_post_views"],
                                    route="/viewing_posts_menu",
                                ),
                                create_menu_button(
                                    icon=ft.Icons.ANALYTICS,
                                    text=translations["ru"]["menu"]["parsing"],
                                    route="/parsing",
                                ),
                                create_menu_button(
                                    icon=ft.Icons.CONTACT_PAGE,
                                    text=translations["ru"]["menu"]["contacts"],
                                    route="/working_with_contacts",
                                ),
                                create_menu_button(
                                    icon=ft.Icons.FILE_DOWNLOAD,
                                    text=translations["ru"]["parsing_menu"]["importing_a_list_of_parsed_data"],
                                    route="/importing_a_list_of_parsed_data",
                                ),
                                create_menu_button(
                                    icon=ft.Icons.MANAGE_ACCOUNTS,
                                    text=translations["ru"]["menu"]["account_connect"],
                                    route="/account_connection_menu",
                                ),
                                create_menu_button(
                                    icon=ft.Icons.VERIFIED_USER,
                                    text=translations["ru"]["menu"]["account_check"],
                                    route="/account_verification_menu",
                                ),
                                create_menu_button(
                                    icon=ft.Icons.AUTORENEW,
                                    text=translations["ru"]["menu"]["subscribe_unsubscribe"],
                                    route="/subscribe_unsubscribe",
                                ),
                                create_menu_button(
                                    icon=ft.Icons.GROUP_ADD,
                                    text=translations["ru"]["menu"]["create_groups"],
                                    route="/creating_groups",
                                ),
                                create_menu_button(
                                    icon=ft.Icons.EDIT_NOTE,
                                    text=translations["ru"]["menu"]["edit_bio"],
                                    route="/bio_editing",
                                ),
                                create_menu_button(
                                    icon=ft.Icons.SETTINGS,
                                    text=translations["ru"]["menu"]["settings"],
                                    route="/settings",
                                ),
                                create_menu_button(
                                    icon=ft.Icons.SYSTEM_UPDATE_ALT,
                                    text="Проверить обновления",
                                    route="/check_updates",
                                ),
                                create_menu_button(
                                    icon=ft.Icons.INFO_OUTLINED,
                                    text="Об авторе",
                                    route="/about_author",
                                ),
                            ],
                        ),
                    ),
                    ft.Container(content=outlet, expand=True, padding=16),
                ],
                expand=True,
            ),
        ],
    )


# ---------------------------------------------------------------------------
# App Router
# ---------------------------------------------------------------------------


@ft.component
def App():
    return ft.Router(
        [
            ft.Route(
                component=RootLayout,
                outlet=True,
                children=[
                    ft.Route(index=True, component=HomeContent),
                    ft.Route(path="inviting", component=InvitingMenu),
                    ft.Route(path="parsing", component=ParsingMenu),
                    ft.Route(path="working_with_contacts", component=ContactsMenu),
                    ft.Route(path="subscribe_unsubscribe", component=SubscribeUnsubscribeMenu),
                    ft.Route(path="account_connection_menu", component=AccountConnectionMenu),
                    ft.Route(path="working_with_reactions", component=ReactionsMenu),
                    ft.Route(path="account_verification_menu", component=AccountVerificationMenu),
                    ft.Route(path="creating_groups", component=CreatingGroupsMenu),
                    ft.Route(path="bio_editing", component=BioEditingMenu),
                    ft.Route(path="viewing_posts_menu", component=ViewingPostsMenu),
                    ft.Route(path="sending_messages_files_via_chats", component=SendingMessagesMenu),
                    ft.Route(path="importing_a_list_of_parsed_data", component=ImportingParsedDataMenu),
                    ft.Route(path="settings", component=SettingsPageMenu),
                    ft.Route(path="check_updates", component=CheckUpdatesMenu),
                    ft.Route(path="about_author", component=AboutAuthorMenu),
                ],
            ),
        ],
        manage_views=True,
    )


if __name__ == "__main__":
    ft.run(lambda page: page.render_views(App))
