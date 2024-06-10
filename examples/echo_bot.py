import os

from dotenv import load_dotenv

from bot_whatsapp import Bot
from bot_whatsapp.filters import MessageContentFilter
from bot_whatsapp.handler import CommandHandler, MessageHandler
from bot_whatsapp.models import OutputMessage, Text, WebhookEvent


async def handle_echo(event: WebhookEvent, bot: Bot):
    message = event.entry[0].changes[0].value.messages[0]
    text = message.text.body
    wa_id = event.entry[0].changes[0].value.contacts[0].wa_id

    output_text = f"Echo: {text}"
    output_message = OutputMessage(
        to=wa_id,
        text=Text(
            body=output_text,
        ),
        type="text",
        messaging_product="whatsapp",
    )
    await bot.send_message(output_message)


async def handle_audio(event: WebhookEvent, bot: Bot):
    message = event.entry[0].changes[0].value.messages[0]
    audio = message.audio

    ext = audio.extension
    await bot.get_media(message.audio, f"audio.{ext}")


async def handle_command(event: WebhookEvent, bot: Bot):
    message = event.entry[0].changes[0].value.messages[0]
    text = message.text.body
    wa_id = event.entry[0].changes[0].value.contacts[0].wa_id

    assert text.startswith("/")

    command = text.split(" ")[0]
    output_text = f"Command: {command}"
    params = text.split(" ")[1:]

    output_text = f"Command: {command} | params: {params}"
    output_message = OutputMessage(
        to=wa_id,
        text=Text(
            body=output_text,
        ),
        type="text",
        messaging_product="whatsapp",
    )
    await bot.send_message(output_message)


# we don't use if __name__ == "__main__" because this runs via fastapi cli
load_dotenv()
whatsapp_token = os.getenv("WHATSAPP_TOKEN")
phone_number_id = os.getenv("PHONE_NUMBER_ID")
webhook_verify_token = os.getenv("WEBHOOK_VERIFY_TOKEN")
bot = Bot(
    whatsapp_token=whatsapp_token,
    phone_number_id=phone_number_id,
    webhook_verify_token=webhook_verify_token,
)
bot.add_handler(CommandHandler("/start", handle_command))
bot.add_handler(MessageHandler(MessageContentFilter.TEXT, handle_echo))
bot.add_handler(MessageHandler(MessageContentFilter.AUDIO, handle_audio))

app = bot.app
# poetry run fastapi dev examples/echo_bot.py
