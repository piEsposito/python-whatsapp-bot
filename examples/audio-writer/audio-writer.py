import os
from uuid import uuid4

from dotenv import load_dotenv
from tiny_ai_client import AsyncAI

from bot_whatsapp import Bot
from bot_whatsapp.filters import MessageContentFilter
from bot_whatsapp.handler import CommandHandler, MessageHandler
from bot_whatsapp.models import OutputMessage, Text, WebhookEvent


async def transcribe(audio_file_path: str) -> str:
    from openai import AsyncOpenAI

    client = AsyncOpenAI()

    with open(audio_file_path, "rb") as audio_file:
        transcription = await client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )
    return transcription.text


async def summarize(long_text: str) -> str:
    SYSTEM = "You are a text summarizer. Summarize the following transcribed voice note with bullet points on its original language."
    ai = AsyncAI(
        "gemini-1.5-pro",
        max_new_tokens=512,
        system=SYSTEM,
        timeout=30,
    )
    summary = await ai(long_text)
    return summary


async def handle_echo(event: WebhookEvent, bot: Bot):
    wa_id = event.entry[0].changes[0].value.contacts[0].wa_id

    output_text = "Send me an audio and I'll write it for you!"
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
    wa_id = event.entry[0].changes[0].value.contacts[0].wa_id
    audio = message.audio

    fname = str(uuid4())
    ext = audio.extension
    fname = f"{fname}.{ext}"
    await bot.get_media(message.audio, fname)
    transcription = await transcribe(fname)

    for i in range(0, len(transcription), 2048):
        chunk = transcription[i : i + 2048]
        output_message = OutputMessage(
            to=wa_id,
            text=Text(
                body=chunk,
            ),
            type="text",
            messaging_product="whatsapp",
        )
        await bot.send_message(output_message)

    if len(transcription) > 512:
        summary = await summarize(transcription)
        output_message = OutputMessage(
            to=wa_id,
            text=Text(
                body=summary,
            ),
            type="text",
            messaging_product="whatsapp",
        )
        await bot.send_message(output_message)
    os.remove(fname)


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
# poetry run fastapi dev audio-writer.py
