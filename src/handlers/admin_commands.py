from telethon import events, Button
import logging
from src.handlers.client import client  # Import the client from src/handlers/client.py

# Dictionary to store the last message ID for each user
last_message_ids = {}
user_conversations = {}

# Global raid_manager variable
raid_manager = None

# Delete the previous message before sending a new one
async def delete_previous_message(client, event):
    chat_id = event.chat_id
    if chat_id in last_message_ids:
        try:
            await client.delete_messages(chat_id, last_message_ids[chat_id])
        except Exception as e:
            logging.error(f"Error deleting previous message: {e}")

# Function to show the initial instructions with two buttons
async def start(event):
    global raid_manager  # Use the global raid_manager
    await delete_previous_message(client, event)
    instructions = raid_manager.get_instructions() + "\n\n"
    message = await event.respond(
        instructions,
        buttons=[
            [Button.url("Add me to your group", "https://t.me/Engagetrackerbot?startgroup=true")],
            [Button.inline("Show Ads", b"show_ads")]
        ]
    )
    last_message_ids[event.chat_id] = message.id

# Function to handle admin-related commands
def handle_admin_commands(client, raid_manager_instance):  # Pass client and raid_manager
    global raid_manager
    raid_manager = raid_manager_instance  # Assign the passed raid_manager to the global variable

    # Handle the /start command in private chat and send the instructions with two buttons
    @client.on(events.NewMessage(pattern='/start'))
    async def start_command(event):
       if not event.is_private:  # Restrict the /start command to private chats only
        await event.respond("The /start command is only available in private chats.")
        return
    
        await start(event)  # Proceed to the start function if it's a private chat
    async def show_ad_pricing(event):
        await delete_previous_message(client, event)
        pricing_message = (
            "📢 **Ads pricing**\n\n"
            "Spybox statistics:\n"
            "4758+ groups actively using Spybox\n"
            "2.8+ million Telegram group members\n\n"
            "❶ **AD BUTTON**:\n"
            "This ad will be displayed at the bottom of the follow notification as a button.\n\n"
            "❷ **AD TEXT**:\n"
            "This ad will be displayed at the bottom of the follow notification as a text.\n\n"
            "❶ + ❷ **COMBO**:\n"
            "Both placements, meaning text and button will be displayed for a discounted price.\n\n"
            "View pricing by selecting one of the options below."
        )
        message = await event.respond(
            pricing_message,
            buttons=[
                [Button.inline("❶ Ad Button", b"ad_button"), Button.inline("Preview", b"preview_ad_button")],
                [Button.inline("❷ Ad Text", b"ad_text"), Button.inline("Preview", b"preview_ad_text")],
                [Button.inline("❶ + ❷ Combo", b"combo"), Button.inline("Preview", b"preview_combo")]
            ]
        )
        last_message_ids[event.chat_id] = message.id

    # Handle button clicks for ad options
    @client.on(events.CallbackQuery)
    async def handle_callback(event):
        data = event.data.decode('utf-8')
        logging.info(f"Button clicked with data: {data}")  # Log the button click

        # Handle show_ads button
        if data == "show_ads":
            logging.info("Show Ads button clicked, showing ad pricing.")
            await show_ad_pricing(event)  # Call the show_ad_pricing function when show_ads button is clicked
            return

        # Define the descriptions for each ad type
        ad_button_description = (
            "❶ Ad Button\n\n"
            "This ad will be displayed at the bottom of the follow notification as a button.\n\n"
            "For support, kindly contact our Ads Manager.\n\n"
            "Cryptocurrency accepted:\n"
            "SOL, ETH, USDT, BTC, USDC, BNB, LTC, TRX, XMR, MATIC, DASH, DOGE, TON, BCH, AVAX, DAI, VERSE, SHIB\n\n"
            "Choose the ad package you want to purchase."
        )
        ad_text_description = (
            "❷ Ad Text\n\n"
            "This ad will be displayed at the bottom of the follow notification as a text.\n\n"
            "For support, kindly contact our Ads Manager.\n\n"
            "Cryptocurrency accepted:\n"
            "SOL, ETH, USDT, BTC, USDC, BNB, etc.\n\n"
            "Choose the ad package you want to purchase."
        )
        combo_description = (
            "❶ + ❷ Combo (Ad text + button)\n\n"
            "Both placements will be displayed for a discounted price.\n\n"
            "For support, kindly contact our Ads Manager.\n\n"
            "Cryptocurrency accepted:\n"
            "SOL, ETH, USDT, BTC, USDC, BNB, LTC, TRX, XMR, MATIC, DASH, DOGE, TON, BCH, AVAX, DAI, VERSE, SHIB\n\n"
            "Choose the ad package you want to purchase."
        )

        # Handle the ad button clicks
        if data == "ad_button":
            logging.info("Ad Button clicked, displaying pricing.")
            await show_ad_button_pricing(client, event, "Ad Button", ad_button_description)
        elif data == "ad_text":
            logging.info("Ad Text clicked, displaying pricing.")
            await show_ad_button_pricing(client, event, "Ad Text", ad_text_description)
        elif data == "combo":
            logging.info("Combo Button clicked, displaying pricing.")
            await show_ad_button_pricing(client, event, "Combo", combo_description)

        # Handle "Preview" button clicks
        elif data.startswith("preview_"):
            logging.info(f"Preview button clicked: {data}")
            await event.respond("Preview functionality coming soon.", buttons=[Button.inline("Back to Ads", b"back_to_ads")])
        elif data == "back_to_ads":
            logging.info("Back to Ads button clicked.")
            await show_ad_pricing(event)

        # Handle the pricing button clicks (progress to user input)
        if data.startswith("pricing_"):
            logging.info(f"Pricing selected: {data}")
            await handle_pricing_selection(client, event, data)

