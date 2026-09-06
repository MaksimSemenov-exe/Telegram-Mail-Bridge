import asyncio
from src.mail.imap import MailClient
from src.storage.db import Database
import threading

class MailManager:
    def __init__(self):
        pass

    def start_idle(self, user_data, loop, app):
        client = MailClient(
            server=user_data[3],
            username=user_data[1],
            password=user_data[2],
        )
        client.connect()
        print("CONNECTED")
        chat_id = user_data[0]

        def handle_new_message(msg):
            db_local = Database()
            text = f'От: {msg['from']}\nТема: {msg["subject"]}\nТекст: {msg['text']}'
            print(f"Отправка письма")
            asyncio.run_coroutine_threadsafe(app.bot.send_message(chat_id, text), loop)
            db_local.update_uid(msg['uid'], client.username)

            client.idle(handle_new_message)

    def start_idle_for_user(self, user_data, start_idle):
        client = MailClient(
            server=user_data[3],
            username=user_data[1],
            password=user_data[2],
        )
        loop = asyncio.get_event_loop()
        threading.Thread(target=start_idle, args=(user_data, loop), daemon=True).start()