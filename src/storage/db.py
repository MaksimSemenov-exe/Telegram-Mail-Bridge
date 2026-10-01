import sqlite3
import os
import datetime
import logging
from src.utils.mask_email import mask_email
from src.utils.custom_exceptions import UserNotFound


logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(self.current_dir, "mail.db")
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        logger.info('Соединение с БД открыто %s', self.db_path)

    def create_database(self):
        """Создание таблицы users в БД"""
        try:
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    email TEXT,
                    password TEXT,
                    imap_server TEXT,
                    imap_port INTEGER,
                    smtp_server TEXT,
                    smtp_port INTEGER,
                    created_at TEXT,
                    is_active INTEGER DEFAULT 1,
                    last_success TEXT,
                    attachments_enabled INTEGER DEFAULT 1
                )
            """
            )
            self.conn.commit()
            logger.info("Таблица users создана")
        except sqlite3.Error:
            logger.exception("Ошибка при создании таблицы users")
            raise

        try:
            self.cursor.execute(
                """CREATE TABLE IF NOT EXISTS last_mail (email TEXT, uid INTEGER DEFAULT 0, last_update TEXT)"""
            )
            self.conn.commit()
            logger.info("Таблица last_mail создана")
        except sqlite3.Error:
            logger.exception("Ошибка при создании таблицы last_mail")

