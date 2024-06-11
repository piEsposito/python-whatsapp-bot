# Audio Writer

This Python script `audio-writer.py` is designed to transcribe audio files and summarize the transcribed text using AI models. It interacts with a WhatsApp bot to handle audio messages, transcribe them, and provide summaries back to the user.

## Functionality

- **Transcribe Audio**: The script can transcribe audio files using the OpenAI API.
- **Summarize Text**: It can summarize long text using an AI text summarizer.
- **WhatsApp Bot Integration**: Handles commands and audio messages from a WhatsApp bot.

## Setup

1. Install the required dependencies using `poetry install`.
2. Set up environment variables in a `.env` file (e.g., `WHATSAPP_TOKEN`, `PHONE_NUMBER_ID`, `WEBHOOK_VERIFY_TOKEN`, `OPENAI_API_KEY`).
3. Run the script using `poetry run fastapi dev audio-writer.py`.

## Usage

- Send an audio message to the WhatsApp bot to transcribe it.
- Use commands like `/start` to interact with the bot.

## Note

- The script runs via FastAPI CLI and interacts with the WhatsApp API for messaging.

Feel free to explore and modify the script for your own use case!
