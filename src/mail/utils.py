from handlers.register_handler import user_sessions


user_domain = user_sessions.get('email').split('@')[-1].lower()

def get_imap_server(domain: str) -> str:

    imap_dict = {
        "gmail.com": "imap.gmail.com",
        "yandex.ru": "imap.yandex.ru",
        "mail.ru": "imap.mail.ru"
    }

    return imap_dict.get(domain)

