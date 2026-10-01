import sqlite3
import datetime
import logging
from src.utils.mask_email import mask_email
from src.utils.custom_exceptions import UserNotFound


logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, database):
        self.database = database

    def add_user(
        self,
        user_id: int,
        email: str,
        password: str,
        imap_server: str,
        imap_port: str,
        smtp_server: str,
        smtp_port: int,
        created_at: str,
        attachments_enabled: bool
    ) -> None:
        """Добавление нового пользователя в таблицу users в БД"""
        users_table_query = "INSERT INTO users (user_id, email, password, imap_server, imap_port, smtp_server, smtp_port, created_at, attachments_enabled) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        try:
            self.database.cursor.execute(
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
                    attachments_enabled
                ),
            )

            last_mail_table_query = (
                "INSERT INTO last_mail (email, uid, last_update) VALUES (?, ?, ?)"
            )
            self.database.cursor.execute(
                last_mail_table_query,
                (
                    email,
                    0,
                    0,
                ),
            )
            self.database.conn.commit()
            logger.info("Пользователь user_id=%s добавлен в БД", user_id)
        except sqlite3.Error:
            logger.exception(
                "Не удалось добавить пользователя user_id=%s в БД", user_id
            )
            self.database.conn.rollback()
            raise

    def get_all_users(self) -> list[tuple]:
        """Получение всех записей из таблицы users в БД"""
        query = "SELECT * FROM users"
        try:
            data = self.database.cursor.execute(query).fetchall()
        except sqlite3.Error:
            logger.exception("Не удалось получить выгрузку из БД (*)")
            return []
        if not data:
            logger.warning("Таблица users пуста")
        else:
            logger.info("Получено пользователей: %d", len(data))
        return data

    def get_user_info(self, user_id: int) -> tuple | None:
        """Получение полной информации по определенному пользователю из таблицы users"""
        query = "SELECT * FROM users WHERE user_id = ?"
        try:
            settings = self.database.cursor.execute(query, (user_id,)).fetchone()
        except sqlite3.Error:
            logger.exception("Не удалось получить информацию о user_id=%s", user_id)
            raise

        if settings is None:
            logger.warning("Пользователь user_id=%s не найден", user_id)
        else:
            logger.debug("Получена информация из БД о user_id=%s", user_id)
        return settings

    def is_active(self, user_id: int) -> bool | None:
        """Проверка, активен ли IDLE-режи для пользователя из таблицы users. Возвращает True/False, None если пользователь не найден"""
        query = "SELECT is_active FROM users WHERE user_id = ?"
        try:
            row = self.database.cursor.execute(query, (user_id,)).fetchone()
        except sqlite3.Error:
            logger.exception("Не удалось проверить is_active для user_id=%s", user_id)
            raise
        if row is None:
            logger.warning("Пользователь user_id=%s не найден", user_id)
            return None
        return bool(row[0])

    def delete_user(self, user_id: int) -> bool:
        try:
            row = self.database.cursor.execute('SELECT email FROM users WHERE user_id = ?', (user_id,)).fetchone()
        except sqlite3.Error:
            logger.exception('Не удалось получить email user_id=%s', user_id)
            raise

        if row is None:
            logger.warning('user_id=%s не найден для удаления', user_id)
            return False

        email = row[0]

        try:
            self.database.cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id, ))
            self.database.cursor.execute('DELETE FROM last_mail WHERE email = ?', (email, ))
            self.database.conn.commit()
        except sqlite3.Error:
            logger.exception("Не удалось удалить user_id=%s", user_id)
            self.database.conn.rollback()
            raise

        logger.info('user_id=%s удален', user_id)
        return True

    def stop_idle(self, user_id: int) -> str:
        """Смена значения в столбце is_active в таблицу users для остановки IDLE-режима для пользователя"""
        query = "SELECT is_active FROM users WHERE user_id = ?"
        try:
            row = self.database.cursor.execute(query, (user_id,)).fetchone()
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
            self.database.cursor.execute(query, (user_id,))
            self.database.conn.commit()
        except sqlite3.Error:
            logger.exception("Ошибка при остановке IDLE user_id=%s", user_id)
            self.database.conn.rollback()
            raise

        logger.info("IDLE был остановлен user_id=%s", user_id)
        return "stopped"

    def get_user_id_by_email(self, email: str) -> int:
        """Получение значения поля user_id по значению поля email пользователя в таблице users. Если не удалось найти - UserNotFound"""
        query = "SELECT user_id FROM users WHERE email = ?"
        try:
            result = self.database.cursor.execute(query, (email,)).fetchone()
        except sqlite3.Error:
            logger.exception("Ошибка при запросе к БД email=%s", mask_email(email))
            raise

        if result is None:
            logger.warning("Пользователь не найден email=%s", mask_email(email))
            raise UserNotFound(f"email={mask_email(email)}")
        return result[0]

    def set_active(self, user_id: int, value: int) -> bool:
        """Изменение статуса активности IDLE-режима для пользователя. Реализовано через столбец is_active в таблице users"""
        query = 'UPDATE users SET is_active = ? WHERE user_id = ?'
        try:
            cursor = self.database.cursor.execute(query, (value, user_id))
            self.database.conn.commit()
        except sqlite3.Error:
            logger.exception('Не удалось обновить is_active user_id=%s', user_id)
            self.database.conn.rollback()
            raise
        return cursor.rowcount > 0

    def is_registered(self, user_id: int) -> bool:
        """Проверка на то, зарегистрирован ли пользователь. Осуществляется через поиск user_id в таблице users"""
        query = 'SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?)'
        try:
            row = self.database.cursor.execute(query, (user_id,)).fetchone()
        except sqlite3.Error:
            logger.exception('Не удалось проверить существование user_id=%s', user_id)
            raise

        if row is None:
            return False

        return bool(row[0])

    def update_last_success(self, user_id: int) -> None:
        """Обновление значения last_success для пользователя в таблице users"""
        query = 'UPDATE users SET last_success = ? WHERE user_id = ?'
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            cursor = self.database.cursor.execute(query, (now, user_id))
            self.database.conn.commit()
        except sqlite3.Error:
            logger.exception('Не удалось обновить last_success user_id=%s', user_id)
            self.database.conn.rollback()
            raise

        if cursor.rowcount == 0:
            logger.warning('last_success не обновлен user_id=%s', user_id)

    def get_last_success(self, user_id: int) -> str | None:
        """Возвращет last_success из таблицы users. Если пользователь не найден, то возвращает None"""
        query = 'SELECT last_success FROM users WHERE user_id = ?'
        try:
            row = self.database.cursor.execute(query, (user_id,)).fetchone()
        except sqlite3.Error:
            logger.exception('Не удалось получить last_success user_id=%s', user_id)
            raise

        if row is None:
            logger.warning('Пользователь user_id=%s не найден', user_id)
            return None

        return row[0]

    def change_attachments_status(self, user_id: int, status: int) -> bool:
        """Обновление значения attachments_enabled для пользователя из таблицы users"""
        query = 'UPDATE users SET attachments_enabled = ? WHERE user_id = ?'
        try:
            cursor = self.database.cursor.execute(query, (status, user_id))
            self.database.conn.commit()
        except sqlite3.Error:
            logger.exception('Не удалось изменить attachments_enabled user_id=%s', user_id)
            self.database.conn.rollback()
            raise

        return cursor.rowcount > 0

    def check_attachments_status(self, user_id: int) -> bool | None:
        query = 'SELECT attachments_enabled FROM users WHERE user_id = ?'
        try:
            row = self.database.cursor.execute(query, (user_id,)).fetchone()
        except sqlite3.Error:
            logger.exception('Не удалось узнать статус attachments_enabled user_id=%s', user_id)
            raise

        if row is None:
            logger.warning('Пользователь не найден user_id=%s', user_id)
            return None

        return bool(row[0])