import telebot

def register_start(bot):
    @bot.message_handler(commands=['start'])
    def start(message):
        bot.reply_to(message.chat.id, 'Привет. Я бот-мост между твоей почтой и телеграмом! Нажми login чтобы войти')

