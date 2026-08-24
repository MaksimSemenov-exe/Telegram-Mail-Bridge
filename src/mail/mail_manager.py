import asyncio
import threading
from src.mail.imap import MailClient


def start_idle(user_data):
    client = MailClient(
        server=user_data['server'],
        username=user_data['username'],
        password=user_data['password'],
    )
    client.connect()
    chat_id = user_data['user_id']

    def handle_new_message(msg):
        text = f'От: {msg['from_']}\n Тема: {msg["subject"]}\n Текст: {msg['text']}'
        asyncio.run_coroutine_threadsafe()
