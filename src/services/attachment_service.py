import os
import logging


logger = logging.getLogger(__name__)


class AttachmentService:
    MAX_SIZE = int(49.5 * 1024 * 1024)

    def __init__(self, temp_dir: str):
        self.temp_dir = temp_dir

    def save(self, att: dict, uid: str) -> dict:
        filename = att.get('filename')
        if not filename:
            logger.warning('Вложение без filename')
            return {'error': 'no_filename'}
        safe_name = os.path.basename(filename)
        path = os.path.join(self.temp_dir, f'{uid}_{safe_name}')

        payload = att.get('payload')

        if not payload:
            logger.warning('Вложение без payload')
            return {'error': 'no_payload', 'filename': safe_name}

        size = len(payload)
        if size > self.MAX_SIZE:
            logger.info('Вложение %s (%d байт) превышает лимит', safe_name,size)
            return {'error': 'too_large', 'filename': safe_name, 'size': size}
        try:
            with open(path, 'wb') as f:
                f.write(payload)
            logger.debug('Вложение сохранено: %s', path)
            return {"path": path, "filename": safe_name, "size": size}
        except Exception:
            logger.exception('Ошибка записи вложения: %s', path)
            return {'error': 'write_failed', 'filename': safe_name, 'size': size}

    def remove(self, path: str) -> bool:
        try:
            os.remove(path)
            logger.debug('Файл %s удален', path)
            return True
        except FileNotFoundError:
            logger.debug('Файл уже удален: %s', path)
            return True
        except Exception:
            logger.exception('Не удалось удалить файл %s', path)
            return False

