import json
import logging
import os


logger = logging.getLogger(__name__)


def get_user_port(email: str) -> str:
    """Получение SSL порта пользователя по его почтовому адресу"""

    domain = email.split("@")[1]

    base_dir = os.path.dirname(__file__)
    json_path = os.path.join(base_dir, '..', 'configs', 'imap_config.json')

    with open(json_path, 'r') as f:
        data = json.load(f)

    email_config = data.get(domain)
    if email_config is None:
        logger.warning('Не найдены записи о домене domain=%s', domain)
        raise ValueError(f'Нет конфига для домена {domain}')

    port = email_config.get('ssl_port')
    if not port:
        logger.warning("В конфиге нет port для domain=%s", domain)
        raise ValueError(f"Нет port для домена {domain}")

    return port


