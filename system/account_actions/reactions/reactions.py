import json
import os
import random
import sys
import time

import flet as ft  # Импортируем библиотеку flet
from loguru import logger  # Импортируем библиотеку loguru для логирования
from rich import print  # Импортируем библиотеку rich для красивого отображения текста в терминале / консолей (цветного)
from telethon import events, types
from telethon.errors import *
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import SendReactionRequest, GetMessagesViewsRequest
from telethon import TelegramClient

from system.account_actions.creating.account_registration import telegram_connects
from system.account_actions.subscription.subscription import subscribe_to_group_or_channel
from system.auxiliary_functions.global_variables import console, api_id_data, api_hash_data
from system.notification.notification import app_notifications
from system.proxy.checking_proxy import reading_proxy_data_from_the_database
from system.telegram_actions.telegram_actions import telegram_connect_and_output_name


async def reactions_for_groups_and_messages_test(number, chat, db_handler) -> None:
    """Вводим ссылку на группу и ссылку на сообщение"""
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records: list = db_handler.open_and_read_data("config")
    # Количество аккаунтов на данный момент в работе
    print(f"[medium_purple3]Всего accounts: {len(records)}")
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    with open('user_settings/reactions/number_accounts.json', 'r') as json_file:
        number_of_accounts = json.load(json_file)  # Используем функцию load для загрузки данных из файла

    logger.info(f'Всего реакций на пост: {number_of_accounts}')
    records: list = db_handler.open_the_db_and_read_the_data_lim(name_database_table="config",
                                                                 number_of_accounts=int(number_of_accounts))
    for row in records:
        # Подключение к Telegram и вывод имени аккаунта в консоль / терминал
        proxy = reading_proxy_data_from_the_database(db_handler)  # Proxy IPV6 - НЕ РАБОТАЮТ
        client = TelegramClient(f"user_settings/accounts/{row[2]}", int(row[0]), row[1],
                                system_version="4.16.30-vxCUSTOM", proxy=proxy)
        await client.connect()  # Подсоединяемся к Telegram
        try:
            await client(JoinChannelRequest(chat))  # Подписываемся на канал / группу
            time.sleep(5)
            with open('user_settings/reactions/reactions.json', 'r') as json_file:
                reaction_input = json.load(json_file)  # Используем функцию load для загрузки данных из файла
            random_value = random.choice(reaction_input)  # Выбираем случайное значение из списка
            logger.info(random_value)
            await client(SendReactionRequest(peer=chat, msg_id=int(number),
                                             reaction=[types.ReactionEmoji(emoticon=f'{random_value}')]))
            time.sleep(1)
        except KeyError:
            sys.exit(1)
        except Exception as e:
            logger.exception(e)
            print("[medium_purple3][!] Произошла ошибка, для подробного изучения проблемы просмотрите файл log.log")
        finally:
            client.disconnect()

    app_notifications(notification_text=f"Работа с группой {chat} окончена!")


def writing_names_found_files_to_the_db_config_reactions(db_handler) -> None:
    """Запись названий найденных файлов в базу данных"""
    creating_a_table = "CREATE TABLE IF NOT EXISTS config_reactions (id, hash, phone)"
    writing_data_to_a_table = "INSERT INTO config_reactions (id, hash, phone) VALUES (?, ?, ?)"
    db_handler.cleaning_db(name_database_table="config_reactions")  # Call the method on the instance
    records = connecting_account_sessions_config_reactions()
    for entities in records:
        print(f"Записываем данные аккаунта {entities} в базу данных")
        db_handler.write_data_to_db(creating_a_table, writing_data_to_a_table, entities)


def connecting_account_sessions_config_reactions() -> list:
    """Подключение сессий аккаунтов
    Функция listdir() модуля os возвращает список, содержащий имена файлов и директорий в каталоге, заданном путем
    path user_settings/accounts
    Функция str.endswith() возвращает True, если строка заканчивается заданным суффиксом (.session), в противном
    случае возвращает False.
    Os.path.splitext(path) - разбивает путь на пару (root, ext), где ext начинается с точки и содержит не
    более одной точки.
    """
    entities = []  # Создаем словарь с именами найденных аккаунтов в папке user_settings/accounts
    for x in os.listdir(path="user_settings/reactions/accounts"):
        if x.endswith(".session"):
            file = os.path.splitext(x)[0]
            print(f"Найденные аккаунты: {file}.session")  # Выводим имена найденных аккаунтов
            entities.append([api_id_data, api_hash_data, file])
    return entities


