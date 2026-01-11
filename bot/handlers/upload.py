# bot/handlers/upload.py

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.config import FSUB_CHANNELS
from bot.utils.fsub import check_fsub, fsub_prompt
from bot.services.storage import store_telegram_file
from bot.utils.logger import log_event


def register(app: Client) -> None:
    """
    Register Telegram file upload handler.
    """

    @app.on_message(
        filters.document | filters.video | filters.audio
    )
    async def upload_handler(client: Client, message: Message):
        user = message.from_user

        # HARD FSUB GATE
        if FSUB_CHANNELS:
            joined = await check_fsub(client, user.id)
            if not joined:
                await message.reply(
                    text=(
                        "⛔ ACCESS DENIED\n\n"
                        "Join required channels to upload files."
                    ),
                    reply_markup=fsub_prompt()
                )
                return

        # Acknowledge interception
        status_msg = await message.reply(
            "⚡ FILE INTERCEPTED\nProcessing..."
        )

        try:
            # Store file (handles duplicates internally)
            file_key, file_doc = await store_telegram_file(
                client,
                source_message=message,
            )
        except Exception as e:
            await status_msg.edit_text(
                "❌ FAILED TO PROCESS FILE\nTry again later."
            )
            await log_event(
                client,
                title="FILE STORE FAILED",
                body=str(e),
                event="file_store_failed",
                payload={"error": str(e)},
                user_id=user.id,
            )
            return

        # Ask for password protection (actual links sent later)
        await status_msg.edit_text(
            text=(
                "🔐 PROTECT THIS FILE?\n\n"
                "Do you want to set a password?"
            ),
            reply_markup=None,
        )

        # NOTE:
        # Password prompt + link generation will be wired
        # in next handlers (callbacks / message flow)
