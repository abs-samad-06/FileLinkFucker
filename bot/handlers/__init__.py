# bot/handlers/__init__.py

"""
Handlers package
----------------
Central registry for all Telegram handlers.
Order matters.
"""

from pyrogram import Client


def register_all(app: Client) -> None:
    """
    Register all handlers with the bot client.
    """

    # ─────────── BASIC / ACCESS ───────────
    from bot.handlers.start import register as start_register
    from bot.handlers.help_about import register as help_about_register
    from bot.handlers.fsub_verify import register as fsub_verify_register

    # ─────────── FILE UPLOAD FLOW ───────────
    from bot.handlers.upload import register as upload_register
    from bot.handlers.password_prompt import register as password_prompt_register
    from bot.handlers.password_capture import register as password_capture_register
    from bot.handlers.flow_wiring import register as flow_wiring_register

    # ─────────── LINK FLOW ───────────
    from bot.handlers.link_detect import register as link_detect_register
    from bot.handlers.link_process import register as link_process_register
    from bot.handlers.link_ingest_flow import register as link_ingest_flow_register

    # ─────────── ADMIN ───────────
    from bot.handlers.admin import register as admin_register

    # -------- REGISTER IN ORDER --------
    start_register(app)
    help_about_register(app)
    fsub_verify_register(app)

    upload_register(app)
    password_prompt_register(app)
    password_capture_register(app)
    flow_wiring_register(app)

    link_detect_register(app)
    link_process_register(app)
    link_ingest_flow_register(app)

    admin_register(app)
