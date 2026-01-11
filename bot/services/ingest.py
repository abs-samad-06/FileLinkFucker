# bot/services/ingest.py

import os
import aiohttp
from typing import Dict, Tuple
from datetime import datetime

from pyrogram import Client
from pyrogram.types import Message

from bot.database.db import db
from bot.config import STORAGE_CHANNEL_ID
from bot.services.storage import (
    _ensure_storage_dir,
    _local_path,
)
from bot.utils.identity import generate_fingerprint, generate_secure_key
from bot.utils.logger import log_event


# ============================================================
# INTERNAL: DOWNLOAD URL → LOCAL
# ============================================================

async def _download_to_local(url: str, dest: str) -> int:
    bytes_written = 0
    timeout = aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, allow_redirects=True) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as f:
                async for chunk in resp.content.iter_chunked(1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        bytes_written += len(chunk)
    return bytes_written


# ============================================================
# 🔥 TELEGRAM FILE INGEST (DIRECT USER FILE)
# ============================================================

async def ingest_telegram_file(
    *,
    app: Client,
    message: Message,
    user_id: int,
    username: str | None,
) -> Tuple[str, Dict]:
    """
    Ingest a Telegram-uploaded file/video into system.
    """

    if not (message.document or message.video):
        raise RuntimeError("NO TELEGRAM FILE FOUND")

    media = message.document or message.video
    file_name = getattr(media, "file_name", "video.mp4")
    file_size = media.file_size

    _ensure_storage_dir()

    # ----- FINGERPRINT (TG MESSAGE BASED) -----
    base = f"tg:{message.chat.id}:{message.id}"
    fingerprint = generate_fingerprint(source_url=base)

    existing = db.files.find_one(
        {"content_fingerprint": fingerprint, "status": {"$ne": "nuked"}}
    )
    if existing:
        return existing["file_key"], existing

    # ----- FILE KEY -----
    file_key = generate_secure_key(fingerprint=fingerprint)
    local_file = _local_path(file_key, file_name)

    # ----- DOWNLOAD FROM TELEGRAM -----
    await message.download(file_name=local_file)

    # ----- UPLOAD TO STORAGE CHANNEL -----
    sent_msg = await app.send_document(
        STORAGE_CHANNEL_ID,
        document=local_file,
        caption=f"🔑 {file_key}\n📁 {file_name}",
    )

    # ----- DB RECORD -----
    file_doc = {
        "file_key": file_key,
        "file_name": file_name,
        "file_size": file_size,
        "content_fingerprint": fingerprint,
        "source": "telegram",
        "storage_chat_id": STORAGE_CHANNEL_ID,
        "storage_message_id": sent_msg.id,
        "user_id": user_id,
        "username": username,
        "created_at": datetime.utcnow(),
        "status": "active",
        "access_count": 0,
        "last_access": None,
    }

    db.files.insert_one(file_doc)

    await log_event(
        app,
        title="TELEGRAM FILE INGESTED",
        body=(
            f"FILE : {file_name}\n"
            f"KEY  : `{file_key}`\n"
            f"SIZE : {file_size}"
        ),
        event="telegram_ingest_complete",
        payload={"file_key": file_key},
        user_id=user_id,
        file_key=file_key,
    )

    return file_key, file_doc


# ============================================================
# 🔗 EXTRACTED / LINK FILE INGEST (EXISTING LOGIC)
# ============================================================

async def ingest_extracted_file(
    *,
    app: Client,
    file_desc: Dict,
    user_id: int,
    username: str,
) -> Tuple[str, Dict]:
    """
    Ingest a single extracted file descriptor into the system.
    """

    _ensure_storage_dir()

    # ----- FINGERPRINT -----
    fingerprint = generate_fingerprint(
        source_url=file_desc.get("download_url", "")
    )

    existing = db.files.find_one(
        {"content_fingerprint": fingerprint, "status": {"$ne": "nuked"}}
    )
    if existing:
        return existing["file_key"], existing

    file_key = generate_secure_key(fingerprint=fingerprint)
    file_name = file_desc.get("name") or "file.bin"
    local_file = _local_path(file_key, file_name)

    # ----- DOWNLOAD -----
    bytes_written = await _download_to_local(
        file_desc["download_url"], local_file
    )
    file_size = file_desc.get("size") or bytes_written

    # ----- UPLOAD -----
    sent_msg = await app.send_document(
        STORAGE_CHANNEL_ID,
        document=local_file,
        caption=f"🔑 {file_key}\n📁 {file_name}",
    )

    file_doc = {
        "file_key": file_key,
        "file_name": file_name,
        "file_size": file_size,
        "content_fingerprint": fingerprint,
        "source": "direct",
        "storage_chat_id": STORAGE_CHANNEL_ID,
        "storage_message_id": sent_msg.id,
        "user_id": user_id,
        "username": username,
        "created_at": datetime.utcnow(),
        "status": "active",
        "access_count": 0,
        "last_access": None,
    }

    db.files.insert_one(file_doc)

    await log_event(
        app,
        title="LINK FILE INGESTED",
        body=(
            f"FILE : {file_name}\n"
            f"KEY  : `{file_key}`\n"
            f"SIZE : {file_size}"
        ),
        event="link_ingest_complete",
        payload={"file_key": file_key},
        user_id=user_id,
        file_key=file_key,
    )

    return file_key, file_doc
