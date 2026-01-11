# bot/handlers/upload.py

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.config import FSUB_CHANNELS
from bot.utils.fsub import check_fsub, fsub_prompt
from bot.services.storage import store_telegram_file
from bot.handlers.password_prompt import password_prompt_buttons
from bot.utils.logger import log_event


def register(app: Client) -> None:
    """
    Register Telegram file upload handler.
    """

    @app.on_message(filters.document | filters.video | filters.audio)
    async def upload_handler(client: Client, message: Message):
        user = message.from_user

        # ───── FSUB CHECK ─────
        if FSUB_CHANNELS:
            joined = await check_fsub(client, user.id)
            if not joined:
                await message.reply(
                    "⛔ ACCESS DENIED\n\nJoin required channels to upload files.",
                    reply_markup=fsub_prompt(),
                )
                return

        # Acknowledge
        status_msg = await message.reply(
            "⚡ FILE INTERCEPTED\nProcessing..."
        )

        try:
            # Store Telegram file
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

        # ───── PASSWORD PROMPT (CRITICAL FIX) ─────
        await status_msg.edit_text(
            text=(
                "🔐 PROTECT THIS FILE?\n\n"
                f"FILE KEY : `{file_key}`\n\n"
                "Do you want to set a password?"
            ),
            reply_markup=password_prompt_buttons(file_key),
            disable_web_page_preview=True,
        )

        await log_event(
            client,
            title="FILE INGESTED",
            body=f"FILE KEY : `{file_key}`",
            event="file_ingested",
            payload={"file_key": file_key},
            user_id=user.id,
            file_key=file_key,
        )
