from imap_tools import MailBox, A
import time


class MailClient:
    def __init__(self, server: str, username: str, password: str):
        self.server = server
        self.username = username
        self.password = password
        self.mailbox = None
        self.responses = None
    def connect(self) -> bool:

        """Подключение к почтовому серверу"""

        try:
            self.mailbox = MailBox(self.server).login(self.username, self.password)
            print('Подключено')
            return True

        except Exception:
            print("Ошибка подключения")
            return False

    def fetch_unseen(self) -> list[dict[str, str]]:

        messages = []
        for msg in self.mailbox.fetch(A(seen=False)):
            messages.append(
                {
                    "uid": msg.uid,
                    "date": msg.date,
                    "subject": msg.subject,
                    "from": msg.from_,
                    "text": msg.text,
                }
            )
        return messages

    def idle(self):

        while True:
            if not self.mailbox:
                if not self.connect():
                    time.sleep(5)
                    continue
            responses = self.mailbox.idle.wait(timeout=60)
            print(responses)

            if responses:
                messages = self.fetch_unseen()
                for msg in messages:
                    print(msg['subject'])

    def disconnect(self):
        self.mailbox.disconnect()
        self.mailbox.logout()

client = MailClient("imap.yandex.ru", "", "")
client.connect()
client.idle()