# bot/services/storage.py

import os
from typing import Optional, Tuple
from datetime import datetime

from pyrogram import Client
from pyrogram.types import Message

from bot.config import STORAGE_CHANNEL_ID
from bot.database.db import db
from bot.utils.identity import generate_fingerprint, generate_secure_key
from bot.utils.logger import log_event

# Local storage directory
LOCAL_STORAGE_DIR = "storage"


def _ensure_storage_dir():
    if not os.path.exists(LOCAL_STORAGE_DIR):
        os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)


def _local_path(file_key: str, file_name: str) -> str:
    return os.path.join(LOCAL_STORAGE_DIR, f"{file_key}_{file_name}")


def _find_existing_by_fingerprint(fingerprint: str) -> Optional[dict]:
    """
    Find existing file entry by content fingerprint.
    """
    return db.files.find_one(
        {
            "content_fingerprint": fingerprint,
            "status": {"$ne": "nuked"},
        }
    )


async def store_telegram_file(
    app: Client,
    *,
    source_message: Message,
) -> Tuple[str, dict]:
    """
    Store a Telegram-uploaded file:
    - Detect duplicate via fingerprint
    - Save locally
    - Upload to STORAGE_CHANNEL
    - Save DB record

    Returns:
        (file_key, file_doc)
    """
    _ensure_storage_dir()

    tg_file = (
        source_message.document
        or source_message.video
        or source_message.audio
    )

    if not tg_file:
        raise ValueError("No supported Telegram file found")

    file_name = tg_file.file_name or "file.bin"
    file_size = tg_file.file_size
    file_unique_id = tg_file.file_unique_id

    # Generate fingerprint
    fingerprint = generate_fingerprint(file_unique_id=file_unique_id)

    # Duplicate check (DB-first)
    existing = _find_existing_by_fingerprint(fingerprint)
    if existing:
        return existing["file_key"], existing

    # New file → generate key
    file_key = generate_secure_key(fingerprint=fingerprint)

    # Download locally
    local_file = _local_path(file_key, file_name)
    await source_message.download(file_name=local_file)

    # Upload to STORAGE_CHANNEL
    sent = await app.send_document(
        STORAGE_CHANNEL_ID,
        document=local_file,
        caption=f"🔑 {file_key}\n📁 {file_name}",
    )

    # Build DB document
    file_doc = {
        "file_key": file_key,
        "file_name": file_name,
        "file_size": file_size,
        "content_fingerprint": fingerprint,
        "source": "telegram",
        "storage_message_id": sent.id,
        "storage_chat_id": STORAGE_CHANNEL_ID,
        "user_id": source_message.from_user.id,
        "username": source_message.from_user.username,
        "created_at": datetime.utcnow(),
        "status": "active",
        "access_count": 0,
        "last_access": None,
    }

    db.files.insert_one(file_doc)

    # Log
    await log_event(
        app,
        title="FILE STORED",
        body=(
            f"FILE : {file_name}\n"
            f"KEY  : `{file_key}`\n"
            f"SIZE : {file_size} bytes"
        ),
        event="file_stored",
        payload={
            "file_key": file_key,
            "file_name": file_name,
            "size": file_size,
            "source": "telegram",
        },
        user_id=source_message.from_user.id,
        file_key=file_key,
    )

    return file_key, file_doc


async def fetch_from_storage(
    app: Client,
    *,
    file_key: str,
) -> Optional[Message]:
    """
    Fetch archived file message from STORAGE_CHANNEL using DB reference.
    """
    doc = db.files.find_one(
        {
            "file_key": file_key,
            "status": {"$ne": "nuked"},
        }
    )
    if not doc:
        return None

    try:
        return await app.get_messages(
            chat_id=doc["storage_chat_id"],
            message_ids=doc["storage_message_id"],
        )
    except Exception:
        return None


def mark_access(file_key: str):
    """
    Update access stats for a file.
    """
    db.files.update_one(
        {"file_key": file_key},
        {
            "$inc": {"access_count": 1},
            "$set": {"last_access": datetime.utcnow()},
        },
    )


def nuke_file(file_key: str):
    """
    Mark file as nuked (ADMIN action).
    Actual TG deletion handled elsewhere if needed.
    """
    db.files.update_one(
        {"file_key": file_key},
        {"$set": {"status": "nuked"}},
  )
