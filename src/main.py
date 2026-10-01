import os
import asyncio
from telegram.ext import Application, CommandHandler, Updater
from src.bot.handlers import help, registration_handler, delete_handler, settings, stop_idle, manual_check, cancel, start_idle
from src.storage.db import Database
from dotenv import load_dotenv
from src.mail.MailManager import MailManager
from src.storage.repositories.mail_repository import MailRepository
from src.storage.repositories.user_repository import UserRepository
from src.utils.logger import setup_logger
import logging


logger = logging.getLogger(__name__)


current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, "..", "config.env")
load_dotenv(dotenv_path=dotenv_path)


def main():

    """Получение токена, запуск бота"""
    setup_logger()

    TOKEN = os.getenv("BOT_TOKEN")

    if not TOKEN:
        logger.critical('BOT-токен не задан')
        raise SystemExit(1)

    db = Database()
    user_repository = UserRepository(db)
    mail_repository = MailRepository(db)

    try:
        db.create_database()
    except Exception:
        logger.critical('Не удалось создать БД, работа программы невозможна')
        raise
    loop = asyncio.get_event_loop()

    app = Application.builder().token(TOKEN).read_timeout(30).write_timeout(30).connect_timeout(10).build()

    app.add_handler(registration_handler)
    app.add_handler(delete_handler)
    app.add_handler(CommandHandler('help', help))
    app.add_handler(CommandHandler('settings', settings))
    app.add_handler(CommandHandler('stop_idle', stop_idle))
    app.add_handler(CommandHandler('check', manual_check))
    app.add_handler(CommandHandler('cancel', cancel))
    app.add_handler(CommandHandler('start_idle', start_idle))

    mail_manager = MailManager(app, loop, user_repository, mail_repository)

    app.bot_data['mail_manager'] = mail_manager
    app.bot_data['user_repository'] = user_repository
    mail_manager.start_idle_for_all_users()

    logger.debug('Бот запущен')
    app.run_polling()


if __name__ == "__main__":
    main()
