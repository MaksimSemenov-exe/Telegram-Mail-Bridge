import os
import asyncio
from telegram.ext import Application, CommandHandler, Updater
from src.bot.handlers import help, conv_handler, start
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


    # def start_idle(user_data):
    #     client = MailClient(
    #         server=user_data['server'],
    #         username=user_data['username'],
    #         password=user_data['password'],
    #     )
    #     client.connect()
    #     chat_id = user_data['user_id']
    #
    #     def handle_new_message(msg):
    #         text = f'От: {msg['from_']}\n Тема: {msg["subject"]}\n Текст: {msg['text']}'
    #         asyncio.run(app.bot.send_message(chat_id, text))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
