# -*- coding: utf-8 -*-
import asyncio
import random
import sqlite3

from loguru import logger
from telethon.errors import (
    ChannelPrivateError, SessionRevokedError, UserDeactivatedBanError, UsernameInvalidError, InviteRequestSentError,
    FloodWaitError, PeerFloodError, ChannelsTooMuchError
)
from telethon.tl.functions.channels import JoinChannelRequest

from src.core.utils import Utils
from src.gui.gui import AppLogger
from src.locales.translations_loader import translations


class Subscribe:

    def __init__(self, page):
        """
        Инициализация класса для подписки на группы и каналы в Telegram.

        :param page: Страница интерфейса Flet для отображения элементов управления
        """
        self.page = page  # Страница интерфейса Flet для отображения элементов управления.
        self.app_logger = AppLogger(page=page)
        self.utils = Utils(page=page)

    async def subscribe_to_group_or_channel(self, client, groups) -> None:
        """
        Подписывается на указанную группу или канал.

        :param client: Экземпляр клиента Telegram
        :param groups: Ссылка на группу или канал
        :return: None
        """
        # цикл for нужен для того, что бы сработала команда brake команда break в Python используется только для выхода из
        # цикла, а не выхода из программы в целом.
        await self.app_logger.log_and_display(f"✅ Группа для подписки {groups}")
        try:
            await client(JoinChannelRequest(groups))
            await self.app_logger.log_and_display(f"✅ Аккаунт подписался на группу / канал: {groups}")
        except SessionRevokedError:
            await self.app_logger.log_and_display(translations["ru"]["errors"]["invalid_auth_session_terminated"])
        except UserDeactivatedBanError:
            await self.app_logger.log_and_display(
                f"❌ Попытка подписки на группу / канал {groups}. Аккаунт заблокирован.")
        except ChannelsTooMuchError:
            """Если аккаунт подписан на множество групп и каналов, то отписываемся от них"""
            async for dialog in client.iter_dialogs():
                await self.app_logger.log_and_display(f"{dialog.name}, {dialog.id}")
                try:
                    await client.delete_dialog(dialog)
                except ConnectionError:
                    break
            await self.app_logger.log_and_display(f"❌  Список почистили, и в файл записали.")
        except ChannelPrivateError:
            await self.app_logger.log_and_display(translations["ru"]["errors"]["channel_private"])
        except (UsernameInvalidError, ValueError, TypeError):
            await self.app_logger.log_and_display(
                f"❌ Попытка подписки на группу / канал {groups}. Не верное имя или cсылка {groups} не является группой / каналом: {groups}")
        except PeerFloodError:
            await self.app_logger.log_and_display(translations["ru"]["errors"]["peer_flood"], level="error")
            await asyncio.sleep(random.randrange(50, 60))
        except FloodWaitError as e:
            await self.app_logger.log_and_display(f"{translations["ru"]["errors"]["flood_wait"]}{e}", level="error")
            raise  # ← ВАЖНО пробрасываем ошибку наружу
        except InviteRequestSentError:
            await self.app_logger.log_and_display(
                f"❌ Попытка подписки на группу / канал {groups}. Действия будут доступны после одобрения администратором на вступление в группу")
        except sqlite3.DatabaseError:
            await self.app_logger.log_and_display(
                f"❌ Попытка подписки на группу / канал {groups}. Ошибка базы данных, аккаунта или аккаунт заблокирован.")
        except Exception as e:  # Ловим все остальные ошибки
            logger.exception(e)
