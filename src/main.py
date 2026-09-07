import os
import asyncio
from telegram.ext import Application, CommandHandler, Updater
from src.bot.handlers import help, conv_handler
from dotenv import load_dotenv
from src.mail.MailManager import MailManager
from src.storage.db import Database

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

    mail_manager = MailManager(app, loop)

    app.bot_data['mail_manager'] = mail_manager

    mail_manager.start_idle_for_all_users()

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
