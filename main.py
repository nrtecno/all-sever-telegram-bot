import os
import shutil
import threading

import telebot
from flask import Flask, jsonify
from telebot import types

from config import BOT_TOKEN, CHANNEL_USERNAME, CHANNEL_URL
from downloader import download_media


bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)


@app.route("/")
def home():
    return "All Saver Telegram Bot is running!"


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


def is_channel_member(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)

        return member.status in (
            "member",
            "administrator",
            "creator",
        )

    except Exception as error:
        print("Channel verification error:", error)
        return False


def send_join_message(chat_id):
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    join_button = types.InlineKeyboardButton(
        "📢 Join Channel",
        url=CHANNEL_URL
    )

    verify_button = types.InlineKeyboardButton(
        "✅ Verify",
        callback_data="verify_channel"
    )

    keyboard.add(join_button, verify_button)

    bot.send_message(
        chat_id,
        "🔐 <b>Verification Required</b>\n\n"
        "Bot use karne ke liye pehle hamara Telegram channel "
        "<b>@nrtecno2</b> join karein.\n\n"
        "Join karne ke baad <b>Verify</b> button dabayein.",
        reply_markup=keyboard
    )


def send_url_request(chat_id):
    bot.send_message(
        chat_id,
        "✅ <b>Verification successful!</b>\n\n"
        "Ab Instagram, Facebook, X/Twitter ya YouTube ka "
        "public link bhejiye.\n\n"
        "Example:\n"
        "<code>https://www.youtube.com/watch?v=...</code>"
    )


@bot.message_handler(commands=["start"])
def start(message):
    if is_channel_member(message.from_user.id):
        send_url_request(message.chat.id)
    else:
        send_join_message(message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "verify_channel")
def verify_channel(call):
    if is_channel_member(call.from_user.id):
        bot.answer_callback_query(
            call.id,
            "✅ Verification successful!"
        )

        send_url_request(call.message.chat.id)

    else:
        bot.answer_callback_query(
            call.id,
            "❌ Aapne abhi channel join nahi kiya.",
            show_alert=True
        )


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not is_channel_member(message.from_user.id):
        send_join_message(message.chat.id)
        return

    if not message.text:
        bot.reply_to(
            message,
            "❌ Please ek valid media link bhejiye."
        )
        return

    url = message.text.strip()

    if not url.startswith(("http://", "https://")):
        bot.reply_to(
            message,
            "❌ Please Instagram, Facebook, X/Twitter "
            "ya YouTube ka valid link bhejiye."
        )
        return

    processing_message = bot.reply_to(
        message,
        "⏳ <b>Processing...</b>\n\n"
        "Media download kiya ja raha hai."
    )

    temp_dir = None

    try:
        file_path, media_type, temp_dir = download_media(url)

        if not file_path or not os.path.isfile(file_path):
            raise FileNotFoundError(
                "Downloaded file nahi mila."
            )

        bot.edit_message_text(
            "📤 <b>Uploading...</b>\n\n"
            "Downloaded media Telegram par bheja ja raha hai.",
            message.chat.id,
            processing_message.message_id
        )

        with open(file_path, "rb") as media:

            if media_type == "video":
                bot.send_video(
                    message.chat.id,
                    media,
                    caption="✅ Download complete!"
                )

            elif media_type == "image":
                bot.send_photo(
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

        bot.delete_message(
            message.chat.id,
            processing_message.message_id
        )

    except Exception as error:
        print("Download error:", error)

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
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(
                temp_dir,
                ignore_errors=True
            )


def run_bot():
    print("Telegram bot started...")

    bot.infinity_polling(
        skip_pending=True,
        timeout=60,
        long_polling_timeout=60
    )


# Start Telegram bot when Render
