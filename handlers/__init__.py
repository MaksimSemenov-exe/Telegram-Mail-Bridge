from .start_handler import register_start
from .register_handler import register_login

def register_handlers(bot):
    register_start(bot)
    register_login(bot)