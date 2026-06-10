from telegram import Update
from src.utils.is_user_registered import is_registered
from telegram.ext import ContextTypes, CallbackContext


async def start(update: Update, context: CallbackContext.DEFALT_TYPE):
    user_id = update.message.from_user.id
    print(user_id)
    if is_registered(user_id):
        await update.message.reply_text("Вы уже зарегестрированы")
    else:
        await update.message.reply_text("Надо пройти регистрацию")

async def help(update: Update, context: CallbackContext.DEFALT_TYPE):
    await update.message.reply_text("Этот бот создан для автоматической пересылки сообщений с почтового клиента в клиент ТГ")

