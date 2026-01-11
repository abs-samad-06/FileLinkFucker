# bot/utils/logger.py

from datetime import datetime
from typing import Optional

from pyrogram import Client
from pyrogram.types import Message

from bot.config import LOG_CHANNEL_ID
from bot.database.db import db


def _now_utc():
    return datetime.utcnow()


def _hacker_box(title: str, body: str) -> str:
    """
    Format logs in a hacker-style ASCII box.
    Texts will be polished at the end.
    """
    ts = _now_utc().strftime("%Y-%m-%d %H:%M:%S UTC")
    return (
        "╭━━━〔 ⚠️ " + title + " ⚠️ 〕━━━╮\n"
        f"┃ TIME   : {ts}\n"
        "┃ ACCESS : ROOT\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━╯\n"
        f"{body}"
    )


async def log_to_channel(
    app: Client,
    title: str,
    body: str,
    silent: bool = False
) -> Optional[Message]:
    """
    Send formatted log to Telegram LOG_CHANNEL.
    """
    text = _hacker_box(title, body)
    try:
        return await app.send_message(
            LOG_CHANNEL_ID,
            text,
            disable_notification=silent
        )
    except Exception:
        # Channel issues should never crash the bot
        return None


def log_to_db(
    event: str,
    payload: dict,
    user_id: Optional[int] = None,
    file_key: Optional[str] = None,
):
    """
    Persist log event to MongoDB.
    """
    doc = {
        "event": event,
        "payload": payload,
        "user_id": user_id,
        "file_key": file_key,
        "timestamp": _now_utc(),
    }
    try:
        db.logs.insert_one(doc)
    except Exception:
        # DB logging failure should not crash runtime
        pass


async def log_event(
    app: Client,
    *,
    title: str,
    body: str,
    event: str,
    payload: dict,
    user_id: Optional[int] = None,
    file_key: Optional[str] = None,
    silent: bool = False,
):
    """
    Unified logger:
    - Sends hacker-style log to Telegram channel
    - Stores structured log in MongoDB
    """
    # Channel log
    await log_to_channel(app, title, body, silent=silent)

    # DB log
    log_to_db(
        event=event,
        payload=payload,
        user_id=user_id,
        file_key=file_key,
  )
