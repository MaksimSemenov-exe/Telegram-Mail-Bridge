import os
import asyncio
from telegram.ext import Application, CommandHandler, Updater
from src.bot.handlers import help, conv_handler
from src.storage.db import Database
from dotenv import load_dotenv
from src.mail.MailManager import MailManager
from src.utils.logger import setup_logger
import logging


logger = logging.getLogger(__name__)


current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, "..", "config.env")
load_dotenv(dotenv_path=dotenv_path)


def main():

    """Получение токена, запуск бота"""

    TOKEN = os.getenv("BOT_TOKEN")

    if not TOKEN:
        logger.critical('BOT-токен не задан')
        raise SystemExit(1)

    db = Database()

    setup_logger()

    try:
        db.create_database()
    except Exception:
        logger.critical('Не удалось создать БД, работа программы невозможна')
        raise
    loop = asyncio.get_event_loop()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", help))

    mail_manager = MailManager(app, loop)

    app.bot_data['mail_manager'] = mail_manager

    mail_manager.start_idle_for_all_users()

    print('Бот запущен')
    app.run_polling()


if __name__ == "__main__":
    main()
