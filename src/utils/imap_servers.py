"""Словари IMAP серверов"""
imap_data = {
    'gmail.com': {
        'server': 'imap.gmail.com',
        'is_ssl_needed': True,
        'ssl_port': 993,
        'tls_port': 993,
        'is_authentication_needed': True
    },
    'yandex.ru': {
        'server': 'imap.yandex.ru',
        'rus_server': 'imap.yandex.ru',
        'foriegn_server': 'imap.ya.ru',
        'is_ssl_needed': True,              #Убрать rus server
        'ssl_port': 993,
    },
    'mail.ru': {
        'server': 'imap.mail.ru',
        'is_ssl_needed': True,
        'ssl_port': 993,
        'tls_port': 993,
        'is_authentication_needed': True
    },
    'outlook.com': {
        'server': 'outlook.office365.com',
        'is_ssl_needed': True,
        'ssl_port': 993,
        'tls_port': 993,
        'is_authentication_needed': True
    },
    'vk.com': {
        'server': 'imap.mail.ru',
        'is_ssl_needed': True,
        'ssl_port': 993,
        'tls_port': 993,
        'is_authentication_needed': True,
        'STARTTLS': 143
    }
}