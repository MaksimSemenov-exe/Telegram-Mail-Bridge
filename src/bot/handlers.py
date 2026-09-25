import logging
from datetime import datetime
from src.storage.db import Database
from src.utils.get_user_server import get_user_server
from src.utils.get_user_port import get_user_port
from src.utils.mask_email import mask_email
from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

database = Database()
EMAIL, PASSWORD = range(2)
CONFIRMATION = range(1)

logger = logging.getLogger(__name__)


async def start(update: Update, context: CallbackContext) -> int:
    """Хендлер-обработчик команды /start, запускает регистрацию если пользователя нет в БД"""
    user_id = update.message.from_user.id
    logger.info("Команда /start от user_id=%s", user_id)

    db = Database()

    if db.is_registered(user_id):
        await update.message.reply_text("Вы уже зарегистрированы")
        logger.info("user_id=%s уже зарегистрирован", user_id)
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Надо пройти регистрацию. Напишите ваш почтовый адрес"
        )
        logger.info("Регистрация user_id=%s", user_id)
        return EMAIL


async def get_email(update: Update, context: CallbackContext) -> int:
    """Хендлер обработки адреса эл.почты, отправленной пользователем проходящим регистрацию"""
    context.user_data[EMAIL] = update.message.text
    logger.info(
        "Регистрация: получен email %s (user_id=%s)",
        mask_email(context.user_data[EMAIL]),
        update.message.from_user.id,
    )
    await update.message.reply_text(
        "Отлично. Введите пароль приложения для вашей почты"
    )
    return PASSWORD


async def get_password(update: Update, context: CallbackContext) -> int:
    """Хендлер обработки пароля сторонних приложений эл.почты, отправленного пользователем проходящим регистрацию
    Сохранение данных о пользователе в таблицу users в БД"""
    user_id = update.message.from_user.id
    context.user_data[PASSWORD] = update.message.text
    logger.info("Регистрация: получен пароль (user_id=%s)", user_id)
    await update.message.reply_text(
        f"Регистрация завершена \n Почтовый адрес: {context.user_data[EMAIL]} \n Пароль приложения: {context.user_data[PASSWORD]}"
    )
    imap_server = get_user_server(context.user_data[EMAIL])
    imap_port = get_user_port(context.user_data[EMAIL])
    try:
        database.add_user(
            user_id,
            context.user_data[EMAIL],
            context.user_data[PASSWORD],
            imap_server,
            imap_port,
            "0",
            0,
            str(datetime.now()),
            "0"
        )
        logger.info(
            "Пользователь user_id=%s добавлен в БД", user_id
        )
    except Exception:
        logger.exception(
            "Не удалось добавить пользователя user_id=%s", user_id
        )
        await update.message.reply_text('Не удалось завершить регистрацию, попробуйте позже')
        context.user_data.clear()
        return ConversationHandler.END

    mail_manager = context.bot_data.get("mail_manager")
    try:
        mail_manager.start_thread_for_user(
            server=imap_server,
            username=context.user_data[EMAIL],
            password=context.user_data[PASSWORD],
            chat_id=user_id,
        )
        context.user_data.clear()
        return ConversationHandler.END
    except Exception:
        logger.exception(
            "Ошибка при запуске IDLE (user_id=%s)", user_id
        )
        await update.message.reply_text('Регистрация завершена, но IDLE не запустился. Попробуйте /check позже')
        context.user_data.clear()
        return ConversationHandler.END

async def help(update: Update, context: CallbackContext):
    """Хендлер-обработчик команды /help (справочная информация)"""
    logger.debug("Команда /help от user_id=%s", update.message.from_user.id)
    await update.message.reply_text(
        "Этот бот создан для автоматической пересылки сообщений с почтового клиента в клиент ТГ"
    )


async def cancel(update: Update, context: CallbackContext):
    """Хендлер-обработчик команды /cancel (отмена регистрации)"""
    logger.info("Регистрация отменена (user_id=%s)", update.message.from_user.id)
    await update.message.reply_text("Регистрация отменена")
    context.user_data.clear()
    return ConversationHandler.END


async def settings(update: Update, context: CallbackContext):
    """Хендлер-обработчик команды /settings для вывода текущих настроек пользователя"""

    logger.info("Запрос настроек user_id=%s", update.message.from_user.id)
    try:
        db = Database()
        user_info = db.get_user_info(update.message.from_user.id)
    except Exception:
        await update.message.reply_text(
            "Не удалось получить настройки, попробуйте позже"
        )
        return

    if not user_info:
        logger.warning("Настройки не найдены user_id=%s", update.message.from_user.id)
        await update.message.reply_text("Вы еще не зарегистрированы")
        return
    await update.message.reply_text(
        f"Текущие настройки\n"
        f"Почтовый адрес: {user_info[1]}\n"
        f"Пароль приложения: {user_info[2]}\n"
        f"IMAP-сервер: {user_info[3]}\n"
        f"Дата регистрации аккаунта: {user_info[7]}"
    )


async def stop_idle(update: Update, context: CallbackContext):
    """Хендлер-обработчки команды /stop_idle для остановки работы IDLE-режмима"""
    logger.info("Запрос остановки IDLE-режима user_id=%s", update.message.from_user.id) # Добавить try/except
    db = Database()
    try:
        result = db.stop_idle(update.message.from_user.id)
    except Exception:
        await update.message.reply_text('Не удалось остановить IDLE, попробуйте позже')
        return

    if result == 'stopped':
        logger.info('IDLE остановлен user_id=%s', update.message.from_user.id)
        await update.message.reply_text('Работа бота остановлена')
    elif result == 'already_stopped':
        logger.info('IDLE уже был остановлен user_id=%s', update.message.from_user.id)
        await update.message.reply_text('IDLE и так не был запущен')
    else:  # not_found
        logger.warning('Пользователь не найден user_id=%s', update.message.from_user.id)
        await update.message.reply_text('Вы не зарегистрированы')


