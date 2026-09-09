import asyncio
import random
import sqlite3

import flet as ft
from loguru import logger
from telethon.errors import (
    ChannelPrivateError, SessionRevokedError, UserDeactivatedBanError, UsernameInvalidError, InviteRequestSentError,
    FloodWaitError, PeerFloodError, ChannelsTooMuchError, UserNotParticipantError
)
from telethon.tl.functions.channels import JoinChannelRequest

from src.core.utils import Utils
from src.gui.gui import AppLogger
from src.locales.translations_loader import translations


class Subscribe:

    def __init__(self, page: ft.Page):
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
        normalized_group = self.utils.normalize_telegram_link(groups)
        if normalized_group:
            groups = normalized_group

        # цикл for нужен для того, что бы сработала команда brake команда break в Python используется только для выхода из
        # цикла, а не выхода из программы в целом.
        await self.app_logger.log_and_display(f"✅ Группа для подписки {groups}")
        try:
            await client(JoinChannelRequest(groups))
            await self.app_logger.log_and_display(f"✅ Аккаунт подписался на группу / канал: {groups}")
        except SessionRevokedError as e:
            logger.error(f"Сессия прекращена при подписке на {groups}: {e}")
            await self.app_logger.log_and_display(translations["ru"]["errors"]["invalid_auth_session_terminated"])
        except UserDeactivatedBanError as e:
            logger.error(f"Аккаунт заблокирован при попытке подписки на {groups}: {e}")
            await self.app_logger.log_and_display(
                f"❌ Попытка подписки на группу / канал {groups}. Аккаунт заблокирован.")
        except ChannelsTooMuchError as e:
            logger.error(f"Достигнут лимит каналов/групп (ChannelsTooMuchError): {e}")
            await self.app_logger.log_and_display(f"❌ Достигнут лимит каналов/групп: {e}", level="error")
            """Если аккаунт подписан на множество групп и каналов, то отписываемся от них"""
            try:
                async for dialog in client.iter_dialogs():
                    await self.app_logger.log_and_display(f"{dialog.name}, {dialog.id}")
                    try:
                        await client.delete_dialog(dialog)
                    except ConnectionError as conn_err:
                        logger.warning(f"Ошибка соединения при удалении диалога {dialog.name}: {conn_err}")
                        break
                    except UserNotParticipantError as unp_err:
                        logger.warning(f"Пользователь не является участником {dialog.name} ({dialog.id}): {unp_err}")
                    except Exception as del_err:
                        logger.error(f"Ошибка при удалении диалога {dialog.name} ({dialog.id}): {del_err}")
                await self.app_logger.log_and_display(f"❌ Список почистили, и в файл записали.")
            except Exception as dialog_err:
                logger.exception(f"Ошибка при очистке диалогов аккаунта: {dialog_err}")
        except UserNotParticipantError as e:
            logger.warning(f"Пользователь не является участником группы/канала {groups}: {e}")
            await self.app_logger.log_and_display(f"❌ Пользователь не является участником {groups}")
        except ChannelPrivateError as e:
            logger.warning(f"Приватный канал {groups}: {e}")
            await self.app_logger.log_and_display(translations["ru"]["errors"]["channel_private"])
        except (UsernameInvalidError, ValueError, TypeError) as e:
            logger.warning(f"Неверная ссылка или имя группы {groups}: {e}")
            await self.app_logger.log_and_display(
                f"❌ Попытка подписки на группу / канал {groups}. Не верное имя или cсылка {groups} не является группой / каналом: {groups}")
        except PeerFloodError as e:
            logger.error(f"PeerFloodError при подписке на {groups}: {e}")
            await self.app_logger.log_and_display(translations["ru"]["errors"]["peer_flood"], level="error")
            await asyncio.sleep(random.randrange(50, 60))
        except FloodWaitError as e:
            logger.error(f"FloodWaitError при подписке на {groups}: {e}")
            await self.app_logger.log_and_display(f"{translations['ru']['errors']['flood_wait']}{e}", level="error")
            raise  # ← ВАЖНО пробрасываем ошибку наружу
        except InviteRequestSentError as e:
            logger.info(f"Заявка на вступление отправлена для {groups}: {e}")
            await self.app_logger.log_and_display(
                f"❌ Попытка подписки на группу / канал {groups}. Действия будут доступны после одобрения администратором на вступление в группу")
        except sqlite3.DatabaseError as e:
            logger.error(f"DatabaseError при подписке на {groups}: {e}")
            await self.app_logger.log_and_display(
                f"❌ Попытка подписки на группу / канал {groups}. Ошибка базы данных, аккаунта или аккаунт заблокирован.")
        except Exception as e:  # Ловим все остальные ошибки
            logger.exception(f"Необработанная ошибка при подписке на группу/канал {groups}: {e}")
