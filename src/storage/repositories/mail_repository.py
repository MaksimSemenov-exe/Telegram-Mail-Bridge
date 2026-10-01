import sqlite3
import datetime
import logging
from src.utils.mask_email import mask_email


logger = logging.getLogger(__name__)


class MailRepository:
    def __init__(self, database):
        self.database = database

    def check_last_uid(self, email: str) -> int | None:
        """Возвращает последний обработанный uid для email или None, если записи нет"""
        try:
            query = "SELECT uid FROM last_mail WHERE email = ?"
            last_uid = self.database.cursor.execute(query, (email,)).fetchone()
        except sqlite3.Error:
            logger.exception("Не удалось получить last_uid (email=%s)", mask_email(email))
            raise

        if last_uid is None:
            logger.warning(
                "Запись в last_mail не найдена для email=%s", mask_email(email)
            )
            return None

        logger.debug("last_uid=%s для email=%s", last_uid[0], mask_email(email))
        return last_uid[0]

    def update_uid(self, uid: str, email: str) -> None:
        """Обновляет последний обработанный uid для email"""
        query = "UPDATE last_mail SET uid = ?, last_update = ? WHERE email = ?"
        last_update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.database.cursor.execute(
                query,
                (
                    uid,
                    last_update_time,
                    email,
                ),
            )
            self.database.conn.commit()
            logger.debug("UID обновлен для email=%s, uid=%s", mask_email(email), uid)
        except sqlite3.Error:
            logger.exception("Не удалось обновить UID email=%s", mask_email(email))
            self.database.conn.rollback()
            raise