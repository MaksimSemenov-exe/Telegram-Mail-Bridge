import asyncio
import threading
import logging
import os
from src.mail.imap import MailClient
from src.storage.db import Database
from src.utils.custom_exceptions import UserNotFound
from src.utils.mask_email import mask_email

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
        try:
            db = Database()
            user_id = db.get_user_id_by_email(username)
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
            db_local = Database()
            logger.info(
                "Новое письмо uid=%s, from=%s, user=%s (user_id=%s)",
                msg["uid"],
                msg["from"],
                username,
                user_id,
            )
            logger.debug("Отправка письма в Telegram user_id=%s", user_id)
            if len(msg["attachments"]) > 0:
                logger.info("Получено письмо с %d вложениями", len(msg["attachments"]))
                text = f'От: {msg['from']}\nТема: {msg["subject"]}\nТекст: {msg['text']}\nВложения будут отправлены ниже'
                asyncio.run_coroutine_threadsafe(
                    self.app.bot.send_message(chat_id, text), loop=self.loop
                )

                for att in msg["attachments"]:
                    logger.debug(
                        "Обрабатываю вложение filename=%s, user_id=%s",
                        att["filename"],
                        user_id,
                    )
                    try:
                        with open(f'temp/{msg['uid']}_{att['filename']}', "wb") as f:
                            f.write(att["payload"])
                        logger.debug("Вложение filename=%s сохранено", att["filename"])
                    except Exception:
                        logger.exception(
                            "Ошибка записи вложения filename=%s, user_id=%s",
                            att["filename"],
                            user_id,
                        )
                        continue
                    if os.path.getsize(f'temp/{msg["uid"]}_{att["filename"]}') <= 49.5:
                        asyncio.run_coroutine_threadsafe(
                            self.app.bot.send_document(chat_id, document=f'temp/{msg['uid']}_{att['filename']}'), self.loop
                        )
                        logger.debug("Вложение filename=%s отправлено", att["filename"])
                    else:
                        asyncio.run_coroutine_threadsafe(
                            self.app.bot.send_message(chat_id, 'Не удалось отправить вложение. Его вес превыешает 50 МБ'), loop=self.loop
                        )
                        logger.info('Не удалось отправить filename=%s, вес превышет 50 МБ', att["filename"])
                    try:
                        os.remove(f'src/temp/{msg["uid"]}_{att.filename}')
                    except Exception:
                        logger.info("Ошибка при удалении filename=%s", att["filename"])

            else:
                text = f'От: {msg['from']}\nТема: {msg["subject"]}\nТекст: {msg['text']}'
                asyncio.run_coroutine_threadsafe(
                    self.app.bot.send_message(chat_id, text), self.loop
                )
            try:
                db_local.update_uid(msg["uid"], username)
                logger.debug("Uid пользователя %s обновлен на %s", user_id, msg["uid"])
            except Exception:
                logger.exception(
                    "Не удалось обновить UID %s для user=%s", msg["uid"], user_id
                )

        try:
            client = MailClient(server, username, password)
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
        users = self.db.get_all_users()
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
            user_id = self.db.get_user_id_by_email(username)
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
            client = MailClient(server, username, password)
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

        db_local = Database()
        processed = 0

        for msg in messages:
            text = f'От: {msg['from']}\nТема: {msg['subject']}\nТекст: {msg['text']}'
            try:
                asyncio.run_coroutine_threadsafe(
                    self.app.bot.send_message(chat_id, text), self.loop
                )
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
                db_local.update_uid(msg["uid"], username)
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
