import os
import threading
import telebot

from flask import Flask, jsonify

from config import BOT_TOKEN
from downloader import download_media


bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

app = Flask(__name__)


@app.route("/")
def home():
    return "All Saver Telegram Bot is running!"


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 <b>All Saver Bot</b> में आपका स्वागत है!\n\n"
        "पहले आपको हमारे Telegram channel को join करना होगा।"
    )


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()

    if not url.startswith(("http://", "https://")):
        bot.reply_to(
            message,
            "❌ कृपया Instagram, Facebook, X या YouTube का valid link भेजें।"
        )
        return

    msg = bot.reply_to(
        message,
        "⏳ <b>Processing...</b>\n\nआपके link को check किया जा रहा है।"
    )

    try:
        file_path, media_type = download_media(url)

        if not file_path:
            bot.edit_message_text(
                "❌ इस link से media download नहीं हो पाया।",
                message.chat.id,
                msg.message_id
            )
            return

        with open(file_path, "rb") as media:
            if media_type == "video":
                bot.send_video(
                    message.chat.id,
                    media,
                    caption="✅ Download complete!"
                )
            else:
                bot.send_document(
                    message.chat.id,
                    media,
                    caption="✅ Download complete!"
                )

    except Exception as e:
        bot.edit_message_text(
            f"❌ Download failed.\n\n<code>{str(e)[:500]}</code>",
            message.chat.id,
            msg.message_id
        )


def run_bot():
    print("Telegram bot started...")
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
