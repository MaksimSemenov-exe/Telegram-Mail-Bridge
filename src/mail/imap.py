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

    def idle(self):
        client = imaplib.IMAP4_SSL(self.server)
        client.login(self.username, self.password)
        client.select('INBOX')

        try:
            while True:
                responces = client.idle_check(timeout=1)
                for i in responces:
                    pass
    def disconnect(self):
        self.client.disconnect()
        self.client.logout()