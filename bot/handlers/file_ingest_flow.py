# bot/handlers/file_ingest_flow.py

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.services.ingest import ingest_telegram_file
from bot.services.links import build_links
from bot.handlers.password_prompt import password_prompt_buttons
from bot.utils.logger import log_event


def _links_text(file_key: str) -> str:
    links = build_links(file_key)
    return (
        "╭━━━〔 ⚡ YOUR LINK GENERATED ⚡ 〕━━━╮\n"
        "┃  STATUS : ACTIVE\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "🔗 YOUR LINKS\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        f"🖥️ STREAM :\n{links['stream']}\n\n"
        f"⬇️ DOWNLOAD :\n{links['download']}\n\n"
        f"📡 GET FILE :\n{links['telegram']}\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ NOTE : LINK WON'T EXPIRE TILL I DELETE\n"
    )


def register(app: Client) -> None:
    """
    Handle Telegram file → ingest → password → links
    """

    @app.on_message(filters.document | filters.video)
    async def telegram_file_ingest_handler(client: Client, message: Message):
        user = message.from_user

        status = await message.reply(
            "⚡ FILE INTERCEPTED\nProcessing..."
        )

        try:
            file_key, _ = await ingest_telegram_file(
                app=client,
                message=message,
                user_id=user.id,
                username=user.username,
            )
        except Exception as e:
            await status.edit_text(
                "❌ FAILED TO PROCESS FILE\nTry again later."
            )
            await log_event(
                client,
                title="TELEGRAM INGEST FAILED",
                body=str(e),
                event="telegram_ingest_failed",
                payload={"error": str(e)},
                user_id=user.id,
            )
            return

        # Ask for password
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
            title="TELEGRAM FILE INGESTED",
            body=f"FILE KEY : `{file_key}`",
            event="telegram_ingested",
            payload={"file_key": file_key},
            user_id=user.id,
            file_key=file_key,
        )

    # ---------- NO PASSWORD → DIRECT LINKS ----------
    @app.on_callback_query(filters.regex(r"^pwd_no:"))
    async def _no_password_send_links(client, cq):
        file_key = cq.data.split(":", 1)[1]
        await cq.answer()
        await cq.message.edit_text(_links_text(file_key))

    # ---------- PASSWORD SET → SEND LINKS ----------
    @app.on_message(filters.text & filters.reply)
    async def _after_password_send_links(client: Client, message: Message):
        text = message.reply_to_message.text or ""
        if "PASSWORD SET SUCCESSFULLY" not in text:
            return

        if "`" not in text:
            return

        file_key = text.split("`")[1].strip()
        await message.reply(_links_text(file_key))
