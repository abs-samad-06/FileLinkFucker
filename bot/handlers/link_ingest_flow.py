# bot/handlers/file_ingest_flow.py

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot.services.ingest import ingest_telegram_file
from bot.services.links import build_links
from bot.handlers.password_prompt import password_prompt_buttons
from bot.utils.logger import log_event


def _final_links_text(file_key: str, file_name: str, file_size: int) -> str:
    links = build_links(file_key)

    size_mb = round(file_size / (1024 * 1024), 2)

    return (
        "╭━━━〔 ⚡ FILE BREACHED ⚡ 〕━━━╮\n"
        "┃  ACCESS GRANTED ✔\n"
        "┃  STATUS : LIVE\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        "📁 FILE NAME ::\n"
        f"{file_name}\n\n"
        "📦 FILE SIZE ::\n"
        f"{size_mb} MB\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "🔗 YOUR LINKS\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        f"🖥️ STREAM ::\n➤ {links['stream']}\n\n"
        f"⬇️ DOWNLOAD ::\n➤ {links['download']}\n\n"
        f"📡 TG FILE ::\n➤ {links['telegram']}\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "🛡️ SECURITY NOTE\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ LINK WON'T EXPIRE TILL I DELETE\n"
    )


def _action_buttons(file_key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🖥️ STREAM", url=f"https://example.com/watch/{file_key}"),
                InlineKeyboardButton("⬇️ DOWNLOAD", url=f"https://example.com/download/{file_key}"),
            ],
            [
                InlineKeyboardButton("📡 GET FILE", url=f"https://t.me/your_bot?start=get_{file_key}"),
            ],
            [
                InlineKeyboardButton("🗑️ DELETE FILE", callback_data=f"delete:{file_key}"),
            ],
        ]
    )


def register(app: Client) -> None:
    """
    Handle direct Telegram file uploads and convert to links.
    """

    @app.on_message(
        filters.document | filters.video | filters.audio
    )
    async def file_ingest_handler(client: Client, message: Message):
        user = message.from_user
        media = message.document or message.video or message.audio

        status = await message.reply(
            "⚡ FILE INTERCEPTED\nProcessing..."
        )

        try:
            file_key, meta = await ingest_telegram_file(
                app=client,
                message=message,
                user_id=user.id,
                username=user.username,
            )
        except Exception as e:
            await status.edit_text("❌ SYSTEM ERROR\nFile ingestion failed.")
            await log_event(
                client,
                title="FILE INGEST ERROR",
                body=str(e),
                event="file_ingest_error",
                payload={"error": str(e)},
                user_id=user.id,
            )
            return

        # PASSWORD PROMPT
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
            title="FILE INGESTED",
            body=f"FILE KEY : `{file_key}`",
            event="file_ingested",
            payload={"file_key": file_key},
            user_id=user.id,
            file_key=file_key,
        )

        # FINAL LINKS (NO PASSWORD CASE HANDLED IN flow_wiring)
        final_text = _final_links_text(
            file_key=file_key,
            file_name=media.file_name or "Unknown",
            file_size=media.file_size or 0,
        )

        await message.reply(
            text=final_text,
            reply_markup=_action_buttons(file_key),
            disable_web_page_preview=True,
                )
