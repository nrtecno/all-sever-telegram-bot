# All Saver Telegram Bot

Telegram bot for downloading publicly accessible media from supported
YouTube, Instagram, Facebook and X/Twitter links using yt-dlp.

## Features

- Telegram bot interface
- YouTube support
- Instagram support
- Facebook support
- X/Twitter support
- yt-dlp based downloading
- Flask web app
- Render deployment support
- Telegram channel verification

## Environment Variables

Set these variables in Render:

- `BOT_TOKEN` — Telegram Bot Token
- `CHANNEL_USERNAME` — Telegram channel username
- `CHANNEL_URL` — Telegram channel URL

Example:

```env
BOT_TOKEN=your_bot_token
CHANNEL_USERNAME=@nrtecno2
CHANNEL_URL=https://t.me/nrtecno2