async def manual_check(update: Update, context: CallbackContext):
    """Хендлер-обработчик для команды /check (ручная проверка почты)"""
    user_id = update.message.from_user.id
    try:
        db = Database()
        user_info = db.get_user_info(user_id)
    except Exception:
        await update.message.reply_text('Не удалось получить данные, попробуйте позже')
        return

    if not user_info:
        logger.warning('Пользователь user_id=%s не найден', user_id)
        await update.message.reply_text('Вы не зарегистрированы')
        return

    mail_manager = context.bot_data.get("mail_manager")
    try:
        logger.info("Ручная проверка почты user_id=%s", user_id)
        mail_manager.manual_check(
            server=get_user_server(user_info[1]),
            username=user_info[1],
            password=user_info[2],
            chat_id=user_id,
        )
    except Exception:
        logger.exception('Ошибка ручной проверки user_id=%s', user_id)
        await update.message.reply_text('Не удалось получить данные, попробуйте позже')
        return

    logger.info('Ручная проверка запущена для user_id=%s', user_id)
    await update.message.reply_text("Ручная проверка почты")

async def start_idle(update: Update, context: CallbackContext):
    """Хендлер-обработчик команды /start_idle. Ручной запуск IDLE-режима для пользователя если он был отключен"""
    user_id = update.message.from_user.id
    logger.info('Запрос возобновления IDLE-режима user_id=%s', user_id)

    mail_manager = context.bot_data.get("mail_manager")

    if not mail_manager:
        logger.error('mail_manager не найден в bot_data user_id=%s', user_id)
        await update.message.reply_text('Сервис временно недоступен, попробуйте позже')
        return

    try:
        db = Database()
        user_info = db.get_user_info(user_id)
    except Exception:
        logger.exception('Не удалось получить данные user_id=%s', user_id)
        await update.message.reply_text('Не удалось получить данные, попробуйте позже')
        return

    if not user_info:
        logger.warning('Пользователь не найден user_id=%s', user_id)
        await update.message.reply_text('Вы не зарегистрированы')
        return

    try:
        db.set_active(user_id, 1)
    except Exception:
        await update.message.reply_text('Не удалось возобновить IDLE-режим. Попробуйт позже')
        return

    try:
        mail_manager.start_thread_for_user(
            server=user_info[3],
            username=user_info[1],
            password=user_info[2],
            chat_id=user_id,
        )
        logger.info("IDLE возобновлён user_id=%s", user_id)

    except Exception:
        logger.exception("Не удалось возобновить IDLE user_id=%s", user_id)
        await update.message.reply_text("Не удалось возобновить IDLE, попробуйте позже")
        return
    await update.message.reply_text("IDLE-режим возобновлён")

async def delete(update: Update, context: CallbackContext):
    """Хендлер-обработчик команды /delete для удаления профиля пользователя"""
    await update.message.reply_text('Вы уверенны что хотите удалить аккаунт навсегда? Введите Y если да, в противном случае введите N')
    return CONFIRMATION

async def confirm(update: Update, context: CallbackContext):
    confirmation = update.message.text
    if confirmation == 'Y':

        try:
            db = Database()
            db.delete_user(update.message.from_user.id)
            logger.info('Пользователь user_id=%s удален', update.message.from_user.id)
        except Exception:
            await update.message.reply_text('Не удалось удалить аккаунт, попробуйте позже')
            return ConversationHandler.END

        await update.message.reply_text('Аккаунт удален')
        return ConversationHandler.END

    else:
        await update.message.reply_text('Аккаунт не будет удален')
        return ConversationHandler.END



async def check_idle_status(update: Update, context: CallbackContext):

    try:
        db = Database()
        activity = db.is_active(update.message.from_user.id)
    except Exception:
        await update.message.reply_text('Не удалось узнать статус IDLE-режима, попробуйте позже')
        return

    if activity is None:
        await update.message.reply_text('Вы не зарегистрированы')
        return

    if not activity:
        await update.message.reply_text('IDLE-режим выключен')
        return

    try:
        last_success = db.get_last_success(update.message.from_user.id)
    except Exception:
        await update.message.reply_text('Не удалось узнать статус, попробуйте позже')
        return

    if last_success is None:
        await update.message.reply_text('Подождите минуту, IDLE-режим запускается')
        return

    try:
        last_dt = datetime.strptime(last_success, '%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        logger.exception('Неккоретный last_success для user_id=%s %s', update.message.from_user.id ,last_success)
        await update.message.reply_text('Не удалось узнать статус, попробуйте позже')
        return

    delta = (datetime.now() - last_dt).total_seconds()

    if delta < 180:
        await update.message.reply_text('IDLE-режим активен, связь с сервером есть')
    elif delta < 600:
        await update.message.reply_text(f'IDLE-режим активен, но связь с сервером потеряна {int(delta // 60)} минут назад. Пытаюсь восстановить')
    else:
        await update.message.reply_text(f'IDLE-режим не может подключиться {int(delta // 60)} мин. Попробуйте позже или проверьте /check')



"""Диалог-хендлер (Conversation-Handler) - собирает воедино все хендлеры
    -обработчики для создания диалога. Точка входа (entry-point) - команда
    /start (при условии что пользователь не зарегистрирован ранее). Точка 
    выхода (fallback-point) - команда /cancel ИЛИ завершение регистрации"""
registration_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
        PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

delete_handler = ConversationHandler(
    entry_points=[CommandHandler("delete", delete)],
    states={
        CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)]
    },
    fallbacks=[CommandHandler("cancel", cancel)]),
