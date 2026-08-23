
async def send_message_to_client(bot, chat_id, mail):
    message = f'Тема: {mail['subject']}\n Отправитель: {mail['from_']}\n Текст письма: {mail['text']}'
    await bot.send_message(chat_id, message)