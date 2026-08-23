from src.mail.imap import MailClient


def start_idle(user_data):
    client = MailClient(
        server=user_data['server'],
        username=user_data['username'],

    )