# src/client.py
from telethon import TelegramClient
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_API_ID, TELEGRAM_API_HASH

# Initialize the Telegram client
client = TelegramClient('raid_bot', TELEGRAM_API_ID, TELEGRAM_API_HASH)

# Start the client
client.start(bot_token=TELEGRAM_BOT_TOKEN)
