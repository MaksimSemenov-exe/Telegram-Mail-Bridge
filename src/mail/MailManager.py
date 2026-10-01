import threading
import logging
import os

from src.storage.repositories.mail_repository import MailRepository
from src.storage.repositories.user_repository import UserRepository
from src.mail.imap import MailClient
from src.services.notification_service import NotificationService
from src.services.message_formatter import format_message
from src.services.attachment_service import AttachmentService
from src.integrations.telegram_sender import TelegramSender
from src.utils.custom_exceptions import UserNotFound
from src.utils.mask_email import mask_email


logger = logging.getLogger(__name__)


class MailManager:
    def __init__(self, app, loop, user_repository: UserRepository, mail_repository: MailRepository):
        base_dir = os.path.dirname(__file__)
        temp_dir = os.path.join(base_dir, "..", "temp")
        self.app = app
        self.loop = loop
        self.threads = []
        self.user_repository = user_repository
        self.mail_repository = mail_repository
        self.sender = TelegramSender(self.app, self.loop)
        self.attachment_service = AttachmentService(temp_dir)
        self.notification_service = NotificationService(self.sender, self.attachment_service, self.user_repository, self.mail_repository)

    def start_idle_for_user(
        self, server: str, username: str, password: str, chat_id: int
    ) -> None:
        try:
            user_id = self.user_repository.get_user_id_by_email(username)
        except UserNotFound:
            logger.warning(
                "IDLE не запущен: Пользователь не найден user=%s", mask_email(username)
            )
            return
        except Exception:
            logger.exception("IDLE не запущен: Ошибка БД user=%s", mask_email(username))
            return

        logger.info("Запуск IDLE-режима для пользователя user_id=%s", user_id)

        def handle_new_message(msg: dict) -> None:
            self.notification_service.process_message(msg, chat_id, user_id, username)

        try:
            client = MailClient(server, username, password, user_id, self.user_repository)
            if not client.connect():
                logger.warning(
                    "Не удалось подключиться к IMAP user=%s", mask_email(username)
                )
                return
            client.idle(handle_new_message)
        except Exception:
            logger.exception("IDLE-поток упал user=%s", mask_email(username))
        finally:
            logger.info("IDLE завершен для user=%s", mask_email(username))

    def start_idle_for_all_users(self) -> None:
        """Запускает IDLE-поток для каждого пользователя"""
        users = self.user_repository.get_all_users()
        logger.info("Запуск IDLE-режима для %s пользователей", len(users))

        if len(users) == 0:
            logger.warning("Пустая БД")
            return

        threads_counter = 0
        for user in users:
            thread = threading.Thread(
                target=self.start_idle_for_user,
                args=(user[3], user[1], user[2], user[0]),
                daemon=True,
            )
            thread.start()
            self.threads.append(thread)
            logger.debug(
                "Поток запущен user_id=%s, thread=%s", user[0], thread.native_id
            )
            threads_counter += 1
        logger.info("Запущено %s потоков", threads_counter)

    def start_thread_for_user(
        self, server: str, username: str, password: str, chat_id: int
    ) -> None:

        logger.info("Ручной запуск IDLE для user=%s", mask_email(username))
        thread = threading.Thread(
            target=self.start_idle_for_user,
            args=(server, username, password, chat_id),
            daemon=True,
        )
        thread.start()
        self.threads.append(thread)
        logger.info(
            "Поток запущен: thread=%s user=%s", thread.native_id, mask_email(username)
        )

    def manual_check(
        self, server: str, username: str, password: str, chat_id: int
    ) -> None:
        try:
            user_id = self.user_repository.get_user_id_by_email(username)
        except UserNotFound:
            logger.warning(
                "Ручная проверка не запущена: Пользователь не найден user=%s",
                mask_email(username),
            )
            return
        except Exception:
            logger.exception(
                "Ручная проверка не запущена: ошибка БД user=%s", mask_email(username)
            )
            return
        try:
            client = MailClient(server, username, password, self.user_repository)
            if not client.connect():
                logger.warning(
                    "Ручная проверка: Не удалось подключиться к IMAP user=%s",
                    mask_email(username),
                )
                return
            messages = client.fetch_unseen()
        except Exception:
            logger.exception(
                "Ручная проверка: Ошибка получения писем user=%s", mask_email(username)
            )
            return

        logger.info("Найдено писем %d (user_id=%s)", len(messages), user_id)

        processed = 0

        for msg in messages:
            text = format_message(msg)
            try:
                future = self.sender.send_text(chat_id, text)
                logger.debug("Отправка письма %s user_id=%s", msg["uid"], user_id)
                processed += 1
            except Exception:
                logger.exception(
                    "Не удалось отправить письмо UID=%s user=%s",
                    msg["uid"],
                    mask_email(username),
                )
                continue
            try:
                self.mail_repository.update_uid(msg["uid"], username)
                logger.debug("UID %s обработан и занесене в БД", msg["uid"])
            except Exception:
                logger.exception(
                    "Не удалось обновить UID=%s user=%s",
                    msg["uid"],
                    mask_email(username),
                )
        logger.info(
            "Ручная проверка для user_id=%s завершена, обработано %s писем",
            user_id,
            processed,
        )