def setting_reactions(db_handler):
    """Выставление реакций на новые посты"""
    writing_names_found_files_to_the_db_config_reactions(db_handler)

    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records_ac: list = db_handler.open_and_read_data("config_reactions")
    # Количество аккаунтов на данный момент в работе
    print(f"[medium_purple3]Всего accounts: {len(records_ac)}")

    # Считываем количество аккаунтов, которые будут ставить реакции
    with open('user_settings/reactions/number_accounts.json', 'r') as json_file:
        records_ac_json = json.load(json_file)  # Используем функцию load для загрузки данных из файла
    logger.info(records_ac_json)

    records: list = db_handler.open_the_db_and_read_the_data_lim(name_database_table="config_reactions",
                                                                 number_of_accounts=int(records_ac_json))
    logger.info(records)
    for row in records:
        client = telegram_connects(db_handler, session=f"user_settings/reactions/accounts/{row[2]}")
        # Открываем файл для чтения
        with open('user_settings/reactions/link_channel.json', 'r') as json_file:
            chat = json.load(json_file)  # Используем функцию load для загрузки данных из файла
        logger.info(chat)
        client(JoinChannelRequest(chat))  # Подписываемся на канал / группу
        @client.on(events.NewMessage(chats=chat))
        async def handler(event):
            message = event.message  # Получаем сообщение из события
            message_id = message.id  # Получаем id сообщение
            print(f"Идентификатор сообщения: {message_id}")
            logger.info(message)
            # Проверяем, является ли сообщение постом и не является ли оно нашим
            if message.post and not message.out:
                await reactions_for_groups_and_messages_test(message_id, chat, db_handler)

    client.run_until_disconnected()  # Запуск клиента


def save_reactions(reactions, path_to_the_file):
    """Открываем файл для записи данных в формате JSON"""
    with open(f'{path_to_the_file}', 'w') as json_file:
        json.dump(reactions, json_file)  # Используем функцию dump для записи данных в файл


def record_the_number_of_accounts():
    """Запись количества аккаунтов проставляющих реакции"""

    def main_inviting(page) -> None:
        page.window_width = 300  # ширина окна
        page.window_height = 300  # высота окна
        page.window_resizable = False  # Запрет на изменение размера окна
        smaller_time = ft.TextField(label="Введите количество реакций", autofocus=True)
        greetings = ft.Column()

        def btn_click(e) -> None:
            try:
                page.update()
                smaller_times = int(smaller_time.value)  # Extract the text value from the TextField
                save_reactions(reactions=smaller_times,  # Количество аккаунтов для проставления реакций
                               path_to_the_file='user_settings/reactions/number_accounts.json')
                page.window_close()
            except ValueError:
                pass

        page.add(smaller_time, ft.ElevatedButton("Сохранить", on_click=btn_click), greetings, )

    ft.app(target=main_inviting)


def recording_link_channel():
    """Запись ссылки на канал / группу"""

    def main_inviting(page) -> None:
        page.window_width = 300  # ширина окна
        page.window_height = 300  # высота окна
        page.window_resizable = False  # Запрет на изменение размера окна
        smaller_time = ft.TextField(label="Введите ссылку на группу", autofocus=True)
        greetings = ft.Column()

        def btn_click(e) -> None:
            page.update()
            link_text = smaller_time.value  # Extract the text value from the TextField
            save_reactions(reactions=link_text,
                           path_to_the_file='user_settings/reactions/link_channel.json')  # Запись ссылки в json файл
            page.window_close()

        page.add(smaller_time, ft.ElevatedButton("Сохранить", on_click=btn_click), greetings, )

    ft.app(target=main_inviting)


