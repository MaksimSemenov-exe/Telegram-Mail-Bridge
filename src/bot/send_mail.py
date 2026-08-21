
async def send_message_to_client(client, message):
    await client.send_message(message.chat.id, message.text)