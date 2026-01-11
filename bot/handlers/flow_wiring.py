# bot/handlers/flow_wiring.py

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from bot.services.links import build_links, file_requires_password
from bot.utils.logger import log_event


def _links_text(file_key: str) -> str:
    links = build_links(file_key)
    text = (
        "╭━━━〔 ⚡ FILE READY ⚡ 〕━━━╮\n"
        "┃  STATUS : ACTIVE\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "🔗 YOUR LINKS\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        f"🖥️ STREAM ::\n➤ {links['stream']}\n\n"
        f"⬇️ DOWNLOAD ::\n➤ {links['download']}\n\n"
        f"📡 TG FILE ::\n➤ {links['telegram']}\n"
    )

    if file_requires_password(file_key):
        text += (
            "\n━━━━━━━━━━━━━━━━━━━\n"
            "🛡️ SECURITY NOTE\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ PASSWORD REQUIRED to access links.\n"
        )

    return text


def register(app: Client) -> None:
    """
    FINAL LINK DELIVERY GATEKEEPER
    Works for BOTH:
    - Telegram file flow
    - Link ingest flow
    """

    # ─────────── NO PASSWORD (BUTTON CLICK) ───────────
    @app.on_callback_query(filters.regex(r"^pwd_no:"))
    async def _pwd_no_to_links(client: Client, cq: CallbackQuery):
        file_key = cq.data.split(":", 1)[1].strip()
        await cq.answer()

        await cq.message.edit_text(
            _links_text(file_key),
            disable_web_page_preview=True
        )

        await log_event(
            client,
            title="FLOW COMPLETE (NO PASSWORD)",
            body=f"FILE KEY : `{file_key}`",
            event="flow_complete_no_password",
            payload={"file_key": file_key},
            user_id=cq.from_user.id,
            file_key=file_key,
        )

    # ─────────── PASSWORD SET (TEXT REPLY) ───────────
    @app.on_message(
        filters.text
        & filters.reply
        & ~filters.command([
            "start",
            "help",
            "about",
            "stats",
            "user_data",
            "delete",
            "delfile",
        ])
    )
    async def _after_password_set_send_links(client: Client, message: Message):
        replied = message.reply_to_message
        if not replied:
            return

        bot_text = replied.text or ""

        # Must be password success confirmation
        if "PASSWORD SET SUCCESSFULLY" not in bot_text:
            return

        # Extract file_key safely
        if "`" not in bot_text:
            return

        try:
            file_key = bot_text.split("`")[1].strip()
        except Exception:
            return

        if not file_key:
            return

        await message.reply(
            _links_text(file_key),
            disable_web_page_preview=True
        )

        await log_event(
            client,
            title="FLOW COMPLETE (PASSWORD SET)",
            body=f"FILE KEY : `{file_key}`",
            event="flow_complete_password_set",
            payload={"file_key": file_key},
            user_id=message.from_user.id,
            file_key=file_key,
        )
