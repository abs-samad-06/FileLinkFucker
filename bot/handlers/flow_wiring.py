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
    Wire password flow to link delivery.
    """

    # When user clicks "NO, SKIP PASSWORD"
    @app.on_callback_query(filters.regex(r"^pwd_no:"))
    async def _pwd_no_to_links(client: Client, cq: CallbackQuery):
        file_key = cq.data.split(":", 1)[1]
        await cq.answer()

        await cq.message.edit_text(_links_text(file_key))

        await log_event(
            client,
            title="FLOW COMPLETE (NO PASSWORD)",
            body=f"FILE KEY : `{file_key}`",
            event="flow_complete_no_password",
            payload={"file_key": file_key},
            user_id=cq.from_user.id,
            file_key=file_key,
        )

    # After password is set successfully, user sends password text
    # We detect the success message and then push links
    @app.on_message(filters.text & ~filters.command)
    async def _after_password_set_send_links(client: Client, message: Message):
        # Trigger only if bot confirmed password set
        if not message.reply_to_message:
            return

        bot_text = message.reply_to_message.text or ""
        if "PASSWORD SET SUCCESSFULLY" not in bot_text:
            return

        # Extract file_key from the bot message context
        # Expect format: FILE KEY : `xxxxx`
        text = bot_text
        if "`" not in text:
            return

        file_key = text.split("`")[1].strip()

        await message.reply(_links_text(file_key))

        await log_event(
            client,
            title="FLOW COMPLETE (PASSWORD SET)",
            body=f"FILE KEY : `{file_key}`",
            event="flow_complete_password_set",
            payload={"file_key": file_key},
            user_id=message.from_user.id,
            file_key=file_key,
        )
