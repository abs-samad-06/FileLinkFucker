# bot/handlers/link_delivery.py

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from bot.services.links import build_links, file_requires_password
from bot.utils.logger import log_event


def _format_links(file_key: str) -> str:
    links = build_links(file_key)

    return (
        "━━━━━━━━━━━━━━━━━━━\n"
        "🔗 YOUR LINKS\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        f"🖥️ STREAM ::\n➤ {links['stream']}\n\n"
        f"⬇️ DOWNLOAD ::\n➤ {links['download']}\n\n"
        f"📡 TG FILE ::\n➤ {links['telegram']}\n"
    )


def register(app: Client) -> None:
    """
    Register link delivery callbacks.
    """

    @app.on_callback_query(filters.regex(r"^send_links:"))
    async def send_links_handler(client: Client, cq: CallbackQuery):
        """
        Triggered when system decides links can be sent.
        """
        file_key = cq.data.split(":", 1)[1]

        await cq.answer()

        text = (
            "╭━━━〔 ⚡ FILE READY ⚡ 〕━━━╮\n"
            "┃  STATUS : ACTIVE\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        )

        text += _format_links(file_key)

        if file_requires_password(file_key):
            text += (
                "\n━━━━━━━━━━━━━━━━━━━\n"
                "🛡️ SECURITY NOTE\n"
                "━━━━━━━━━━━━━━━━━━━\n"
                "⚠️ This file is PASSWORD PROTECTED.\n"
                "Access will require the correct password.\n"
            )

        await cq.message.edit_text(text)

        await log_event(
            client,
            title="LINKS SENT",
            body=f"FILE KEY : `{file_key}`",
            event="links_sent",
            payload={"file_key": file_key},
            user_id=cq.from_user.id,
            file_key=file_key,
        )
