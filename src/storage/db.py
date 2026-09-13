import sqlite3
import os
import datetime


class Database:
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        # self.db_path = os.path.join(os.path.dirname(__file__), 'storage', 'mail.db')
        self.db_path = os.path.join(self.current_dir, "mail.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

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

    def create_database(self):
        """Создание таблицы users в БД"""
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
                created_at TEXT
            )
        """
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS last_mail (email TEXT, uid INTEGER DEFAULT 0, last_update TEXT)"""
        )
        self.conn.commit()

    def check_last_uid(self, email):
        query = "SELECT uid FROM last_mail WHERE email = ?"
        self.cursor.execute(query, (email,))

    def update_uid(self, uid, email):
        query = "UPDATE last_mail SET uid = ?, last_update = ? WHERE email = ?"
        last_update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            query,
            (
                uid,
                last_update_time,
                email,
            ),
        )
        self.conn.commit()

    def get_all_users(self):
        """Получение всез записей из таблицы users в БД"""
        query = "SELECT * FROM users"
        data = self.cursor.execute(query).fetchall()
        return data

    def get_user_info(self, user_id):
        query = "SELECT * FROM users WHERE user_id = ?"
        settings = self.cursor.execute(query, (user_id,)).fetchone()
        return settings

    def is_active(self, email):
        query = "SELECT is_active FROM users WHERE email = ?"
        self.cursor.execute(query, (email,))

    def delete_user(self, user_id):
        query = "DELETE FROM users WHERE user_id = ?"
        self.cursor.execute(query, (user_id,))

    def stop_idle(self, user_id):
        query = "UPDATE users SET is_active = 0 WHERE user_id = ?"
        result = self.cursor.execute(query, (user_id,)).fetchall()
        return bool(result[0][0]) if result else False

    def get_user_id_by_email(self, email):
        query = "SELECT user_id FROM users WHERE email = ?"
        result = self.cursor.execute(query, (email,)).fetchall()[0][0]
        return result
