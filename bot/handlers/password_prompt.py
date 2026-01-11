# bot/handlers/password_prompt.py

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.utils.logger import log_event


def password_prompt_buttons(file_key: str) -> InlineKeyboardMarkup:
    """
    Generate YES / NO buttons for password protection prompt.
    """
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="🔐 YES, SET PASSWORD",
                    callback_data=f"pwd_yes:{file_key}",
                ),
                InlineKeyboardButton(
                    text="❌ NO, SKIP",
                    callback_data=f"pwd_no:{file_key}",
                ),
            ]
        ]
    )


def register(app: Client) -> None:
    """
    Register password prompt callback handlers.
    """

    @app.on_callback_query(filters.regex(r"^pwd_yes:"))
    async def password_yes_handler(client: Client, cq: CallbackQuery):
        file_key = cq.data.split(":", 1)[1]

        await cq.answer()

        await cq.message.edit_text(
            text=(
                "🔑 SEND PASSWORD\n\n"
                "Rules:\n"
                "• Minimum 6 characters\n"
                "• Numbers / letters / @ allowed\n\n"
                "Example:\n"
                "`123456`, `Sam123`, `@Samad`"
            )
        )

        # Mark message state via reply-to trick (simple approach)
        # Actual password capture handled in next handler
        await log_event(
            client,
            title="PASSWORD REQUESTED",
            body=f"FILE KEY : `{file_key}`",
            event="password_requested",
            payload={"file_key": file_key},
            file_key=file_key,
        )

    @app.on_callback_query(filters.regex(r"^pwd_no:"))
    async def password_no_handler(client: Client, cq: CallbackQuery):
        file_key = cq.data.split(":", 1)[1]

        await cq.answer("Password skipped")

        await cq.message.edit_text(
            text=(
                "⚡ FILE READY\n\n"
                "Password protection skipped.\n"
                "Generating access links..."
            )
        )

        # Links generation will be handled later
        await log_event(
            client,
            title="PASSWORD SKIPPED",
            body=f"FILE KEY : `{file_key}`",
            event="password_skipped",
            payload={"file_key": file_key},
            user_id=cq.from_user.id,
            file_key=file_key,
  )
