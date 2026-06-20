import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('mail.db')
        self.cursor = self.conn.cursor()

    def add_user(self, user_id, email, password, imap_server, imap_port, smtp_server, smtp_port, registered, created):
        query = 'INSERT users (user_id, email, password, imap_server, imap_port, smtp_server, smtp_port, created_at) VALUES (? ? ? ? ? ? ? ?)'
        self.cursor.execute(query, (user_id, email, password, imap_server, imap_port, smtp_server, smtp_port, registered, created))

