# bot/handlers/link_ingest_flow.py

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.services.extractors.router import extract_url
from bot.services.ingest import ingest_extracted_file
from bot.handlers.password_prompt import password_prompt_buttons
from bot.utils.logger import log_event


def register(app: Client) -> None:
    """
    MASTER INGEST FLOW
    Handles:
    - Links (extract → ingest)
    - Telegram files (direct ingest)
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
        | filters.document
        | filters.video
        | filters.audio
    )
    async def ingest_flow_handler(client: Client, message: Message):
        user = message.from_user

        # ===============================
        # CASE 1: TELEGRAM FILE UPLOAD
        # ===============================
        if message.document or message.video or message.audio:
            media = message.document or message.video or message.audio

            status = await message.reply(
                "⚡ FILE INTERCEPTED\nIngesting into system..."
            )

            # Convert Telegram file → extracted-like dict
            file_desc = {
                "file_id": media.file_id,
                "file_name": media.file_name or "unknown",
                "file_size": media.file_size,
                "mime_type": media.mime_type,
                "source": "telegram",
            }

            try:
                file_key, _ = await ingest_extracted_file(
                    app=client,
                    file_desc=file_desc,
                    user_id=user.id,
                    username=user.username,
                )
            except Exception as e:
                await status.edit_text("❌ SYSTEM ERROR\nFile ingest failed.")
                await log_event(
                    client,
                    title="FILE INGEST ERROR",
                    body=str(e),
                    event="file_ingest_error",
                    payload={"error": str(e)},
                    user_id=user.id,
                )
                return

            await status.edit_text(
                text=(
                    "🔐 PROTECT THIS FILE?\n\n"
                    f"FILE KEY : `{file_key}`\n\n"
                    "Do you want to set a password?"
                ),
                reply_markup=password_prompt_buttons(file_key),
            )
            return

        # ===============================
        # CASE 2: LINK INGEST FLOW
        # ===============================
        text = message.text or ""
        if "http://" not in text and "https://" not in text:
            return

        url = next(
            (w for w in text.split() if w.startswith("http://") or w.startswith("https://")),
            None
        )
        if not url:
            return

        status = await message.reply("⚡ LINK VERIFIED\nExtracting content...")

        result = await extract_url(url=url, app=client)
        if not result.success or not result.files:
            await status.edit_text(
                f"❌ EXTRACTION FAILED\nReason: {result.error or 'Unknown'}"
            )
            return

        file_desc = result.files[0]

        try:
            file_key, _ = await ingest_extracted_file(
                app=client,
                file_desc=file_desc,
                user_id=user.id,
                username=user.username,
            )
        except Exception as e:
            await status.edit_text("❌ SYSTEM ERROR\nUnable to ingest file.")
            await log_event(
                client,
                title="INGEST ERROR",
                body=str(e),
                event="ingest_error",
                payload={"url": url, "error": str(e)},
                user_id=user.id,
            )
            return

        await status.edit_text(
            text=(
                "🔐 PROTECT THIS FILE?\n\n"
                f"FILE KEY : `{file_key}`\n\n"
                "Do you want to set a password?"
            ),
            reply_markup=password_prompt_buttons(file_key),
            )
