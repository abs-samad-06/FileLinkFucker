# bot/main.py

import signal
import sys
from pyrogram import idle

from bot.client import create_bot
from bot.config import DEBUG


def _graceful_exit(signum, frame):
    print(f"[SYSTEM] Received signal {signum}. Shutting down safely...")
    sys.exit(0)


def main():
    app = create_bot()

    # Signal handling for clean shutdown
    signal.signal(signal.SIGINT, _graceful_exit)
    signal.signal(signal.SIGTERM, _graceful_exit)

    # Start bot
    app.start()

    if DEBUG:
        print("[SYSTEM] FileLinkFucker is ONLINE (DEBUG MODE)")
    else:
        print("[SYSTEM] FileLinkFucker is ONLINE")

    # Keep bot alive
    idle()

    # Stop bot
    app.stop()
    print("[SYSTEM] FileLinkFucker is OFFLINE")


if __name__ == "__main__":
    main()
