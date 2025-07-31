import telebot

user_sessions = {}

def register_login(bot):
    @bot.message_handler(commands=['login'])
    def register(message):
        bot.reply_to(message.chat.id, 'Напиши имя своей почты')
        bot.register_next_step_hadler(message, get_email)

    def get_email(message):
        user_sessions[message] = {'email': message.text}
        bot.reply_to(message.chat.id, 'Теперь отправь пароль!')
        bot.register_next_step_hadler(message, get_password)

    def get_password(message):
        user_sessions[message.chat.id] = {'password': message.text}
        bot.send_message(message.chat.id, 'Попытка подключения')


