import asyncio
import logging
from telethon.tl.custom import Button
from telethon.tl.types import ChannelParticipantsAdmins

class RaidConfigManager:
    def __init__(self):
        # Stores current raid configurations for each chat/admin
        self.raid_config = {}
        # Stores the current conversation state for admins
        self.conversation_state = {}
        # Track messages that need to be deleted
        self.last_message_ids = {}

    def get_instructions(self):
        """Return the bot instructions."""
        return (
            "🔰 Instructions on using Xraid Bot 🔰\n\n"
            "1️⃣ Add @Engagetrackerbot to your Telegram group\n\n"
            "2️⃣ MAKE THE BOT AN ADMIN.\n"
            "   Must be Admin to function.\n\n"
            "3️⃣ Only Admins can run the Shield Bot\n\n"
            "4️⃣ To Start A Raid:\n"
            "   ➡️ Enter /shield to lock the chat\n"
            "   ➡️ Follow onscreen prompts\n\n"
            "   ➡️ Enter /end to cancel prompts\n"
            "   ➡️ Enter /cancel to force stop current raid and unlock the chat."
        )

    async def is_admin(self, client, chat_id, user_id):
        """Checks if a user is an admin in a group chat."""
        try:
            # Fetch admins using the ChannelParticipantsAdmins filter
            admins = await client.get_participants(chat_id, filter=ChannelParticipantsAdmins)
            return any(admin.id == user_id for admin in admins)
        except Exception as e:
            logging.error(f"Failed to check admin status in chat {chat_id}: {e}")
            return False