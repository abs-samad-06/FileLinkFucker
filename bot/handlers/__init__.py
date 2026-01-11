# bot/handlers/__init__.py

"""
Handlers package
----------------
Central registry for all Telegram handlers.
"""

from pyrogram import Client


def register_all(app: Client) -> None:
    """
    Register all handlers with the bot client.
    Import handlers here to avoid circular imports and
    to control registration order.
    """

    # START & FSUB
    from bot.handlers.start import register as start_register
    from bot.handlers.fsub_verify import register as fsub_verify_register

    # Register in order
    start_register(app)
    fsub_verify_register(app)

    # NOTE:
    # Next handlers will be added here progressively:
    # - file upload handler
    # - link detection handler
    # - password flow
    # - admin commands
