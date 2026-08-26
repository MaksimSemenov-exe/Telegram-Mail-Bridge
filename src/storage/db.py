import sqlite3
import os


class Database:
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
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
        query = "INSERT INTO users (user_id, email, password, imap_server, imap_port, smtp_server, smtp_port, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        self.cursor.execute(
            query,
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
        self.conn.commit()

    def get_all_users(self):
        """Получение всез записей из таблицы users в БД"""
        query = "SELECT * FROM users"
        data = self.cursor.execute(query).fetchall()
        return data