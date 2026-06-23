import imaplib


class MailClient:
    def __init__(self, server: str, username: str, password: str):
        self.server = server
        self.username = username
        self.password = password
        self.client = None

    def connect(self):
        try:
            self.client = imaplib.IMAP4_SSL(self.server)
            self.client.login(self.username, self.password)
        except Exception:
            return 'Ошибка подключения'

    def fetch(self):


    def disconnect(self):
        self.client.disconnect()
        self.client.logout()