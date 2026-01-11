# bot/handlers/link_process.py

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.config import FSUB_CHANNELS
from bot.utils.fsub import check_fsub, fsub_prompt
from bot.utils.logger import log_event
from bot.services.extractors.router import analyze_url, extract_url


def register(app: Client) -> None:
    """
    Register link processing handler.
    This works AFTER link detection and performs:
    analyze -> extract
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
    async def link_process_handler(client: Client, message: Message):
        text = message.text or ""
        if "http://" not in text and "https://" not in text:
            return

        user = message.from_user

        # HARD FSUB GATE
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

        # Extract first URL only (batch links handled later)
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
            "🔍 ANALYZING SOURCE...\nPlease wait."
        )

        # -------- ANALYZE --------
        try:
            analysis = await analyze_url(url=url, app=client)
        except Exception as e:
            await status.edit_text(
                "❌ ANALYSIS FAILED\nTry again later."
            )
            await log_event(
                client,
                title="ANALYZE ERROR",
                body=str(e),
                event="analyze_error",
                payload={"url": url, "error": str(e)},
                user_id=user.id,
            )
            return

        if analysis.get("file_count", 0) == 0:
            reason = analysis.get("error", "Unsupported or private link")
            await status.edit_text(
                f"❌ EXTRACTION BLOCKED\nReason: {reason}"
            )
            await log_event(
                client,
                title="ANALYZE BLOCKED",
                body=f"URL : {url}\nReason : {reason}",
                event="analyze_blocked",
                payload={"url": url, "reason": reason},
                user_id=user.id,
            )
            return

        # -------- EXTRACT --------
        await status.edit_text(
            "⚡ SOURCE VERIFIED\nExtracting content..."
        )

        result = await extract_url(url=url, app=client)

        if not result.success:
            await status.edit_text(
                f"❌ EXTRACTION FAILED\nReason: {result.error}"
            )
            await log_event(
                client,
                title="EXTRACTION FAILED",
                body=f"URL : {url}\nReason : {result.error}",
                event="extract_failed",
                payload={"url": url, "error": result.error},
                user_id=user.id,
            )
            return

        # -------- SUCCESS (TEMP: single-file only) --------
        files = result.files
        if not files:
            await status.edit_text("❌ NO FILES FOUND")
            return

        f = files[0]
        await status.edit_text(
            "⚡ FILE READY FOR INGESTION\n"
            f"📁 {f.get('name')}\n"
            "Processing into system..."
        )

        # NOTE:
        # Next step will ingest file + password + links
