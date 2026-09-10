import os
import shutil
import threading
import time

import telebot
from flask import Flask, jsonify
from telebot import types

from config import BOT_TOKEN, CHANNEL_USERNAME, CHANNEL_URL
from downloader import download_media


# =========================
# TELEGRAM BOT
# =========================

bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML"
)

app = Flask(__name__)


# =========================
# FLASK WEB APP
# =========================

@app.route("/")
def home():
    return "All Saver Telegram Bot is running!"


@app.route("/health")
def health():
    return jsonify({
        "status": "ok"
    })


# =========================
# CHANNEL VERIFICATION
# =========================

def is_channel_member(user_id):
    try:
        member = bot.get_chat_member(
            CHANNEL_USERNAME,
            user_id
        )

        return member.status in (
            "member",
            "administrator",
            "creator"
        )

    except Exception as error:
        print(
            f"Channel verification error: {error}",
            flush=True
        )

        return False


def send_join_message(chat_id):

    keyboard = types.InlineKeyboardMarkup(
        row_width=1
    )

    join_button = types.InlineKeyboardButton(
        "📢 Join Channel",
        url=CHANNEL_URL
    )

    verify_button = types.InlineKeyboardButton(
        "✅ Verify",
        callback_data="verify_channel"
    )

    keyboard.add(
        join_button,
        verify_button
    )

    bot.send_message(
        chat_id,
        "🔐 <b>Verification Required</b>\n\n"
        "Bot use karne ke liye pehle hamara "
        "Telegram channel <b>@nr_hackz</b> join karein.\n\n"
        "Channel join karne ke baad "
        "<b>Verify</b> button dabayein.",
        reply_markup=keyboard
    )


def send_url_request(chat_id):

    bot.send_message(
        chat_id,
        "✅ <b>Verification successful!</b>\n\n"
        "Ab Instagram, Facebook, X/Twitter "
        "ya YouTube ka public link bhejiye.\n\n"
        "Example:\n"
        "<code>https://www.youtube.com/watch?v=...</code>"
    )


# =========================
# /START COMMAND
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    user_id = message.from_user.id

    if is_channel_member(user_id):
        send_url_request(message.chat.id)

    else:
        send_join_message(message.chat.id)


# =========================
# VERIFY BUTTON
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "verify_channel"
)
def verify_channel(call):

    user_id = call.from_user.id

    if is_channel_member(user_id):

        bot.answer_callback_query(
            call.id,
            "✅ Verification successful!"
        )

        send_url_request(
            call.message.chat.id
        )

    else:

        bot.answer_callback_query(
            call.id,
            "❌ Pehle channel join karein.",
            show_alert=True
        )


# =========================
# MEDIA DOWNLOAD
# =========================

@bot.message_handler(
    func=lambda message: True
)
def handle_message(message):

    # Check channel membership
    if not is_channel_member(
        message.from_user.id
    ):

        send_join_message(
            message.chat.id
        )

        return

    # Check text
    if not message.text:

        bot.reply_to(
            message,
            "❌ Please Instagram, Facebook, "
            "X/Twitter ya YouTube ka link bhejiye."
        )

        return

    url = message.text.strip()

    # Check URL
    if not url.startswith(
        ("http://", "https://")
    ):

        bot.reply_to(
            message,
            "❌ Please ek valid URL bhejiye."
        )

        return

    processing_message = bot.reply_to(
        message,
        "⏳ <b>Processing...</b>\n\n"
        "Media download kiya ja raha hai."
    )

    temp_dir = None

    try:

        # Download media
        result = download_media(url)

        file_path = result[0]
        media_type = result[1]
        temp_dir = result[2]

        if not file_path:
            raise FileNotFoundError(
                "Downloaded file nahi mila."
            )

        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                "Downloaded file exist nahi karta."
            )

        # Upload message
        bot.edit_message_text(
            "📤 <b>Uploading...</b>\n\n"
            "Media Telegram par bheja ja raha hai.",
            message.chat.id,
            processing_message.message_id
        )

        # Send video
        if media_type == "video":

            with open(
                file_path,
                "rb"
            ) as media:

                bot.send_video(
                    message.chat.id,
                    media,
                    caption="✅ Download complete!"
                )

        # Send image
        elif media_type == "image":

            with open(
                file_path,
                "rb"
            ) as media:

                bot.send_photo(
                    message.chat.id,
                    media,
                    caption="✅ Download complete!"
                )

        # Send other files
        else:

            with open(
                file_path,
                "rb"
            ) as media:

                bot.send_document(
                    message.chat.id,
                    media,
                    caption="✅ Download complete!"
                )

        # Delete processing message
        try:

            bot.delete_message(
                message.chat.id,
                processing_message.message_id
            )

        except Exception:
            pass

    except Exception as error:

        print(
            f"Download error: {error}",
            flush=True
        )

        try:

            bot.edit_message_text(
                "❌ <b>Download failed.</b>\n\n"
                "Is link se media download nahi ho paya.\n\n"
                f"<code>{str(error)[:500]}</code>",
                message.chat.id,
                processing_message.message_id
            )

        except Exception:

            bot.send_message(
                message.chat.id,
                "❌ Download failed."
            )

    finally:

        # Delete temporary downloaded files
        if temp_dir and os.path.exists(
            temp_dir
        ):

            shutil.rmtree(
                temp_dir,
                ignore_errors=True
            )


# =========================
# TELEGRAM BOT RUNNER
# =========================

def start_bot():

    while True:

        try:

            print(
                "Starting Telegram bot...",
                flush=True
            )

            # Remove existing webhook
            bot.remove_webhook()

            print(
                "Telegram bot polling started.",
                flush=True
            )

            bot.infinity_polling(
                skip_pending=True,
                timeout=60,
                long_polling_timeout=60
            )

        except Exception as error:

            print(
                f"Telegram polling error: {error}",
                flush=True
            )

            print(
                "Retrying in 10 seconds...",
                flush=True
            )

            time.sleep(10)


# =========================
# START BOT THREAD
# =========================

bot_thread = threading.Thread(
    target=start_bot,
    daemon=True
)

bot_thread.start()


# =========================
# LOCAL / RENDER SERVER
# =========================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
