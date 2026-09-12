import time
import logging
from imap_tools import MailBox, A
from src.storage.db import Database


logger = logging.getLogger(__name__)


class MailClient:
    def __init__(self, server: str, username: str, password: str):
        self.server = server
        self.username = username
        self.password = password
        self.user_id = Database().get_user_id_by_email(self.username)
        self.mailbox = None
        self.responses = None

    def connect(self) -> bool:
        """Подключение к почтовому серверу"""
        try:
            self.mailbox = MailBox(self.server).login(self.username, self.password)
            logger.info(
                "Успешное подключение по IMAP для пользователя user=%s", self.username
            )
            return True

        except Exception:
            logger.exception("Попытка подключеия по IMAP не удалась")
            return False

    def fetch_unseen(self) -> list[dict[str, str]]:
        """Парсинг непрочитанных писем в почте"""
        messages = []
        try:
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
        except Exception:
            logger.exception("Не удалось получить непрочитанные письма")
        return messages

    def idle(self, callback=None):

        """Работа с почтовым сервисом используя IDLE-режим с таймаутом 60 секунд"""

        logger.info("Запуск IDLE-режима для пользователя user=%s", self.user_id)
        db = Database()

        while True:

            if not db.is_active(self.user_id):
                logger.info("Пользователь user_id=%s отключил IDLE-режим", self.user_id)
                self.disconnect()
                break

            if not self.mailbox:
                logger.info(
                    "Нет активного соединения с IMAP-сервером (user_id=%s), попытка подключения ",
                    self.user_id,
                )
                if not self.connect():
                    logger.info(
                        "Подключение к IMAP-серверу %s не удалось, повтор через 5 секунд (user_id=%s)",
                        self.server,
                        self.user_id,
                    )
                    time.sleep(5)
                    continue

            responses = self.mailbox.idle.wait(timeout=60)
            print(responses)

            if responses:
                logger.info("Получены непрочитанные письма (user_id=%s)", self.user_id)
                messages = self.fetch_unseen()
                logger.info(
                    "Получено непрочитанных писем: %d (user_id=%s)",
                    len(messages),
                    self.user_id,
                )
                print("Найдены письма, вызов коллбэка")
                for msg in messages:
                    if callback:
                        callback(msg)
            else:
                logger.debug("IDLE: таймаут, событий нет (user_id=%s)", self.user_id)

    def disconnect(self):
        """Отключение от почтового сервиса"""
        try:
            self.mailbox.disconnect()
            self.mailbox.logout()
            logger.info(
                "Соединение с IMAP %s закрыто (user_id=%s)", self.server, self.user_id
            )
        except Exception:
            logger.exception(
                "Не удалось закрыть соединение с IMAP %s (user_id=%s)",
                self.server,
                self.user_id,
            )
