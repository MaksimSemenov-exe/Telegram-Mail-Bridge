import sqlite3

conn = sqlite3.connect(r"C:\Users\arefb\PycharmProjects\Telegram-Mail-Bridge\src\storage\mail.db")

cursor = conn.cursor()
info = cursor.execute('''SELECT * FROM users''').fetchall()
print(info)