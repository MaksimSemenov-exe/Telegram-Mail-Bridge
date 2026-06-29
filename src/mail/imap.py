from imap_tools import MailBox, A


class MailClient:
    def __init__(self, server: str, username: str, password: str):
        self.server = server
        self.username = username
        self.password = password
        self.mailbox = None

    def connect(self) -> MailBox:
        try:
            self.mailbox = MailBox(self.server).login(self.username, self.password)
        except Exception:
            return 'Ошибка подключения'

    def idle(self):
        with self.mailbox:
            responses = self.mailbox.idle.wait()
            if responses:
                for msg in self.mailbox.fetch(A(seen=False)):
                    pass

    def disconnect(self):
        self.mailbox.disconnect()
        self.mailbox.logout()