# utils.py

async def is_admin(chat_id, user_id, client):
    """Check if a user is an admin in the given chat."""
    try:
        participant = await client.get_permissions(chat_id, user_id)
        return participant.is_admin or participant.is_creator
    except Exception:
        return False
