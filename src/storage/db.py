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
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        logger.info('Соединение с БД открыто %s', self.db_path)

    def add_user(
        self,
        user_id,
        email,
        password,
        imap_server,
        imap_port,
        smtp_server,
        smtp_port,
        created_at,
    ):
        """Добавление нового пользователя в таблицу users в БД"""
        users_table_query = "INSERT INTO users (user_id, email, password, imap_server, imap_port, smtp_server, smtp_port, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        try:
            self.cursor.execute(
                users_table_query,
                (
                    user_id,
                    email,
                    password,
                    imap_server,
                    imap_port,
                    smtp_server,
                    smtp_port,
                    created_at,
                ),
            )

            last_mail_table_query = (
                "INSERT INTO last_mail (email, uid, last_update) VALUES (?, ?, ?)"
            )
            self.cursor.execute(
                last_mail_table_query,
                (
                    email,
                    0,
                    0,
                ),
            )
            self.conn.commit()
            logger.info("Пользователь user_id=%s добавлен в БД", user_id)
        except sqlite3.Error:
            logger.exception(
                "Не удалось добавить пользователя user_id=%s в БД", user_id
            )
            self.conn.rollback()
            raise

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
                    is_active INTEGER DEFAULT 1
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

    def check_last_uid(self, email):
        try:
            query = "SELECT uid FROM last_mail WHERE email = ?"
            last_uid = self.cursor.execute(query, (email,)).fetchone()
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

    def update_uid(self, uid, email):
        query = "UPDATE last_mail SET uid = ?, last_update = ? WHERE email = ?"
        last_update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.cursor.execute(
                query,
                (
                    uid,
                    last_update_time,
                    email,
                ),
            )
            self.conn.commit()
            logger.debug("UID обновлен для email=%s, uid=%s", mask_email(email), uid)
        except sqlite3.Error:
            logger.exception("Не удалось обновить UID email=%s", mask_email(email))
            self.conn.rollback()
            raise

    def get_all_users(self):
        """Получение всех записей из таблицы users в БД"""
        query = "SELECT * FROM users"
        try:
            data = self.cursor.execute(query).fetchall()
        except sqlite3.Error:
            logger.exception("Не удалось получить выгрузку из БД (*)")
            return []
        if not data:
            logger.warning("Таблица users пуста")
        else:
            logger.info("Получено пользователей: %d", len(data))
        return data

    def get_user_info(self, user_id):
        query = "SELECT * FROM users WHERE user_id = ?"
        try:
            settings = self.cursor.execute(query, (user_id,)).fetchone()
        except sqlite3.Error:
            logger.exception("Не удалось получить информацию о user_id=%s", user_id)
            raise

        if settings is None:
            logger.warning("Пользователь user_id=%s не найден", user_id)
        else:
            logger.debug("Получена информация из БД о user_id=%s", user_id)
        return settings

    def is_active(self, user_id):
        query = "SELECT is_active FROM users WHERE user_id = ?"
        try:
            active_status = self.cursor.execute(query, (user_id,)).fetchone()
        except sqlite3.Error:
            logger.exception("Не удалось проверить is_active для user_id=%s", user_id)
            raise
        if active_status is None:
            logger.warning("Пользователь user_id=%s не найден", user_id)
            return False
        return bool(active_status[0])

    def delete_user(self, user_id):
        query = "DELETE FROM users WHERE user_id = ?"
        try:
            self.cursor.execute(query, (user_id,))
            self.conn.commit()
        except sqlite3.Error:
            logger.exception("Не удалось удалить user_id=%s", user_id)
            self.conn.rollback()
            raise

    def stop_idle(self, user_id):
        """Смена значения в столбце is_active для остановки IDLE-режима для пользователя"""
        query = "SELECT is_active FROM users WHERE user_id = ?"
        try:
            row = self.cursor.execute(query, (user_id,)).fetchone()
        except sqlite3.Error:
            logger.exception("Ошибка SELECT при остановке IDLE user_id=%s", user_id)
            raise
        if row is None:
            logger.warning("user_id=%s не найден, IDLE не остановлен", user_id)
            return "not_found"
        if row[0] == 0:
            logger.info("IDLE уже был остановлен user_id=%s", user_id)
            return "already_stopped"
        query = "UPDATE users SET is_active = 0 WHERE user_id = ?"
        try:
            self.cursor.execute(query, (user_id,))
            self.conn.commit()
        except sqlite3.Error:
            logger.exception("Ошибка при остановке IDLE user_id=%s", user_id)
            self.conn.rollback()
            raise

        logger.info("IDLE был остановлен user_id=%s", user_id)
        return "stopped"

    def get_user_id_by_email(self, email):
        query = "SELECT user_id FROM users WHERE email = ?"
        try:
            result = self.cursor.execute(query, (email,)).fetchone()
        except sqlite3.Error:
            logger.exception("Ошибка при запросе к БД email=%s", mask_email(email))
            raise

        if result is None:
            logger.warning("Пользователь не найден email=%s", mask_email(email))
            raise UserNotFound(f"email={mask_email(email)}")
        return result[0]

    def set_active(self, user_id, value):
        query = 'UPDATE users SET is_active = ? WHERE user_id = ?'
        try:
            cursor = self.cursor.execute(query, (value, user_id))
            self.conn.commit()
        except sqlite3.Error:
            logger.exception('Не удалось обновить is_active user_id=%s', user_id)
            self.conn.rollback()
            raise
        return cursor.rowcount > 0

    def is_registered(self, user_id):
        query = 'SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?)'
        try:
            row = self.cursor.execute(query, (user_id,)).fetchone()
        except sqlite3.Error:
            logger.exception('Не удалось проверить существование user_id=%s', user_id)
            raise

        if row is None:
            return False

        return bool(row[0])