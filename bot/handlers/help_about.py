# bot/handlers/help_about.py

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.texts import (
    START_TEXT,
    HELP_TEXT,
    ABOUT_TEXT,
)
from bot.config import FSUB_CHANNELS
from bot.utils.fsub import check_fsub, fsub_prompt


def register(app: Client) -> None:
    """
    Register /start, /help, /about handlers
    using centralized hacker-style texts.
    """

    @app.on_message(filters.command("start"))
    async def start_handler(client: Client, message: Message):
        # Soft FSUB check (warning only)
        if FSUB_CHANNELS:
            joined = await check_fsub(client, message.from_user.id)
            if not joined:
                await message.reply(
                    text=START_TEXT,
                    reply_markup=fsub_prompt(),
                )
                return

        await message.reply(START_TEXT)

    @app.on_message(filters.command("help"))
    async def help_handler(client: Client, message: Message):
        await message.reply(HELP_TEXT)

    @app.on_message(filters.command("about"))
    async def about_handler(client: Client, message: Message):
        await message.reply(ABOUT_TEXT)
