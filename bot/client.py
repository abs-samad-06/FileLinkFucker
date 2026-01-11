# bot/client.py

from pyrogram import Client
from bot.config import API_ID, API_HASH, BOT_TOKEN


def create_bot() -> Client:
    """
    Create and return the Pyrogram Client instance.
    This is the single source of truth for the bot client.
    """
    app = Client(
        name="filelinkfucker",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        workers=16,
        in_memory=True,
    )
    return app
