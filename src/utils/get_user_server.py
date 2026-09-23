import json
import logging
import os

logger = logging.getLogger(__name__)


def get_user_server(email: str) -> str:
    """Получение IMAP сервера пользователя по его почтовому адресу"""

    domain = email.split('@')[1]

    base_dir = os.path.dirname(__file__)
    json_path = os.path.join(base_dir, '..', 'configs', 'imap_config.json')
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.exception('Config-файл не найден path=%s', json_path)
        raise

    email_config = data.get(domain)
    if email_config is None:
        logger.warning('Не найдены записи о данном почтовом сервисе domain=%s', domain)
        raise

    return email_config.get('server')


