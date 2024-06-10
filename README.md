# WhatsApp Python SDK

A Python SDK for building bots and integrating with the WhatsApp Business API. Minimally working, but working.

To use it, you must obtain WhatsApp Business API credentials. The [process](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started) is not as kafkian as it may look like.

## Features

- Send and receive messages
- Handle different message types (text, image, audio, document)
- Webhook verification
- Easy-to-use handler system

## Installation

Install the package using `poetry`:

```sh
poetry add bot-whatsapp
```

## Usage

- The code is 100% type hinted and is pretty simple, you can understand what you need just by reading it.
- `examples/echo_bot.py` has an example of usage.

### Setting Up the Bot

Create a bot instance and add handlers:

```python
import os
from dotenv import load_dotenv
from bot_whatsapp import Bot
from bot_whatsapp.filters import MessageContentFilter
from bot_whatsapp.handler import MessageHandler
from bot_whatsapp.models import OutputMessage, Text, WebhookEvent

async def handle_echo(event: WebhookEvent, bot: Bot):
    message = event.entry[0].changes[0].value.messages[0]
    text = message.text.body
    wa_id = event.entry[0].changes[0].value.contacts[0].wa_id

    output_text = f"Echo: {text}"
    output_message = OutputMessage(
        to=wa_id,
        text=Text(body=output_text),
        type="text",
        messaging_product="whatsapp",
    )
    await bot.send_message(output_message)

if __name__ == "__main__":
    load_dotenv()
    whatsapp_token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("PHONE_NUMBER_ID")
    webhook_verify_token = os.getenv("WEBHOOK_VERIFY_TOKEN")
    bot = Bot(
        whatsapp_token=whatsapp_token,
        phone_number_id=phone_number_id,
        webhook_verify_token=webhook_verify_token,
    )
    bot.add_handler(MessageHandler(MessageContentFilter.TEXT, handle_echo))
    bot.start()
```

```bash
poetry run python examples/echo_bot.py
```

Alternatively, you can serve with the fastapi API:

```python
# do not use if __name__ == "__main__" because this runs via fastapi cli
load_dotenv()
whatsapp_token = os.getenv("WHATSAPP_TOKEN")
phone_number_id = os.getenv("PHONE_NUMBER_ID")
webhook_verify_token = os.getenv("WEBHOOK_VERIFY_TOKEN")
bot = Bot(
    whatsapp_token=whatsapp_token,
    phone_number_id=phone_number_id,
    webhook_verify_token=webhook_verify_token,
)
bot.add_handler(MessageHandler(MessageContentFilter.TEXT, handle_echo))
bot.start()
```

Then run

```bash
poetry run fastapi dev examples/echo_bot.py
```

### Environment Variables

Create a `.env` file with the following variables:

```
WHATSAPP_TOKEN=your_whatsapp_token
PHONE_NUMBER_ID=your_phone_number_id
WEBHOOK_VERIFY_TOKEN=your_webhook_verify_token
```

### License

This project is licensed under the Apache 2.0 License. See the [LICENSE](./LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Contact

For any inquiries, please contact [piEsposito](mailto:piero.skywalker@gmail.com).
