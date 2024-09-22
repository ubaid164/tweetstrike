import sys
import os
import logging
from telethon import TelegramClient
import tweepy

# Add project root (parent directory of `src`) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import TELEGRAM_BOT_TOKEN
from src.handlers.client import client
from src.handlers.group_commands import handle_group_commands
from src.handlers.admin_commands import handle_admin_commands
from src.modules.raid_config import RaidConfigManager  # Import RaidConfigManager

# Initialize RaidConfigManager
raid_manager = RaidConfigManager()

# Start the client
client.start(bot_token=TELEGRAM_BOT_TOKEN)

# Pass the client and raid_manager to the admin commands handler
handle_admin_commands(client, raid_manager)
handle_group_commands(client)

# Enable logging
logs_folder = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(logs_folder, exist_ok=True)
log_file = os.path.join(logs_folder, 'bot.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()  # Log to console as well
    ]
)

# Start the bot
client.run_until_disconnected()
