import asyncio


class TelegramSender:
    def __init__(self, app, loop):
        self.app = app
        self.loop = loop

    def send_text(self, chat_id: int, text: str):
        """Отправляет сообщение и возвращает объект asyncio.Future"""
        return asyncio.run_coroutine_threadsafe(
            self.app.bot.send_message(chat_id, text), self.loop
        )

    def send_file(self, chat_id: int, file_path: str):
        """Отправляет файл и возвращает объект asyncio.Future"""
        return asyncio.run_coroutine_threadsafe(
            self.app.bot.send_document(chat_id, document=file_path), self.loop
        )

