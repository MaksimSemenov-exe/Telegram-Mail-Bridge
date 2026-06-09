
import asyncio
from telegram.ext import Application, CommandHandler


async def start(update, context):
    await update.message.reply_text("Бот работает асинхронно!")



def main():

    app = Application.builder().token("8253434945:AAHDx83n9yQ7HUGSMTmnWbYbYbmA9g7HXmc").build()
    app.add_handler(CommandHandler("start", start))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
