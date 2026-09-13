import asyncio
import threading
import logging
from src.mail.imap import MailClient
from src.storage.db import Database


logger = logging.getLogger(__name__)


class MailManager:
    def __init__(self, app, loop):
        self.app = app
        self.loop = loop
        self.threads = []
        self.db = Database()

    def start_idle_for_user(
        self, server: str, username: str, password: str, chat_id: int
    ) -> None:
        user_id = self.db.get_user_id_by_email(username)
        logger.info("Запуск IDLE-режима для пользователя user_id=%s", user_id)
        client = MailClient(server, username, password)
        client.connect()

        def handle_new_message(msg):
            db_local = Database()
            logger.info(
                "Новое письмо uid=%s, from=%s, user=%s (user_id=%s)",
                msg["uid"],
                msg["from"],
                username,
                user_id,
            )
            logger.debug("Отправка письма в Telegram user_id=%s", user_id)
            text = f'От: {msg['from']}\nТема: {msg["subject"]}\nТекст: {msg['text']}'
            asyncio.run_coroutine_threadsafe(
                self.app.bot.send_message(chat_id, text), self.loop
            )
            db_local.update_uid(msg["uid"], client.username)
            logger.debug("Uid пользователя %s обновлен на %s", user_id, msg["uid"])

        client.idle(handle_new_message)
        logger.info("IDLE завершен для user_id=%s", user_id)

    def start_idle_for_all_users(self) -> None:

        users = self.db.get_all_users()
        logger.info("Запуск IDLE-режима для %s пользователей", len(users))

        if len(users) == 0:
            logger.warning("Пустая БД")
        else:
            for user in users:
                thread = threading.Thread(
                    target=self.start_idle_for_user,
                    args=(user[3], user[1], user[2], user[0]),
                    daemon=True,
                )
                thread.start()
                self.threads.append(thread)
                logger.debug(
                    "Поток запущен user_id=%s, thread=%s", user[1], thread.native_id
                )
            logger.info("Запущено %s потоков")

    def start_thread_for_user(
        self, server: str, username: str, password: str, chat_id: int
    ) -> None:
        user_id = self.db.get_user_id_by_email(username)
        logger.info("Ручной запуск IDLE для user_id=%s", user_id)
        thread = threading.Thread(
            target=self.start_idle_for_user,
            args=(server, username, password, chat_id),
            daemon=True,
        )
        thread.start()
        self.threads.append(thread)
        logger.info("Запущен поток %s для пользователя %s", thread.native_id, user_id)

    def manual_check(
        self, server: str, username: str, password: str, chat_id: int
    ) -> None:
        user_id = self.db.get_user_id_by_email(username)
        logger.info("Ручная проверка почты для user_id=%s, сервер %s", user_id, server)
        client = MailClient(server, username, password)
        db_local = Database()
        client.connect()
        messages = client.fetch_unseen()
        logger.info("Найдено писем %d (user_id=%s)", len(messages), user_id)
        for msg in messages:
            text = f'От: {msg['from']}\nТема: {msg['subject']}\nТекст: {msg['text']}'
            asyncio.run_coroutine_threadsafe(
                self.app.bot.send_message(chat_id, text), self.loop
            )
            logger.debug("Отправка письма %s user_id=%s", msg["uid"], user_id)
            db_local.update_uid(msg["uid"], client.username)
            logger.debug("UID %s обработан и занесене в БД", msg["uid"])
        logger.info(
            "Ручная проверка для user_id=%s завершена, обработано %s писем",
            user_id,
            len(messages),
        )
