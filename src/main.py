import asyncio
from telegram.ext import Application, CommandHandler
from src.bot.handlers import start, help

def main():

    app = Application.builder().token("8253434945:AAHDx83n9yQ7HUGSMTmnWbYbYbmA9g7HXmc").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
