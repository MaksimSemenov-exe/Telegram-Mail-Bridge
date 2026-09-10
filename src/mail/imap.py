from imap_tools import MailBox, A
import time
from src.storage.db import Database
from MailManager import MailManager

class MailClient:
    def __init__(self, server: str, username: str, password: str):
        self.server = server
        self.username = username
        self.password = password
        self.mail_manager = MailManager()
        self.mailbox = None
        self.responses = None

    def connect(self) -> bool:

        """Подключение к почтовому серверу"""

        try:
            self.mailbox = MailBox(self.server).login(self.username, self.password)
            print("Подключено")
            return True

        except Exception:
            print("Ошибка подключения")
            return False

    def fetch_unseen(self) -> list[dict[str, str]]:
        """Парсинг непрочитанных писем в почте"""
        messages = []
        for msg in self.mailbox.fetch(A(seen=False)):
            messages.append(
                {
                    "uid": msg.uid,
                    "date": msg.date,
                    "subject": msg.subject,
                    "from": msg.from_,
                    "text": msg.text,
                }
            )
        return messages

    def idle(self, user_id, callback=None):

        """Работа с почтовым сервисом используя IDLE-режим с таймаутом 60 секунд"""

        while True:

            db = Database()

            if not db.is_active(user_id):
                print('Пользователь отключил IDLE-режим')
                self.disconnect()
                break

            if not self.mailbox:
                if not self.connect():
                    time.sleep(5)
                    continue
            responses = self.mailbox.idle.wait(timeout=60)
            print(responses)

            if responses:
                messages = self.fetch_unseen()
                print(messages)
                print("Найдены письма, вызов коллбэка")
                for msg in messages:
                    if callback:
                        callback(msg)

    def manual_mail_check(self):
        db = Database()
        unseen_mail = self.mailbox.fetch(A(seen=False))

    def disconnect(self):
        """Отключение от почтового сервиса"""
        self.mailbox.disconnect()
        self.mailbox.logout()

