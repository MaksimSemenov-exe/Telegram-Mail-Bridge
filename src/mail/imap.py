import time
import logging
from imap_tools import MailBox, A
from src.storage.db import Database
from src.utils.custom_exceptions import UserNotFound
from src.utils.mask_email import mask_email

logger = logging.getLogger(__name__)


class MailClient:
    def __init__(self, server: str, username: str, password: str):
        self.server = server
        self.username = username
        self.password = password
        self.mailbox = None
        self.responses = None

        try:
            self.user_id = Database().get_user_id_by_email(self.username)
        except UserNotFound:
            logger.warning("Пользователь не найден user=%s", mask_email(self.username))
            raise
        except Exception:
            logger.exception(
                "Ошибка БД при получении user=%s", mask_email(self.username)
            )
            raise

    def connect(self) -> bool:
        """Подключение к почтовому серверу"""
        try:
            self.mailbox = MailBox(self.server).login(self.username, self.password)
            logger.info(
                "Успешное подключение по IMAP для пользователя user=%s",
                mask_email(self.username),
            )
            return True

        except Exception:
            logger.exception(
                "Не удалось подключиться к IMAp %s user=%s",
                self.server,
                mask_email(self.username),
            )
            return False

    def fetch_unseen(self) -> list[dict[str, str]]:
        """Парсинг непрочитанных писем в почте"""
        messages = []
        try:
            for msg in self.mailbox.fetch(A(seen=False)):
                attachments = []
                for att in msg.attachments:
                    attachments.append({'filename': att.filename, 'payload': att.payload})
                messages.append(
                    {
                        "uid": msg.uid,
                        "date": msg.date,
                        "subject": msg.subject,
                        "from": msg.from_,
                        "text": msg.text,
                        'attachments': attachments
                    }
                )
        except Exception:
            logger.exception(
                "Не удалось получить письма user_id=%s", mask_email(self.username)
            )
        return messages

    def idle(self, callback=None):

        """Работа с почтовым сервисом используя IDLE-режим с таймаутом 60 секунд"""

        logger.info("Запуск IDLE-режима для пользователя user_id=%s", self.user_id)
        db = Database()

        while True:
            try:
                is_active = db.is_active(self.user_id)
            except Exception:
                logger.exception(
                    "Ошибка проверки is_active user_id=%s, повтор через 5 секунд",
                    self.user_id,
                )
                time.sleep(5)
                continue

            if is_active is None:
                logger.warning('Пользователь не найден, IDLE остановлен user_id=%s', self.user_id)
                self.disconnect()
                break

            if not is_active:
                logger.info("Пользователь user_id=%s отключил IDLE-режим", self.user_id)
                self.disconnect()
                break

            if not self.mailbox:
                logger.info(
                    "Нет активного соединения с IMAP %s user_id=%s, попытка подключения",
                    self.server,
                    self.user_id,
                )
                if not self.connect():
                    logger.warning(
                        "Повтор подключения через 5 с user_id=%s",
                        self.user_id,
                    )
                    time.sleep(5)
                    continue
            try:
                responses = self.mailbox.idle.wait(timeout=60)
            except Exception:
                logger.exception(
                    "Ошибка в IDLE, сбрасываю соединение user_id=%s", self.user_id
                )
                self.mailbox = None
                time.sleep(5)
                continue

            try:
                db.update_last_success(self.user_id)
            except Exception:
                logger.debug("last_success не обновлён user_id=%s, детали в db.py", self.user_id)

            logger.debug("IDLE wait вернул: %r user_id=%s", responses, self.user_id)

            if responses:
                logger.info("Получены непрочитанные письма (user_id=%s)", self.user_id)
                messages = self.fetch_unseen()
                logger.info(
                    "Получено непрочитанных писем: %d (user_id=%s)",
                    len(messages),
                    self.user_id,
                )
                for msg in messages:
                    if callback:
                        try:
                            callback(msg)
                        except Exception:
                            logger.exception(
                                "Ошибка в callback UID=%s, user_id=%s",
                                msg["uid"],
                                self.user_id,
                            )
            else:
                logger.debug("IDLE: таймаут, событий нет (user_id=%s)", self.user_id)

    def disconnect(self):
        """Отключение от почтового сервиса"""
        if not self.mailbox:
            return

        try:
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
        finally:
            self.mailbox = None
