import os
import threading
from src.mail.imap import MailClient
from src.bot.notifier import send_message_to_client
from telegram.ext import Application, CommandHandler, Updater
from src.bot.handlers import help, conv_handler
from dotenv import load_dotenv
from src.storage.db import Database

load_dotenv(dotenv_path=r'C:\Users\arefb\PycharmProjects\Telegram-Mail-Bridge\config.env')

def main():

    TOKEN = os.getenv("BOT_TOKEN")
    print(TOKEN)

    if not os.path.isfile(r'src\storage\mail.db'):
        db = Database()
        db.create_database()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", help))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
