# bot/handlers/link_detect.py

import re
from pyrogram import Client, filters
from pyrogram.types import Message

from bot.config import FSUB_CHANNELS
from bot.utils.fsub import check_fsub, fsub_prompt
from bot.utils.logger import log_event

# Basic URL regex (safe & simple)
URL_REGEX = re.compile(
    r"(https?://[^\s]+)",
    re.IGNORECASE,
)


def _identify_source(url: str) -> str:
    """
    Identify link source type.
    """
    u = url.lower()

    if "t.me/" in u:
        return "telegram"
    if "terabox" in u:
        return "terabox"
    if "drive.google.com" in u:
        return "gdrive"
    if "mediafire.com" in u:
        return "mediafire"
    if "mega.nz" in u:
        return "mega"
    return "direct"


def register(app: Client) -> None:
    """
    Register auto link detection handler.
    """

    @app.on_message(
        filters.text
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
    async def link_detect_handler(client: Client, message: Message):
        text = message.text or ""
        match = URL_REGEX.search(text)
        if not match:
            return  # No link → ignore

        url = match.group(1)
        user = message.from_user

        # HARD FSUB GATE (links too)
        if FSUB_CHANNELS:
            joined = await check_fsub(client, user.id)
            if not joined:
                await message.reply(
                    text=(
                        "⛔ ACCESS DENIED\n\n"
                        "Join required channels to process links."
                    ),
                    reply_markup=fsub_prompt()
                )
                return

        source = _identify_source(url)

        status_msg = await message.reply(
            text=(
                "╭━━━〔 🔗 LINK INTERCEPTED 🔗 〕━━━╮\n"
                f"┃ SOURCE : {source.upper()}\n"
                "┃ STATUS : ANALYZING\n"
                "╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
                "⚡ Inspecting source…"
            )
        )

        await log_event(
            client,
            title="LINK DETECTED",
            body=(
                f"SOURCE : {source}\n"
                f"URL    : {url}"
            ),
            event="link_detected",
            payload={
                "url": url,
                "source": source,
            },
            user_id=user.id,
        )

        # Temporary placeholder response (until extractors are wired)
        await status_msg.edit_text(
            text=(
                "⚠️ SOURCE QUEUED\n\n"
                f"Detected source: {source}\n"
                "Extraction engine initializing…"
            )
            )
