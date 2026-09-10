import asyncio
import threading
from src.mail.imap import MailClient
from src.storage.db import Database
from imap_tools import MailMessage

class MailManager:
    def __init__(self, app, loop):
        self.app = app
        self.loop = loop
        self.threads = []
        self.db = Database()

    def start_idle_for_user(self, server: str, username: str, password: str, chat_id: int) -> None:
        client = MailClient(server, username, password)
        client.connect()

        def handle_new_message(msg):
            db_local = Database()
            text = f'От: {msg['from']}\nТема: {msg["subject"]}\nТекст: {msg['text']}'
            print(f"Отправка письма")
            asyncio.run_coroutine_threadsafe(self.app.bot.send_message(chat_id, text), self.loop)
            db_local.update_uid(msg['uid'], client.username)

        print('Idle открыт')
        client.idle(handle_new_message)

    def start_idle_for_all_users(self) -> None:

        users = self.db.get_all_users()

        for user in users:
            thread = threading.Thread(target=self.start_idle_for_user, args=(user[3], user[1], user[2], user[0]), daemon=True
                ).start()
            self.threads.append(thread)

    def start_thread_for_user(self, server: str, username: str, password: str, chat_id: int ) -> None:
        thread = threading.Thread(
            target=self.start_idle_for_user,
            args=(server, username, password, chat_id),
            daemon=True
        ).start()

        self.threads.append(thread)
        print('Thread открыт')

    def message_for_manual_check(self, mails, chat_id) -> None:
        for mail in mails:
            text = f'От: {mail.from_}\nТема: {mail.subject}\nТекст: {mail.text}'
            asyncio.run_coroutine_threadsafe(self.app.bot.send_message(chat_id, text), self.loop)

