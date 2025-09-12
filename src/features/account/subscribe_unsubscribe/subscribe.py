# -*- coding: utf-8 -*-
import asyncio
import random
import sqlite3

from telethon.errors import (ChannelPrivateError, SessionRevokedError, UserDeactivatedBanError, UsernameInvalidError,
                             InviteRequestSentError, FloodWaitError, PeerFloodError, ChannelsTooMuchError)
from telethon.tl.functions.channels import JoinChannelRequest

from src.core.configs import time_subscription_1, time_subscription_2
from src.core.sqlite_working_tools import write_data_to_db
from src.core.utils import record_and_interrupt
from src.gui.gui import AppLogger
from src.locales.translations_loader import translations


class Subscribe:

    def __init__(self, page):
        self.page = page  # Страница интерфейса Flet для отображения элементов управления.
        self.app_logger = AppLogger(page=page)

    async def subscribe_to_group_or_channel(self, client, groups_wr) -> None:
        """
        Подписываемся на группу или канал

        :param groups_wr: Str - группа или канал
        :param client:    TelegramClient - объект клиента
        """
        # цикл for нужен для того, что бы сработала команда brake команда break в Python используется только для выхода из
        # цикла, а не выхода из программы в целом.
        await self.app_logger.log_and_display(f"Группа для подписки {groups_wr}")
        try:
            await client(JoinChannelRequest(groups_wr))
            await self.app_logger.log_and_display(f"Аккаунт подписался на группу / канал: {groups_wr}")
        except SessionRevokedError:
            await self.app_logger.log_and_display(translations["ru"]["errors"]["invalid_auth_session_terminated"])
        except UserDeactivatedBanError:
            await self.app_logger.log_and_display(
                f"❌ Попытка подписки на группу / канал {groups_wr}. Аккаунт заблокирован.")
        except ChannelsTooMuchError:
            """Если аккаунт подписан на множество групп и каналов, то отписываемся от них"""
            async for dialog in client.iter_dialogs():
                await self.app_logger.log_and_display(f"{dialog.name}, {dialog.id}")
                try:
                    await client.delete_dialog(dialog)
                    await client.disconnect()
                except ConnectionError:
                    break
            await self.app_logger.log_and_display(f"❌  Список почистили, и в файл записали.")
        except ChannelPrivateError:
            await self.app_logger.log_and_display(translations["ru"]["errors"]["channel_private"])
        except (UsernameInvalidError, ValueError, TypeError):
            await self.app_logger.log_and_display(
                f"❌ Попытка подписки на группу / канал {groups_wr}. Не верное имя или cсылка {groups_wr} не является группой / каналом: {groups_wr}")
            write_data_to_db(groups_wr)
        except PeerFloodError:
            await self.app_logger.log_and_display(translations["ru"]["errors"]["peer_flood"], level="error")
            await asyncio.sleep(random.randrange(50, 60))
        except FloodWaitError as e:
            await self.app_logger.log_and_display(f"{translations["ru"]["errors"]["flood_wait"]}{e}", level="error")
            await record_and_interrupt(time_subscription_1, time_subscription_2, self.page)
            # Прерываем работу и меняем аккаунт
            raise
        except InviteRequestSentError:
            await self.app_logger.log_and_display(
                f"❌ Попытка подписки на группу / канал {groups_wr}. Действия будут доступны после одобрения администратором на вступление в группу")
        except sqlite3.DatabaseError:
            await self.app_logger.log_and_display(
                f"❌ Попытка подписки на группу / канал {groups_wr}. Ошибка базы данных, аккаунта или аккаунт заблокирован.")
