import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('mail.db')
        self.cursor = self.conn.cursor()

    def add_user(self, email, password):
        
        self.cursor.execute('''''')