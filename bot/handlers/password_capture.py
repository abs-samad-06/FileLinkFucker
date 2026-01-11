# bot/handlers/password_capture.py

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.utils.passwords import validate_password, set_password
from bot.utils.logger import log_event


def _extract_file_key_from_context(message: Message) -> str:
    """
    Extract file_key from conversation context.
    Strategy:
    - Expect the previous bot message to contain FILE KEY in backticks
    NOTE: Simple & reliable for now; can be upgraded to FSM later.
    """
    if not message.reply_to_message:
        return ""

    text = message.reply_to_message.text or ""
    # Try to find something like `abc123xyz`
    if "`" in text:
        parts = text.split("`")
        if len(parts) >= 2:
            return parts[1].strip()

    return ""


def register(app: Client) -> None:
    """
    Register password capture handler.
    """

    @app.on_message(
        filters.text
        & ~filters.command(["start", "help", "about", "stats", "user_data", "delete", "delfile"])
    )
    async def password_capture_handler(client: Client, message: Message):
        # Only act if user is replying to bot password prompt
        if not message.reply_to_message:
            return

        file_key = _extract_file_key_from_context(message)
        if not file_key:
            return

        password = message.text.strip()

        # Validate password
        ok, reason = validate_password(password)
        if not ok:
            await message.reply(
                f"❌ INVALID PASSWORD\nReason: {reason}\n\nTry again."
            )
            return

        # Save password
        set_password(file_key, password)

        await message.reply(
            "🔐 PASSWORD SET SUCCESSFULLY\n\n"
            "Generating secure access links..."
        )

        # Log event
        await log_event(
            client,
            title="PASSWORD SET",
            body=f"FILE KEY : `{file_key}`",
            event="password_set",
            payload={"file_key": file_key},
            user_id=message.from_user.id,
            file_key=file_key,
        )

        # NOTE:
        # Link generation will be triggered next (separate handler/service)
