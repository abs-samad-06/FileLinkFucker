# bot/handlers/fsub_verify.py

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from bot.utils.fsub import check_fsub, fsub_prompt


def register(app: Client) -> None:
    """
    Register FSUB verify callback handler.
    """

    @app.on_callback_query(filters.regex("^fsub_verify$"))
    async def fsub_verify_handler(client: Client, cq: CallbackQuery):
        user_id = cq.from_user.id

        joined = await check_fsub(client, user_id)

        if not joined:
            # Still not joined → keep locked, show prompt again
            await cq.answer(
                "❌ ACCESS DENIED\nJoin all required channels first.",
                show_alert=True
            )
            try:
                await cq.message.edit_reply_markup(reply_markup=fsub_prompt())
            except Exception:
                pass
            return

        # Joined successfully → unlock
        await cq.answer(
            "✅ ACCESS GRANTED\nSystem unlocked.",
            show_alert=True
        )

        try:
            await cq.message.edit_text(
                text=(
                    "⚡ ACCESS GRANTED\n\n"
                    "You are now verified.\n"
                    "Send a file or paste a link to proceed."
                )
            )
        except Exception:
            pass
