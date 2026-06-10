from telegram import Update
from src.utils.is_user_registered import is_registered
from telegram.ext import ContextTypes, CallbackContext, ConversationHandler

EMAIL, PASSWORD = range(2)

async def start(update: Update, context: CallbackContext.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    print(user_id)
    if is_registered(user_id):
        await update.message.reply_text("Вы уже зарегестрированы")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Надо пройти регистрацию. Напишите ваш почтовый адрес")
        return EMAIL

async def get_email(update: Update, context: CallbackContext) -> int:
    context.user_data[EMAIL] = update.message.text
    await update.message.reply_text('Отлично. Введите пароль приложения для вашей почты')
    return PASSWORD

async def get_password(update: Update, context: CallbackContext) -> int:
    context.user_data[PASSWORD] = update.message.text
    await update.message.reply_text(f'Регистрация завершена \n Почтовый адрес: {context.user_data[EMAIL]} \n Пароль приложения: {context.user_data[PASSWORD]}')
    return ConversationHandler.END

async def help(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await update.message.reply_text("Этот бот создан для автоматической пересылки сообщений с почтового клиента в клиент ТГ")

