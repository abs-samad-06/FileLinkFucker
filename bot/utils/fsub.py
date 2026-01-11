# bot/utils/fsub.py

from typing import List
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

from bot.config import FSUB_CHANNELS


async def check_fsub(app: Client, user_id: int) -> bool:
    """
    Check whether a user has joined all required FSUB channels.
    Returns True if joined all, else False.
    """
    if not FSUB_CHANNELS:
        return True

    for channel in FSUB_CHANNELS:
        try:
            member = await app.get_chat_member(channel, user_id)
            if member.status in ("left", "kicked"):
                return False
        except UserNotParticipant:
            return False
        except Exception:
            # Any unexpected error → treat as not joined (safe default)
            return False

    return True


def fsub_prompt() -> InlineKeyboardMarkup:
    """
    Generate FSUB join + verify buttons.
    """
    buttons: List[List[InlineKeyboardButton]] = []

    # Join buttons
    for channel in FSUB_CHANNELS:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"🔥 Join {channel}",
                    url=f"https://t.me/{channel.lstrip('@')}"
                )
            ]
        )

    # Verify button
    buttons.append(
        [
            InlineKeyboardButton(
                text="🔓 VERIFY ACCESS",
                callback_data="fsub_verify"
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)
