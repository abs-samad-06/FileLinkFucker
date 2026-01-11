# bot/handlers/start.py

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.config import FSUB_CHANNELS
from bot.utils.fsub import check_fsub, fsub_prompt


def register(app: Client) -> None:
    """
    Register /start command handler.
    """

    @app.on_message(filters.command("start"))
    async def start_handler(client: Client, message: Message):
        # Always reply so bot never feels dead
        # FSUB check (soft-gate: warn here, hard-gate on file/link actions)
        if FSUB_CHANNELS:
            joined = await check_fsub(client, message.from_user.id)
            if not joined:
                # Soft block on /start: show warning + buttons
                await message.reply(
                    text=(
                        "⚠️ SYSTEM ONLINE\n\n"
                        "Limited access detected.\n"
                        "Join required channels to unlock full system."
                    ),
                    reply_markup=fsub_prompt()
                )
                return

        # Normal /start response (placeholder text)
        await message.reply(
            text=(
                "⚡ SYSTEM ONLINE\n\n"
                "FileLinkFucker is active.\n"
                "Send a file or paste a link to proceed."
            )
        )
