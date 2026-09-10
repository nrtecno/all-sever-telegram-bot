import os


SECRET_DIR = "/etc/secrets"


def read_secret(name, default=None):
    path = os.path.join(SECRET_DIR, name)

    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as file:
            value = file.read().strip()

        if value:
            return value

    # Fallback: normal Render Environment Variables
    value = os.getenv(name)

    if value:
        return value.strip()

    return default


BOT_TOKEN = read_secret("BOT_TOKEN")

CHANNEL_USERNAME = read_secret(
    "CHANNEL_USERNAME",
    "@nrtecno2"
)

CHANNEL_URL = read_secret(
    "CHANNEL_URL",
    "https://t.me/nrtecno2"
)


if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN secret is not set."
    )
