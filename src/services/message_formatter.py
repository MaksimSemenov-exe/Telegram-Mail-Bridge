def format_message(msg: dict, with_attachments: bool = False) -> str:
    """Собирает текст письма для отправки в Telegram"""
    msg_text = f'От: {msg['from']}\nТема: {msg['subject']}\nТекст: {msg['text']}'

    if with_attachments:
        msg_text += '\nВложения будут отправлены ниже'

    return msg_text