# bot/handlers/admin.py

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.config import OWNER_ID
from bot.database.db import db
from bot.services.storage import nuke_file
from bot.utils.logger import log_event


def _is_admin(user_id: int) -> bool:
    return user_id == OWNER_ID


def register(app: Client) -> None:
    """
    Register admin-only commands.
    """

    # ─────────── STATS ───────────
    @app.on_message(filters.command("stats"))
    async def stats_handler(client: Client, message: Message):
        if not _is_admin(message.from_user.id):
            return

        total_files = db.files.count_documents({})
        active_files = db.files.count_documents({"status": "active"})
        users = db.users.count_documents({})

        text = (
            "╭━━━〔 📊 SYSTEM STATS 〕━━━╮\n"
            f"┃ USERS        : {users}\n"
            f"┃ FILES (ALL)  : {total_files}\n"
            f"┃ FILES LIVE  : {active_files}\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        )

        await message.reply(text)

    # ─────────── USER DATA ───────────
    @app.on_message(filters.command("user_data"))
    async def user_data_handler(client: Client, message: Message):
        if not _is_admin(message.from_user.id):
            return

        if len(message.command) < 2:
            await message.reply("❌ Usage: /user_data <user_id | @username>")
            return

        query = message.command[1]
        if query.startswith("@"):
            user = db.users.find_one({"username": query.lstrip("@")})
        else:
            user = db.users.find_one({"user_id": int(query)})

        if not user:
            await message.reply("❌ USER NOT FOUND")
            return

        files = list(db.files.find({"user_id": user["user_id"]}))
        file_lines = "\n".join(
            f"• `{f['file_key']}` | {f['file_name']}"
            for f in files
        ) or "No files"

        text = (
            "╭━━━〔 👤 USER DATA 〕━━━╮\n"
            f"┃ USER ID : {user['user_id']}\n"
            f"┃ USER    : @{user.get('username')}\n"
            f"┃ FILES   : {len(files)}\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
            f"{file_lines}"
        )

        await message.reply(text)

    # ─────────── DELETE SINGLE FILE ───────────
    @app.on_message(filters.command("delete"))
    async def delete_file_handler(client: Client, message: Message):
        if not _is_admin(message.from_user.id):
            return

        if len(message.command) < 2:
            await message.reply("❌ Usage: /delete <file_key>")
            return

        file_key = message.command[1]
        file = db.files.find_one({"file_key": file_key})

        if not file:
            await message.reply("❌ FILE NOT FOUND")
            return

        nuke_file(file_key)

        await message.reply(
            f"💀 FILE NUKED\nKEY : `{file_key}`"
        )

        await log_event(
            client,
            title="FILE NUKED",
            body=f"FILE KEY : `{file_key}`",
            event="file_nuked",
            payload={"file_key": file_key},
            user_id=message.from_user.id,
            file_key=file_key,
        )

    # ─────────── DELETE ALL FILES OF USER ───────────
    @app.on_message(filters.command("delfile"))
    async def delete_user_files_handler(client: Client, message: Message):
        if not _is_admin(message.from_user.id):
            return

        if len(message.command) < 2:
            await message.reply("❌ Usage: /delfile <user_id>")
            return

        user_id = int(message.command[1])
        files = db.files.find({"user_id": user_id})

        count = 0
        for f in files:
            nuke_file(f["file_key"])
            count += 1

        await message.reply(
            f"💣 USER FILES NUKED\nUSER ID : {user_id}\nFILES : {count}"
        )

        await log_event(
            client,
            title="USER FILES NUKED",
            body=f"USER ID : {user_id}\nFILES : {count}",
            event="user_files_nuked",
            payload={"user_id": user_id, "count": count},
            user_id=message.from_user.id,
      )
