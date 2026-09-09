import os


BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL_USERNAME = os.getenv(
    "CHANNEL_USERNAME",
    "@nrtecno2"
)

CHANNEL_URL = os.getenv(
    "CHANNEL_URL",
    "https://t.me/nrtecno2"
)


if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN environment variable is not set."
    )
