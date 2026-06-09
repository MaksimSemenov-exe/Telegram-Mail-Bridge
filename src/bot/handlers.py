

async def start(update, context):
    await update.message.reply_text("Бот работает асинхронно!")

async def help(update, context):
    await update.message.reply_text("Этот бот создан для автоматической пересылки сообщений с почтового клиента в клиент ТГ")

