from src.utils.imap_servers import imap_data


def get_user_port(email: str) -> str:

    """Получение SSL порта пользователя по его почтовому адресу"""
    server = imap_data[email.split("@")[1]].get("ssl_port")
    return server


srv = get_user_port("arefbrq@gmail.com")
print(srv)