def reaction_gui():
    """Выбираем реакцию с помощью чекбокса"""

    def main(page):
        """Основное тело программы"""

        page.window_width = 480  # ширина окна
        page.window_height = 450  # высота окна
        page.window_resizable = False  # Запрет на изменение размера окна

        def button_clicked(e):
            """Выбранная реакция"""
            selected_reactions = []  # Создает пустой список selected_reactions для хранения выбранных реакций.
            for checkbox in [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, q13, c14, q15, q16, q18, c19, c20, c21, c23,
                             c24, c25, c26, c27, c28, c29, c30, c31, c32, c33, c34, c35, c36, c37, c38, c39, c41, c42,
                             c43, c44, c45, c46, q47, c48, c49, c50, c51, q52, c53]:  # Перебирает чекбоксы (c1 - c53).
                if checkbox.value:  # Проверяет, отмечен ли чекбокс.
                    # Если чекбокс отмечен, добавляет его текст (метку) в список selected_reactions.
                    selected_reactions.append(checkbox.label)

            print(f"Выбранные реакции: {selected_reactions}")  # Печатает список выбранных реакций.
            save_reactions(reactions=selected_reactions,
                           path_to_the_file='user_settings/reactions/reactions.json')  # Сохраняем реакцию в jsone файл
            page.window_close()

        t = ft.Text(value='Выберите реакцию')  # Создает текстовое поле (t).
        c1 = ft.Checkbox(label="😀")  # Создает чекбокс c1 с меткой "😀".
        c2 = ft.Checkbox(label="😎")
        c3 = ft.Checkbox(label="😍")
        c4 = ft.Checkbox(label="😂")
        c5 = ft.Checkbox(label="😡")
        c6 = ft.Checkbox(label="😱")
        c7 = ft.Checkbox(label="👍")
        c8 = ft.Checkbox(label="👎")
        c9 = ft.Checkbox(label="❤")
        c10 = ft.Checkbox(label="🔥")
        c11 = ft.Checkbox(label="🎉")
        q13 = ft.Checkbox(label="😁")
        c14 = ft.Checkbox(label="😢")
        q15 = ft.Checkbox(label="💩")
        q16 = ft.Checkbox(label="👏")
        q18 = ft.Checkbox(label="🤷‍♀️")
        c19 = ft.Checkbox(label="🤷")
        c20 = ft.Checkbox(label="🤷‍♂️")
        c21 = ft.Checkbox(label="👾️")
        c23 = ft.Checkbox(label="🙊")
        c24 = ft.Checkbox(label="💊")
        c25 = ft.Checkbox(label="😘")
        c26 = ft.Checkbox(label="🦄")
        c27 = ft.Checkbox(label="💘")
        c28 = ft.Checkbox(label="🆒")
        c29 = ft.Checkbox(label="🗿")
        c30 = ft.Checkbox(label="🤪")
        c31 = ft.Checkbox(label="💅")
        c32 = ft.Checkbox(label="☃️")
        c33 = ft.Checkbox(label="🎄")
        c34 = ft.Checkbox(label="🎅")
        c35 = ft.Checkbox(label="🤗")
        c36 = ft.Checkbox(label="🤬")
        c37 = ft.Checkbox(label="🤮")
        c38 = ft.Checkbox(label="🤡")
        c39 = ft.Checkbox(label="🥴")
        c41 = ft.Checkbox(label="💯")
        c42 = ft.Checkbox(label="🌭")
        c43 = ft.Checkbox(label="⚡️")
        c44 = ft.Checkbox(label="🍌")
        c45 = ft.Checkbox(label="🖕")
        c46 = ft.Checkbox(label="💋")
        q47 = ft.Checkbox(label="👀")
        c48 = ft.Checkbox(label="🤝")
        c49 = ft.Checkbox(label="🍾")
        c50 = ft.Checkbox(label="🏆")
        c51 = ft.Checkbox(label="🥱")
        q52 = ft.Checkbox(label="🕊")
        c53 = ft.Checkbox(label="😭")

        # Кнопка "Готово" (b) и связывает ее с функцией button_clicked.
        b = ft.ElevatedButton(text="Готово", on_click=button_clicked)

        page.add(ft.Row([t]))  # Добавляет все элементы (c1 - c6, b, t) на страницу (page).
        page.add(ft.Row([c1, c2, c3, c4, c5, c6, c49]))  # Добавляет все элементы (c1 - c6, b, t) на страницу (page).
        page.add(ft.Row([c7, c8, c9, c10, c11, c53, c48]))  # Добавляет все элементы (c1 - c6, b, t) на страницу (page).
        page.add(ft.Row([c19, c20, c21, c23, c24, c51, c46]))
        page.add(ft.Row([c25, c26, c27, c28, c29, c30, c45]))
        page.add(ft.Row([c31, c32, c33, c34, c35, c36, c44]))
        page.add(ft.Row([c37, c38, c39, c41, c42, c50, c43]))
        page.add(ft.Row([q13, c14, q15, q16, q18, q52, q47]))
        page.add(ft.Row([b]))  # Добавляет все элементы (c1 - c6, b, t) на страницу (page).

    ft.app(target=main)  # Запускает приложение, используя функцию main в качестве точки входа.


