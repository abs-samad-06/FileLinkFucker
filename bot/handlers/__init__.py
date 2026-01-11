# bot/handlers/__init__.py

"""
Handlers package
----------------
All Telegram handlers are registered from here.
"""

from pyrogram import Client


def register_all(app: Client) -> None:
    """
    Register all handlers with the bot client.
    Import handlers here to avoid circular imports.
    """

    # NOTE:
    # Actual handler imports will be added progressively.
    # Example (later):
    # from bot.handlers.start import register as start_register
    # start_register(app)

    pass
