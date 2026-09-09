import flet as ft  # Импортируем библиотеку flet

from src.gui.gui import list_view
from src.gui.gui_elements import GUIProgram
from src.locales.translations_loader import translations


# async def gui_button(text: str, on_click, bgcolor):
#     """
#     :param text: Текст, отображаемый на кнопке меню.
#     :param on_click: Функция, которая должна быть выполнена
#     :return: Контейнер с кнопкой меню, готовый для добавления в layout (`Column`, `Row`, `View`).
#     """
#     # return ft.Container(  # ft.Container https://docs.flet.dev/controls/container/
#     #     content=ft.Button(
#     #         content=text,
#     #         width=width,
#     # height=BUTTON_HEIGHT, # Задает высоту кнопки.
#     # expand=True,  # Заставляет кнопку растягиваться, занимая всю доступную ширину.
#     # on_click=on_click
#     # ),
#     # )
#     return ft.Button(
#         content=text,  # Задает содержимое кнопки.
#         height=BUTTON_HEIGHT,  # Задает высоту кнопки.
#         expand=True,  # Заставляет кнопку растягиваться, занимая всю доступную ширину.
#         on_click=on_click,  # Используем синхронную обёртку
#         style=ft.ButtonStyle(
#             shape=ft.RoundedRectangleBorder(radius=30),  # Делает края кнопки сильно скругленными
#             padding=ft.Padding(15, 10, 15, 10),
#             bgcolor=bgcolor,  # Цвет кнопки
#         ),
#     )


class FunctionButton:

    def __init__(self, page: ft.Page):
        """
        Инициализация класса для управления кнопками в интерфейсе.

        :param page: Страница интерфейса Flet для отображения элементов управления
        """
        self.page = page
        self.gui_program = GUIProgram(page=page)

    async def function_button_ready_viewing(self, number_views, btn_click, link_channel, link_post):
        """
        Создает интерфейс для накрутки просмотров постов.

        :param number_views: Поле ввода количества просмотров
        :param btn_click: Функция-обработчик для кнопки "Готово"
        :param link_channel: Поле ввода ссылки на канал
        :param link_post: Поле ввода ссылки на пост
        :return: None
        """
        # Добавление представления на страницу
        self.page.views.append(
            ft.View(
                route="/viewing_posts_menu",  # Маршрут для этого представления
                appbar=await self.gui_program.key_app_bar(),  # Кнопка назад
                controls=[
                    await self.gui_program.create_gradient_text(
                        text=translations["ru"]["reactions_menu"]["we_are_winding_up_post_views"]
                    ),
                    list_view,  # Отображение логов 📝
                    number_views,  # Поле ввода количества просмотров основываясь на количестве аккаунтов
                    link_channel,  # Поле ввода ссылки на чат
                    link_post,  # Поле ввода ссылки пост
                    ft.Column(),  # Колонка для размещения других элементов (при необходимости)
                    ft.Row(
                        expand=True,
                        controls=[
                            await self.gui_program.gui_button(  # ✅ Готово
                                text=translations["ru"]["buttons"]["done"],
                                on_click=btn_click,
                                bgcolor=ft.Colors.GREEN,
                            ),
                        ]
                    ),
                ]
            )
        )
