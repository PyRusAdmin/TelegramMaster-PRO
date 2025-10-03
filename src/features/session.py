from telethon.sessions import StringSession
from telethon.sync import TelegramClient

api_id = 7655060
api_hash = "cc1290cd733c1f1d407598e5a31be4a8"

with TelegramClient(StringSession(), api_id, api_hash, system_version="4.16.30-vxCUSTOM") as client:
    # Авторизация
    client.start()

    # Сохраняем строку сессии (после успешного входа)
    print("StringSession:", client.session.save())

# client = TelegramClient(StringSession(), api_id=7655060, api_hash="cc1290cd733c1f1d407598e5a31be4a8",
#                         system_version="4.16.30-vxCUSTOM")
# client.connect()
#
# client = TelegramClient('sqlite-session', api_id=7655060, api_hash="cc1290cd733c1f1d407598e5a31be4a8")
# string = StringSession.save(client.session)
#
# with TelegramClient(StringSession(string), api_id=7655060, api_hash="cc1290cd733c1f1d407598e5a31be4a8") as client:
#     string = client.session.save()

# class CreateString:
#     def __init__(self, api_id: int, api_hash: str, session: str) -> None:
#         self.client = TelegramClient(session, api_id, api_hash)
#
#     async def GenerateStringSession(self) -> str:
#         await self.client.start()
#         string_session = sessions.StringSession(self.client.session).save()
#         await self.client.disconnect()
#         return string_session
#
# if __name__ == "__main__":
#     import asyncio
#
#     api_id = int(input("Введите ваш API ID: "))
#     api_hash = input("Введите ваш API Hash: ")
#     session_name = input("Введите имя для вашей сессии (например, 'my_session'): ")
#
#     creator = CreateString(api_id, api_hash, session_name)
#     string_session = asyncio.run(creator.GenerateStringSession())
#     print(f"Ваша строковая сессия: {string_session}")
