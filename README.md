# Telegram Mail Bridge

![Python](https://img.shields.io/badge/python-3.12-blue?logo=python)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-brightgreen)
![Last Commit](https://img.shields.io/github/last-commit/MaksimSemenov-exe/Telegram-Mail-Bridge)

**Telegram Mail Bridge** пересылает письма с вашей почты прямо в Telegram. Подключите свой ящик - и получайте уведомления о новых письмах мгновенно, включая вложения.

---

## Возможности

- Мгновенные уведомления о новых письмах (IMAP IDLE)
- Поддержка нескольких пользователей
- Пересылка вложений
- Регистрация прямо в боте
- Хранение настроек в SQLite
- Логирование всех операций
- Остановка и удаление аккаунта

---

## Как это работает

1. Вы регистрируетесь в боте: указываете email и пароль приложения.
2. Бот подключается к вашему почтовому ящику через IMAP.
3. При поступлении нового письма бот отправляет его в Telegram.

---

## Установка

```bash
git clone https://github.com/MaksimSemenov-exe/Telegram-Mail-Bridge.git
cd Telegram-Mail-Bridge
pip install -r requirements.txt
```

---

## ⚙️ Настройка

Создайте файл `config.env` в корне проекта:

```
BOT_TOKEN=ваш_токен_бота
```

Токен можно получить у [@BotFather](https://t.me/BotFather).

---

## Запуск

```bash
python src/main.py
```

---

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Регистрация или приветствие |
| `/settings` | Текущие настройки |
| `/stop` | Остановить уведомления |
| `/check` | Ручная проверка почты |
| `/delete` | Удалить аккаунт |
| `/help` | Справка |

---

## Технологии

- Python 3.12
- `python-telegram-bot`
- `imap_tools`
- SQLite
- `threading`

---

## Лицензия

MIT