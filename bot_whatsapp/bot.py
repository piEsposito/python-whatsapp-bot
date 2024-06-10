from typing import Dict, List

import aiohttp
import uvicorn
from fastapi import FastAPI, HTTPException, Query

from bot_whatsapp.constants import BASE_GRAPH_URL, BASE_MESSAGES_URL
from bot_whatsapp.handler import Handler
from bot_whatsapp.models import Media, OutputMessage, WebhookEvent


class Bot:
    def __init__(
        self,
        whatsapp_token: str,
        webhook_verify_token: str,
        phone_number_id: str,
        webhook_endpoint: str = "/",
    ):
        self.whatsapp_token = whatsapp_token
        self.webhook_verify_token = webhook_verify_token
        self.phone_number_id = phone_number_id
        self.base_message_url = BASE_MESSAGES_URL.format(
            phone_number_id=phone_number_id
        )

        self.app = FastAPI()
        self.app.get("/")(self.webhook_verification)

        assert webhook_endpoint.startswith("/"), "webhook_endpoint must start with /"
        self.app.post(webhook_endpoint)(self.handle_webhook)
        self.handlers: List[Handler] = []

    async def handle_webhook(self, event: WebhookEvent) -> Dict:
        message = event.entry[0].changes[0].value.messages
        if message is None:
            return {
                "detail": "No message found",
            }
        for handler in self.handlers:
            if handler.verify(event):
                await handler.handler(event, self)
                return {"detail": "Handler found"}
        return {
            "detail": "No handler found",
        }

    async def webhook_verification(
        self,
        hub_mode: str | None = Query(None, alias="hub.mode"),
        hub_verify_token: str | None = Query(None, alias="hub.verify_token"),
        hub_challenge: str | None = Query(None, alias="hub.challenge"),
    ) -> int:
        if hub_mode == "subscribe" and hub_verify_token == self.webhook_verify_token:
            print(f"Webhook verified successfully! {hub_challenge=}")
            return int(hub_challenge)
        else:
            raise HTTPException(status_code=403, detail="Forbidden")

    def add_handler(self, handler: Handler):
        self.handlers.append(handler)

    async def send_message(self, message: OutputMessage) -> dict:
        headers = {
            "Authorization": f"Bearer {self.whatsapp_token}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_message_url, headers=headers, json=message.dict()
            ) as response:
                print(await response.json())
                return await response.json()

    async def get_media(self, media: Media, output_path: str):
        print(f"{media.id_=}")
        print(media)
        url = BASE_GRAPH_URL + "/" + media.id_
        headers = {
            "Authorization": f"Bearer {self.whatsapp_token}",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response_json = await response.json()
                url = response_json["url"]
                async with session.get(url, headers=headers) as media_response:
                    with open(output_path, "wb") as f:
                        f.write(await media_response.content.read())

    def start(self, port: int = 8000):
        uvicorn.run(self.app, host="0.0.0.0", port=port)
