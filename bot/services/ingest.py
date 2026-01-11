# bot/services/ingest.py

import os
import aiohttp
from typing import Dict, Tuple
from datetime import datetime

from pyrogram import Client

from bot.database.db import db
from bot.config import STORAGE_CHANNEL_ID
from bot.services.storage import (
    _ensure_storage_dir,
    _local_path,
)
from bot.utils.identity import generate_fingerprint, generate_secure_key
from bot.utils.logger import log_event


async def _download_to_local(url: str, dest: str) -> int:
    """
    Download a URL to local file. Returns bytes written.
    """
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


async def ingest_extracted_file(
    *,
    app: Client,
    file_desc: Dict,
    user_id: int,
    username: str,
) -> Tuple[str, Dict]:
    """
    Ingest a single extracted file descriptor into the system.

    file_desc expected keys:
    - name
    - size (optional)
    - download_url (optional)
    - telegram {chat_id, message_id} (optional)

    Returns:
        (file_key, file_doc)
    """
    _ensure_storage_dir()

    # ----- FINGERPRINT (DB-FIRST) -----
    if "telegram" in file_desc:
        # Telegram-sourced descriptor
        base = f"tg:{file_desc['telegram']['chat_id']}:{file_desc['telegram']['message_id']}"
        fingerprint = generate_fingerprint(source_url=base)
    else:
        # Direct URL or other sources
        fingerprint = generate_fingerprint(source_url=file_desc.get("download_url", ""))

    existing = db.files.find_one(
        {"content_fingerprint": fingerprint, "status": {"$ne": "nuked"}}
    )
    if existing:
        return existing["file_key"], existing

    # ----- NEW FILE -----
    file_key = generate_secure_key(fingerprint=fingerprint)
    file_name = file_desc.get("name") or "file.bin"
    local_file = _local_path(file_key, file_name)

    # ----- ACQUIRE FILE -----
    sent_msg = None
    if "telegram" in file_desc:
        # Fetch and re-upload from Telegram
        chat_id = file_desc["telegram"]["chat_id"]
        msg_id = file_desc["telegram"]["message_id"]
        src = await app.get_messages(chat_id, msg_id)
        if not src:
            raise RuntimeError("SOURCE MESSAGE NOT FOUND")

        # Download locally first (safe)
        await src.download(file_name=local_file)

        # Upload to STORAGE_CHANNEL
        sent_msg = await app.send_document(
            STORAGE_CHANNEL_ID,
            document=local_file,
            caption=f"🔑 {file_key}\n📁 {file_name}",
        )
        file_size = src.document.file_size if src.document else file_desc.get("size")

    else:
        # Direct URL download
        bytes_written = await _download_to_local(
            file_desc["download_url"], local_file
        )
        file_size = file_desc.get("size") or bytes_written

        # Upload to STORAGE_CHANNEL
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
        "source": "telegram" if "telegram" in file_desc else "direct",
        "storage_chat_id": STORAGE_CHANNEL_ID,
        "storage_message_id": sent_msg.id if sent_msg else None,
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
        title="INGEST COMPLETE",
        body=(
            f"FILE : {file_name}\n"
            f"KEY  : `{file_key}`\n"
            f"SIZE : {file_size}"
        ),
        event="ingest_complete",
        payload={"file_key": file_key, "file_name": file_name, "size": file_size},
        user_id=user_id,
        file_key=file_key,
    )

    return file_key, file_doc
