import sqlite3


def is_registered(user_id: int) -> bool:
    """Проверка, зарегестрирован ли пользователь"""
    conn = None
    try:
        conn = sqlite3.connect(
            r"C:\Users\arefb\PycharmProjects\Telegram-Mail-Bridge\src\storage\mail.db"
        )
        cursor = conn.cursor()
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?)"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()[0]
        return bool(result)

    except Exception as e:
        print(e)
        return False

    finally:
        if conn is not None:
            conn.close()
            conn = None
