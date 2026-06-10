import asyncio
import os

from telegram.ext import Application, CommandHandler
from src.bot.handlers import start, help
from dotenv import load_dotenv

load_dotenv()

def main():

    app = Application.builder().token(os.getenv('BOT_TOKEN')).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