# Show pricing with different text for each ad type
async def show_ad_button_pricing(client, event, ad_type, description):
    await delete_previous_message(client, event)  # Ensure the previous message is deleted
    message = await event.respond(
        f"🛒 **{ad_type} Pricing**\n\n"
        f"{description}\n\n"
        "Select the duration for your ad placement:",
        buttons=[
            [Button.inline("1 Day - $170", f"pricing_{ad_type}_1_day")],
            [Button.inline("7 Days - $300", f"pricing_{ad_type}_7_days")],
            [Button.inline("15 Days - $500", f"pricing_{ad_type}_15_days")],
            [Button.inline("1 Month - $900", f"pricing_{ad_type}_1_month")],
            [Button.inline("Back to Ads", b"back_to_ads")]
        ]
    )
    last_message_ids[event.chat_id] = message.id  # Store the new message ID

# Handle pricing selection, ask for Telegram username
async def handle_pricing_selection(client, event, data):
    ad_type, duration = data.split('_')[1:3]  # Extract ad type and duration
    user_conversations[event.chat_id] = {
        'ad_type': ad_type,
        'duration': duration,
        'cost': get_cost(duration),
        'state': 'awaiting_username'
    }
    await delete_previous_message(client, event)  # Delete previous pricing message
    message = await event.respond(
        f"Great choice! You've selected {ad_type} for {duration}.\n\n"
        "Please enter your Telegram username in case we need to contact you.\n\n"
        "If you want to end the conversation, type /cancel"
    )
    last_message_ids[event.chat_id] = message.id  # Store the new message ID

# Get the cost based on duration
def get_cost(duration):
    if duration == '1_day':
        return 170
    elif duration == '7_days':
        return 300
    elif duration == '15_days':
        return 500
    elif duration == '1_month':
        return 900

# Handle text inputs for username, ad message, and ad link
@client.on(events.NewMessage)
async def handle_user_message(event):
    chat_id = event.chat_id
    user_input = event.message.message.strip()

    if user_input.lower() == "/cancel":
        await event.respond("Conversation canceled.")
        user_conversations.pop(chat_id, None)
        await start(event)  # Reset to initial instructions
        return

    if chat_id not in user_conversations:
        return  # Exit if no active conversation for the user

    conversation = user_conversations[chat_id]
    state = conversation.get('state')

    if state == 'awaiting_username':
        conversation['username'] = user_input
        conversation['state'] = 'awaiting_ad_message'
        await delete_previous_message(client, event)
        message = await event.respond(
            "Great! Now, please provide the AD message.\n\n"
            "Please keep it under 30 characters and use only standard emojis.\n\n"
            "Example: Top signal Channel\n\n"
            "If you want to end the conversation, type /cancel"
        )
        last_message_ids[event.chat_id] = message.id  # Store the new message ID

    elif state == 'awaiting_ad_message':
        conversation['ad_message'] = user_input
        conversation['state'] = 'awaiting_ad_link'
        await delete_previous_message(client, event)
        message = await event.respond(
            "Thank you!\n\n"
            "Now please provide the AD link.\n\n"
            "Example: https://t.me/spyboxofficial\n\n"
            "If you want to end the conversation, type /cancel"
        )
        last_message_ids[event.chat_id] = message.id  # Store the new message ID

    elif state == 'awaiting_ad_link':
        conversation['ad_link'] = user_input
        await delete_previous_message(client, event)
        await send_confirmation(client, event)

# Send the final confirmation message
async def send_confirmation(client, event):
    chat_id = event.chat_id
    conversation = user_conversations[chat_id]

    username = conversation['username']
    ad_message = conversation['ad_message']
    ad_link = conversation['ad_link']
    ad_type = conversation['ad_type']
    duration = conversation['duration']
    cost = conversation['cost']

    message = await event.respond(
        f"Please confirm your ad details:\n\n"
        f"Username: @{username}\n"
        f"Message: {ad_message}\n"
        f"Link: {ad_link}\n"
        f"Duration: {duration.replace('_', ' ')}\n"
        f"Cost: {cost} USD\n"
        f"Type: {ad_type}\n\n"
        "Click 'Yes' to proceed with payment or 'Cancel' to make changes.",
        buttons=[
            [Button.inline("Yes", b"payment_yes"), Button.inline("Cancel", b"payment_cancel")]
        ]
    )
    last_message_ids[event.chat_id] = message.id  # Store the new message ID

# Handle the payment confirmation process
@client.on(events.CallbackQuery)
async def handle_payment(event):
    data = event.data.decode('utf-8')

    if data == "payment_yes":
        await event.respond(
            "Step 1: Complete the payment here: https://pay.cryptomus.com/pay/bd3f3f5a-adcb-4ff8-8a8d-36fdd0d15225\n\n"
            "Step 2: Click the button below once you've completed the payment."
        )
        # You could implement an automatic payment verification logic here as well
    elif data == "payment_cancel":
        await delete_previous_message(client, event)
        await start(event)  # Reset the flow to the initial instructions
