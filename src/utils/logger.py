import logging


def setup_logger(name):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("src/logs/bot.log"), logging.StreamHandler()],
    )