def users_choice_of_reaction(db_handler) -> None:
    """Выбираем реакцию для выставления в чате / канале"""
    print("[medium_purple3][!] Давайте выберем какую реакцию будем ставить\n",
          "[magenta][0] Поднятый большой палец 👍\n",
          "[magenta][1] Опущенный большой палец 👎\n",
          "[magenta][2] Красное сердце ❤\n",
          "[magenta][3] Огонь 🔥\n",
          "[magenta][4] Хлопушка 🎉\n",
          "[magenta][5] Лицо, кричащее от страха 😱\n",
          "[magenta][6] Широко улыбающееся лицо 😁\n",
          "[magenta][7] Лицо с открытым ртом и в холодном поту 😢\n",
          "[magenta][8] Фекалии 💩\n",
          "[magenta][9] Аплодирующие руки 👏\n"
          "[magenta][10] Злость 😡\n"
          "[magenta][11] Женщина разводит руками 🤷‍♀️\n"
          "[magenta][12] Человек разводит руками 🤷\n"
          "[magenta][13] Мужчина разводит руками 🤷‍♂️\n"
          "[magenta][14] Космический монстр 👾️\n"
          "[magenta][15] Лицо в темных очках 😎\n"
          "[magenta][16] Ничего не скажу 🙊\n"
          "[magenta][17] Таблетка 💊\n"
          "[magenta][18] Воздушный поцелуй 😘\n"
          "[magenta][19] Единорог 🦄\n"
          "[magenta][20] Сердце со стрелой 💘\n"
          "[magenta][21] Значок круто 🆒\n"
          "[magenta][22] Каменное лицо 🗿\n"
          "[magenta][23] Глупое лицо 🤪\n"
          "[magenta][24] Маникюр 💅\n"
          "[magenta][25] Снеговик ☃️\n"
          "[magenta][26] Елочка 🎄\n"
          "[magenta][27] Дед мороз 🎅\n"
          "[magenta][28] Объятия 🤗\n"
          "[magenta][29] Непечатные выражения 🤬\n"
          "[magenta][30] Тошнота 🤮\n"
          "[magenta][31] Клоун 🤡\n"
          "[magenta][32] Одурманенное лицо 🥴\n"
          "[magenta][33] Влюбленный глаза 😍\n"
          "[magenta][34] Сто балов 💯\n"
          "[magenta][35] Хот-дог 🌭\n"
          "[magenta][36] Высокое напряжение ⚡️\n"
          "[magenta][37] Банан 🍌\n"
          "[magenta][38] Средний палец 🖕\n"
          "[magenta][39] Поцелуй 💋\n"
          "[magenta][40] Глаза 👀\n"
          "[magenta][41] Рукопожатие 🤝\n"
          "[magenta][42] Шампанское 🍾\n"
          "[magenta][43] Кубок 🏆\n"
          "[magenta][44] Зевота 🥱\n"
          "[magenta][45] Голубь мира 🕊\n"
          "[magenta][46] Слезы рекой 😭")

    user_input = console.input("[medium_purple3][+] Введите номер: ")

    if user_input == "0":
        reactions_for_groups_and_messages(reaction_input="👍", db_handler=db_handler)  # Поднятый большой палец
    elif user_input == "1":
        reactions_for_groups_and_messages(reaction_input="👎", db_handler=db_handler)  # Опущенный большой палец
    elif user_input == "2":
        reactions_for_groups_and_messages(reaction_input="❤", db_handler=db_handler)  # Красное сердце
    elif user_input == "3":
        reactions_for_groups_and_messages(reaction_input="🔥", db_handler=db_handler)  # Огонь
    elif user_input == "4":
        reactions_for_groups_and_messages(reaction_input="🎉", db_handler=db_handler)  # Хлопушка
    elif user_input == "5":
        reactions_for_groups_and_messages(reaction_input="😱", db_handler=db_handler)  # Лицо, кричащее от страха
    elif user_input == "6":
        reactions_for_groups_and_messages(reaction_input="😁", db_handler=db_handler)  # Широко улыбающееся лицо
    elif user_input == "7":
        reactions_for_groups_and_messages(reaction_input="😢",
                                          db_handler=db_handler)  # Лицо с открытым ртом и в холодном поту
    elif user_input == "8":
        reactions_for_groups_and_messages(reaction_input="💩", db_handler=db_handler)  # Фекалии
    elif user_input == "9":
        reactions_for_groups_and_messages(reaction_input="👏", db_handler=db_handler)  # Аплодирующие руки
    elif user_input == "11":
        reactions_for_groups_and_messages(reaction_input="🤷‍♀️", db_handler=db_handler)  # Женщина разводит руками
    elif user_input == "12":
        reactions_for_groups_and_messages(reaction_input="🤷", db_handler=db_handler)  # Человек разводит руками
    elif user_input == "13":
        reactions_for_groups_and_messages(reaction_input="🤷‍♂️", db_handler=db_handler)  # Мужчина разводит руками
    elif user_input == "14":
        reactions_for_groups_and_messages(reaction_input="👾️", db_handler=db_handler)  # Космический монстр
    elif user_input == "15":
        reactions_for_groups_and_messages(reaction_input="😎", db_handler=db_handler)  # Лицо в темных очках
    elif user_input == "16":
        reactions_for_groups_and_messages(reaction_input="🙊", db_handler=db_handler)  # Ничего не скажу
    elif user_input == "17":
        reactions_for_groups_and_messages(reaction_input="💊", db_handler=db_handler)  # Таблетка
    elif user_input == "18":
        reactions_for_groups_and_messages(reaction_input="😘", db_handler=db_handler)  # Воздушный поцелуй
    elif user_input == "19":
        reactions_for_groups_and_messages(reaction_input="🦄", db_handler=db_handler)  # Единорог
    elif user_input == "20":
        reactions_for_groups_and_messages(reaction_input="💘", db_handler=db_handler)  # Сердце со стрелой
    elif user_input == "21":
        reactions_for_groups_and_messages(reaction_input="🆒", db_handler=db_handler)  # Значок круто
    elif user_input == "22":
        reactions_for_groups_and_messages(reaction_input="🗿", db_handler=db_handler)  # Каменное лицо
    elif user_input == "23":
        reactions_for_groups_and_messages(reaction_input="🤪", db_handler=db_handler)  # Глупое лицо
    elif user_input == "24":
        reactions_for_groups_and_messages(reaction_input="💅", db_handler=db_handler)  # Маникюр
    elif user_input == "25":
        reactions_for_groups_and_messages(reaction_input="☃", db_handler=db_handler)  # Снеговик
    elif user_input == "26":
        reactions_for_groups_and_messages(reaction_input="🎄", db_handler=db_handler)  # Елочка
    elif user_input == "27":
        reactions_for_groups_and_messages(reaction_input="🎅", db_handler=db_handler)  # Дед мороз
    elif user_input == "28":
        reactions_for_groups_and_messages(reaction_input="🤗", db_handler=db_handler)  # Объятия
    elif user_input == "29":
        reactions_for_groups_and_messages(reaction_input="🤬", db_handler=db_handler)  # Непечатные выражения
    elif user_input == "30":
        reactions_for_groups_and_messages(reaction_input="🤮", db_handler=db_handler)  # Тошнота
    elif user_input == "31":
        reactions_for_groups_and_messages(reaction_input="🤡", db_handler=db_handler)  # Клоун
    elif user_input == "32":
        reactions_for_groups_and_messages(reaction_input="🥴", db_handler=db_handler)  # Одурманенное лицо
    elif user_input == "33":
        reactions_for_groups_and_messages(reaction_input="😍", db_handler=db_handler)  # Влюбленный глаза
    elif user_input == "34":
        reactions_for_groups_and_messages(reaction_input="💯", db_handler=db_handler)  # Сто балов
    elif user_input == "35":
        reactions_for_groups_and_messages(reaction_input="🌭", db_handler=db_handler)  # Хот-дог
    elif user_input == "36":
        reactions_for_groups_and_messages(reaction_input="⚡️", db_handler=db_handler)  # Высокое напряжение
    elif user_input == "37":
        reactions_for_groups_and_messages(reaction_input="🍌", db_handler=db_handler)  # Банан
    elif user_input == "38":
        reactions_for_groups_and_messages(reaction_input="🖕", db_handler=db_handler)  # Средний палец
    elif user_input == "39":
        reactions_for_groups_and_messages(reaction_input="💋", db_handler=db_handler)  # Поцелуй
    elif user_input == "40":
        reactions_for_groups_and_messages(reaction_input="👀", db_handler=db_handler)  # Глаза
    elif user_input == "41":
        reactions_for_groups_and_messages(reaction_input="🤝", db_handler=db_handler)  # Рукопожатие
    elif user_input == "42":
        reactions_for_groups_and_messages(reaction_input="🍾", db_handler=db_handler)  # Шампанское
    elif user_input == "43":
        reactions_for_groups_and_messages(reaction_input="🏆", db_handler=db_handler)  # Кубок
    elif user_input == "44":
        reactions_for_groups_and_messages(reaction_input="🥱", db_handler=db_handler)  # Зевота
    elif user_input == "45":
        reactions_for_groups_and_messages(reaction_input="🕊", db_handler=db_handler)  # Голубь мира
    elif user_input == "46":
        reactions_for_groups_and_messages(reaction_input="😭", db_handler=db_handler)  # Слезы рекой


