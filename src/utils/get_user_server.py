from src.utils.imap_servers import imap_data

def get_user_server(email: str) -> str:

    server = imap_data[email.split('@')[1]].get('ssl_port')
    return server

srv = get_user_server('arefbrq@gmail.com')
print(srv)