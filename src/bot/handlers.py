from datetime import datetime
from src.storage.db import Database
from src.utils.get_user_server import get_user_server
from src.utils.get_user_port import get_user_port
from src.utils.is_user_registered import is_registered
from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

database = Database()
EMAIL, PASSWORD = range(2)


async def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    print(user_id)
    if is_registered(user_id):
        await update.message.reply_text("Вы уже зарегестрированы")
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Надо пройти регистрацию. Напишите ваш почтовый адрес"
        )
        return EMAIL


async def get_email(update: Update, context: CallbackContext) -> int:
    context.user_data[EMAIL] = update.message.text
    await update.message.reply_text(
        "Отлично. Введите пароль приложения для вашей почты"
    )
    return PASSWORD


async def get_password(update: Update, context: CallbackContext) -> int:
    context.user_data[PASSWORD] = update.message.text
    await update.message.reply_text(
        f"Регистрация завершена \n Почтовый адрес: {context.user_data[EMAIL]} \n Пароль приложения: {context.user_data[PASSWORD]}"
    )
    imap_server = get_user_server(context.user_data[EMAIL])
    imap_port = get_user_port(context.user_data[EMAIL])
    database.add_user(
        update.message.from_user.id,
        context.user_data[EMAIL],
        context.user_data[PASSWORD],
        imap_server,
        imap_port,
        "0",
        0,
        datetime.now(),
    )
    print("Данные добавлены в БД")
    return ConversationHandler.END


async def help(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Этот бот создан для автоматической пересылки сообщений с почтового клиента в клиент ТГ"
    )


async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Регистрация отменена")
    context.user_data.clear()
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
        PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
