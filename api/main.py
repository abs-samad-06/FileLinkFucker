# api/main.py

import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from bot.config import API_HOST, API_PORT
from bot.database.db import db
from bot.services.storage import fetch_from_storage
from bot.utils.passwords import is_protected, verify_password

app = FastAPI(title="FileLinkFucker API")

# CORS (optional but safe)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_file_doc(file_key: str) -> dict:
    doc = db.files.find_one(
        {"file_key": file_key, "status": {"$ne": "nuked"}}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="FILE NOT FOUND")
    return doc


def _password_gate(file_key: str, password: Optional[str]):
    if is_protected(file_key):
        if not password:
            raise HTTPException(
                status_code=401,
                detail="PASSWORD REQUIRED",
            )
        if not verify_password(file_key, password):
            raise HTTPException(
                status_code=403,
                detail="INVALID PASSWORD",
            )


@app.get("/d/{file_key}")
async def download_file(
    file_key: str,
    password: Optional[str] = Query(None),
):
    """
    Download endpoint.
    """
    _password_gate(file_key, password)

    doc = _get_file_doc(file_key)

    # Try local storage first
    local_path = os.path.join(
        "storage", f"{file_key}_{doc['file_name']}"
    )
    if os.path.exists(local_path):
        return FileResponse(
            local_path,
            filename=doc["file_name"],
        )

    # Fallback: redirect to TG archive
    tg_link = f"https://t.me/c/{str(doc['storage_chat_id']).replace('-100', '')}/{doc['storage_message_id']}"
    return RedirectResponse(tg_link)


@app.get("/s/{file_key}")
async def stream_file(
    file_key: str,
    password: Optional[str] = Query(None),
):
    """
    Stream endpoint (basic file stream).
    """
    _password_gate(file_key, password)

    doc = _get_file_doc(file_key)

    local_path = os.path.join(
        "storage", f"{file_key}_{doc['file_name']}"
    )
    if not os.path.exists(local_path):
        raise HTTPException(
            status_code=404,
            detail="STREAM SOURCE NOT AVAILABLE",
        )

    def iterfile():
        with open(local_path, "rb") as f:
            while chunk := f.read(1024 * 1024):
                yield chunk

    return StreamingResponse(
        iterfile(),
        media_type="application/octet-stream",
    )


@app.get("/tg/{file_key}")
async def telegram_link(
    file_key: str,
    password: Optional[str] = Query(None),
):
    """
    Telegram mirror redirect.
    """
    _password_gate(file_key, password)

    doc = _get_file_doc(file_key)

    tg_link = f"https://t.me/c/{str(doc['storage_chat_id']).replace('-100', '')}/{doc['storage_message_id']}"
    return RedirectResponse(tg_link)


# Entrypoint for uvicorn
def run():
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=False,
  )
