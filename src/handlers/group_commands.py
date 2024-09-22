import time
import logging
import sys
import requests
from telethon import events
from telethon.tl.types import ChannelParticipantsAdmins
from src.handlers.client import client  # Import your client
from src.config import TWITTER_BEARER_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Dictionary to store settings and state for each raid
raid_data = {}

# Helper function to check if the user is an admin in the group
async def is_admin(client, chat_id, user_id):
    try:
        admins = await client.get_participants(chat_id, filter=ChannelParticipantsAdmins)
        return any(admin.id == user_id for admin in admins)
    except Exception as e:
        logging.error(f"Failed to check admin status in chat {chat_id}: {e}")
        return False

# Group command handler registration
def handle_group_commands(client):
    # Catch-all message handler for debugging
    @client.on(events.NewMessage)
    async def handle_any_message(event):
        logging.info(f"Received message: {event.message.message} from user {event.sender_id} in chat {event.chat_id}")

    # Function to handle /raid command in group chats
    @client.on(events.NewMessage(pattern='/raid(?:@Engagetrackerbot)?'))
    async def handle_raid_command(event):
        logging.info(f"Received /raid command from user {event.sender_id} in chat {event.chat_id}")
        if event.is_private:
            logging.info("Command was received in private chat, but it is only for group chats.")
            await event.respond("The /raid command can only be used in groups.")
            return

        # Check if the user is an admin
        user_id = event.sender_id
        chat_id = event.chat_id
        logging.info(f"Checking if user {user_id} is admin in chat {chat_id}")
        if not await is_admin(client, chat_id, user_id):
            logging.info("User is not an admin.")
            await event.respond("You must be an admin to use the /raid command.")
            return

        # Start the raid configuration process
        logging.info(f"User {user_id} is admin. Starting the raid configuration process.")
        await event.respond("Please provide the tweet link for the raid.")
        raid_data[chat_id] = {
            'state': 'awaiting_tweet_link',
            'admin_id': user_id
        }

    # Handle raid settings input
    @client.on(events.NewMessage)
    async def handle_raid_input(event):
        chat_id = event.chat_id
        user_id = event.sender_id
        message = event.message.message.strip()

        if chat_id in raid_data and raid_data[chat_id].get('admin_id') == user_id:
            state = raid_data[chat_id].get('state')

            if state == 'awaiting_tweet_link':
                raid_data[chat_id]['tweet_link'] = message
                raid_data[chat_id]['state'] = 'awaiting_likes'
                await event.respond("How many likes do you want to target?")

            elif state == 'awaiting_likes':
                raid_data[chat_id]['target_likes'] = int(message)
                raid_data[chat_id]['state'] = 'awaiting_replies'
                await event.respond("How many replies do you want to target?")

            elif state == 'awaiting_replies':
                raid_data[chat_id]['target_replies'] = int(message)
                raid_data[chat_id]['state'] = 'awaiting_reposts'
                await event.respond("How many reposts do you want to target?")

            elif state == 'awaiting_reposts':
                raid_data[chat_id]['target_reposts'] = int(message)
                raid_data[chat_id]['state'] = 'awaiting_bookmarks'
                await event.respond("How many bookmarks do you want to target?")

            elif state == 'awaiting_bookmarks':
                raid_data[chat_id]['target_bookmarks'] = int(message)
                raid_data[chat_id]['state'] = 'raid_active'
                # Start monitoring the tweet
                await event.respond("🚨 Raid started! We will monitor the tweet progress.")
                await monitor_raid_progress(client, event, chat_id)

# Additional functions (fetch_tweet_stats and monitor_raid_progress) would follow here with proper indentation and scope.

# Function to fetch tweet statistics using Twitter API v2
def fetch_tweet_stats(tweet_id):
    url = f"https://api.twitter.com/2/tweets/{tweet_id}?tweet.fields=public_metrics"
    
    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        public_metrics = data['data']['public_metrics']

        return {
            'likes': public_metrics['like_count'],
            'replies': public_metrics['reply_count'],
            'reposts': public_metrics['retweet_count'],
            'bookmarks': 0  # Twitter API v2 does not expose bookmark count (you can leave this as 0)
        }
    else:
        logging.error(f"Failed to fetch tweet stats: {response.status_code} - {response.text}")
        print(f"Error {response.status_code}: {response.text}")  # Print error details to console for debugging
        return None

# Function to monitor raid progress and send updates
async def monitor_raid_progress(client, event, chat_id):
    raid = raid_data[chat_id]
    tweet_link = raid['tweet_link']
    try:
        tweet_id = tweet_link.split("/")[-1]  # Extract the tweet ID from the tweet URL
    except IndexError:
        await client.send_message(chat_id, "⚠️ Invalid tweet link provided.")
        logging.error(f"Invalid tweet link: {tweet_link}")
        return

    target_likes = raid['target_likes']
    target_replies = raid['target_replies']
    target_reposts = raid['target_reposts']
    target_bookmarks = raid['target_bookmarks']

    while True:
        # Fetch current tweet statistics using the Twitter API
        current_stats = fetch_tweet_stats(tweet_id)
        
        if not current_stats:
            await client.send_message(chat_id, "⚠️ Failed to fetch tweet statistics. Please check the tweet link and try again.")
            break

        # Send progress update
        await client.send_message(chat_id, 
            f"🚨 Raid Progress 🚨\n\n"
            f"🎯 Tweet Statistics:\n"
            f"🟥 Current Likes: {current_stats['likes']} / {target_likes}\n"
            f"🟥 Current Retweets: {current_stats['reposts']} / {target_reposts}\n"
            f"🟥 Current Replies: {current_stats['replies']} / {target_replies}\n"
            f"🟥 Current Bookmarks: {current_stats['bookmarks']} / {target_bookmarks}\n\n"
            f"🔗 {tweet_link}"
        )

        # Check if the raid is complete
        if (current_stats['likes'] >= target_likes and
            current_stats['replies'] >= target_replies and
            current_stats['reposts'] >= target_reposts and
            current_stats['bookmarks'] >= target_bookmarks):
            await client.send_message(chat_id, "✅ Raid is complete! All targets have been hit!")
            logging.info(f"Raid in chat {chat_id} is complete.")
            del raid_data[chat_id]  # Clean up the raid data
            break

        # Wait for 6-7 seconds before checking again
        time.sleep(7)

# Function to handle /cancel_raid command in group chats
@client.on(events.NewMessage(pattern='/cancel_raid(?:@Engagetrackerbot)?'))
async def handle_cancel_raid_command(event):
    logging.info(f"Received /cancel_raid command from user {event.sender_id} in chat {event.chat_id}")

    if event.is_private:
        logging.info("Command was received in private chat, but it is only for group chats.")
        await event.respond("The /cancel_raid command can only be used in groups.")
        return

    # Check if the user is an admin
    user_id = event.sender_id
    chat_id = event.chat_id

    if not await is_admin(client, chat_id, user_id):
        logging.info("User is not an admin.")
        await event.respond("You must be an admin to use the /cancel_raid command.")
        return

    # Check if there is an active raid in the group
    if chat_id in raid_data and raid_data[chat_id].get('admin_id') == user_id:
        # Cancel the raid and clear the data
        del raid_data[chat_id]
        await event.respond("The raid has been successfully canceled.")
        logging.info(f"Raid in chat {chat_id} has been canceled by admin {user_id}.")
    else:
        await event.respond("No active raid found to cancel.")
        logging.info("No active raid found to cancel.")
