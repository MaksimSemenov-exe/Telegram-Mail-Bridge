from imap_tools import MailBox, AND
from mail import get_imap_server
from handlers.register_handler import user_sessions
import datetime


searching_date = datetime.date.today() - datetime.timedelta(days=1)
user_email = user_sessions.get('email')
user_password = user_sessions.get('password')
server = get_imap_server(user_email)

def get_mails(date: datetime.date, email: str, password: str, serv: str):
    with MailBox(serv).login(email, password) as mailbox:
        return list(mailbox.fetch(AND(seen=False, sent_date_gte=date)))



