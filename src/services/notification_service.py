from src.integrations.telegram_sender import TelegramSender
from src.services.attachment_service import AttachmentService
from src.storage.db import Database
from src.services.message_formatter import format_message
import logging


logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, sender: TelegramSender, attachment_service: AttachmentService, database: Database):
        self.sender = sender
        self.attachment_service = attachment_service
        self.database = database

    def process_message(self, msg: dict, chat_id: int, user_id: int, username: str) -> None:
        logger.info('Новое письмо: uid: %s user_id: %s', msg['uid'], user_id)

        if len(msg['attachments']) > 0:
            logger.debug("Получено письмо с %d вложениями", len(msg['attachments']))
            text = format_message(msg, with_attachments=True)
            logger.info("Длина текста письма uid=%s: %d символов", msg["uid"], len(text))
            self.sender.send_text(chat_id, text).result(10)

            if self.database.check_attachments_status(user_id):
                for att in msg['attachments']:
                    result = self.attachment_service.save(att, msg['uid'])
                    if result.get('error') == 'too_large':
                        filename = result.get('filename')
                        size_mb = result.get('size') / (1024 * 1024)
                        self.sender.send_text(chat_id,
                        f'Вложение {filename} ({size_mb:.1f} МБ) превышает лимит 50 МБ. Оно не будет отправлено')
                        continue
                    if not result.get('path'):
                        continue
                    path = result.get('path')
                    future = self.sender.send_file(chat_id, path)
                    try:
                        future.result(30)
                        logger.debug('Вложение %s отправлено', result.get('filename'))
                    except TimeoutError:
                        logger.warning(
                            "Таймаут ответа Telegram для %s (файл, вероятно, доставлен)",
                            result.get("filename")
                        )
                    except Exception:
                        logger.exception('Не удалось отправить вложение %s user_id=%s', result.get('filename'), user_id)
                    finally:
                        self.attachment_service.remove(path)
        else:
            text = format_message(msg)
            logger.info("Длина текста письма uid=%s: %d символов", msg["uid"], len(text))
            self.sender.send_text(chat_id, text).result(10)
        try:
            self.database.update_uid(msg['uid'], username)
            logger.debug('UID пользователя %s обновлен на %s', user_id, msg['uid'])
        except Exception:
            logger.exception(
                'Не удалось обновить UID %s для user=%s', msg['uid'], user_id
            )