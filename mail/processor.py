from mail import get_mails
from .imap_client import user_password, user_email, searching_date
from .utils import get_imap_server


server = get_imap_server(user_email)

def process_mails(serv):

    for i in get_mails(searching_date, user_email, user_password, serv):
