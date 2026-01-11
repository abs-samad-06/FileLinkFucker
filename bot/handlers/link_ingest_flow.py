# bot/handlers/link_ingest_flow.py

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.services.extractors.router import extract_url
from bot.services.ingest import ingest_extracted_file
from bot.handlers.password_prompt import password_prompt_buttons
from bot.utils.logger import log_event


def register(app: Client) -> None:
    """
    Wire extracted link content into ingestion + password flow.
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
    async def link_ingest_flow_handler(client: Client, message: Message):
        text = message.text or ""
        if "http://" not in text and "https://" not in text:
            return

        user = message.from_user

        # Extract first URL
        url = next(
            (
                w for w in text.split()
                if w.startswith("http://") or w.startswith("https://")
            ),
            None
        )
        if not url:
            return

        status = await message.reply(
            "⚡ LINK VERIFIED\nIngesting into system..."
        )

        # -------- EXTRACT --------
        result = await extract_url(url=url, app=client)
        if not result.success or not result.files:
            await status.edit_text(
                f"❌ INGEST FAILED\nReason: {result.error or 'Unknown'}"
            )
            return

        # TEMP: handle first file (batch later)
        f = result.files[0]

        try:
            file_key, _ = await ingest_extracted_file(
                app=client,
                file_desc=f,
                user_id=user.id,
                username=user.username,
            )
        except Exception as e:
            await status.edit_text(
                "❌ SYSTEM ERROR\nUnable to ingest file."
            )
            await log_event(
                client,
                title="INGEST ERROR",
                body=str(e),
                event="ingest_error",
                payload={"url": url, "error": str(e)},
                user_id=user.id,
            )
            return

        # -------- PASSWORD PROMPT --------
        await status.edit_text(
            text=(
                "🔐 PROTECT THIS FILE?\n\n"
                f"FILE KEY : `{file_key}`\n\n"
                "Do you want to set a password?"
            ),
            reply_markup=password_prompt_buttons(file_key),
        )

        await log_event(
            client,
            title="LINK INGESTED",
            body=f"FILE KEY : `{file_key}`",
            event="link_ingested",
            payload={"url": url, "file_key": file_key},
            user_id=user.id,
            file_key=file_key,
        )