def reactions_for_groups_and_messages(reaction_input, db_handler) -> None:
    """Вводим ссылку на группу и ссылку на сообщение"""
    chat = console.input("[medium_purple3][+] Введите ссылку на группу / канал: ")  # Ссылка на группу или канал
    message = console.input("[medium_purple3][+] Введите ссылку на сообщение или пост: ")  # Ссылка на сообщение
    records: list = choosing_a_number_of_reactions(db_handler)  # Выбираем лимиты для аккаунтов
    send_reaction_request(records, chat, message, reaction_input, db_handler)  # Ставим реакцию на пост, сообщение


def choosing_a_number_of_reactions(db_handler) -> list:
    """Выбираем лимиты для аккаунтов"""
    print("[medium_purple3]Введите количество с которых будут поставлены реакции")
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    records: list = db_handler.open_and_read_data("config")
    # Количество аккаунтов на данный момент в работе
    print(f"[medium_purple3]Всего accounts: {len(records)}")
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    number_of_accounts = console.input("[medium_purple3][+] Введите количество аккаунтов для выставления реакций: ")
    records: list = db_handler.open_the_db_and_read_the_data_lim(name_database_table="config",
                                                                 number_of_accounts=int(number_of_accounts))
    return records


def send_reaction_request(records, chat, message_url, reaction_input, db_handler) -> None:
    """Ставим реакции на сообщения"""
    for row in records:
        # Подключение к Telegram и вывод имени аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        try:
            subscribe_to_group_or_channel(client, chat, phone, db_handler)  # Подписываемся на группу
            number = re.search(r'/(\d+)$', message_url).group(1)
            time.sleep(5)
            client(SendReactionRequest(peer=chat, msg_id=int(number),
                                       reaction=[types.ReactionEmoji(emoticon=f'{reaction_input}')]))
            time.sleep(1)
        except KeyError:
            sys.exit(1)
        except Exception as e:
            logger.exception(e)
            print("[medium_purple3][!] Произошла ошибка, для подробного изучения проблемы просмотрите файл log.log")
        finally:
            client.disconnect()

    app_notifications(notification_text=f"Работа с группой {chat} окончена!")


