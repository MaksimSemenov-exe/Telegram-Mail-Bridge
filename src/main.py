import os
import asyncio
import threading
from telegram.ext import Application, CommandHandler, Updater
from src.bot.handlers import help, conv_handler
from dotenv import load_dotenv
from src.storage.db import Database
from src.mail.imap import MailClient

current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, "..", "config.env")
load_dotenv(dotenv_path=dotenv_path)


def main():
    """Получение токена, запуск бота"""
    TOKEN = os.getenv("BOT_TOKEN")
    print(TOKEN)

    db = Database()
    db.create_database()

    loop = asyncio.get_event_loop()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", help))

    def start_idle(user_data, loop):
        client = MailClient(
            server=user_data[3],
            username=user_data[1],
            password=user_data[2],
        )
        client.connect()
        print("CONNECTED")
        chat_id = user_data[0]

        def handle_new_message(msg):
            db_local = Database()
            text = f'От: {msg['from']}\nТема: {msg["subject"]}\nТекст: {msg['text']}'
            print(f"Отправка письма")
            asyncio.run_coroutine_threadsafe(app.bot.send_message(chat_id, text), loop)
            db_local.update_uid(msg['uid'], client.username)

        client.idle(handle_new_message)

    users = db.get_all_users()
    print(users)
    for user in users:
        threading.Thread(target=start_idle, args=(user, loop), daemon=True
            ).start()

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