def viewing_posts(db_handler) -> None:
    """Накрутка просмотров постов"""
    chat = console.input("[medium_purple3][+] Введите ссылку на канал: ")  # Ссылка на группу или канал
    records: list = db_handler.open_and_read_data("config")
    # Количество аккаунтов на данный момент в работе
    print(f"[medium_purple3]Всего accounts: {len(records)}")
    # Открываем базу данных для работы с аккаунтами user_settings/software_database.db
    number_of_accounts = console.input("[medium_purple3][+] Введите количество аккаунтов для просмотра постов: ")
    records: list = db_handler.open_the_db_and_read_the_data_lim(name_database_table="config",
                                                                 number_of_accounts=int(number_of_accounts))
    for row in records:
        # Подключение к Telegram и вывод имени аккаунта в консоль / терминал
        client, phone = telegram_connect_and_output_name(row, db_handler)
        try:
            subscribe_to_group_or_channel(client, chat, phone, db_handler)  # Подписываемся на группу
            channel = client.get_entity(chat)  # Получение информации о канале
            time.sleep(5)
            posts = client.get_messages(channel, limit=10)  # Получение последних 10 постов из канала
            for post in posts:  # Вывод информации о постах
                post_link = f"{chat}/{post.id}"  # Ссылка на пост
                print("Ссылка на пост:", post_link)
                print(f"Date: {post.date}\nText: {post.text}\n")
                number = re.search(r"/(\d+)$", post_link).group(1)
                time.sleep(5)
                client(GetMessagesViewsRequest(peer=channel, id=[int(number)], increment=True))
        except KeyError:
            sys.exit(1)
        except Exception as e:
            logger.exception(e)
            print("[medium_purple3][!] Произошла ошибка, для подробного изучения проблемы просмотрите файл log.log")
        finally:
            client.disconnect()

    app_notifications(notification_text=f"Работа с каналом {chat} окончена!")


if __name__ == "__main__":
    reaction_gui()
