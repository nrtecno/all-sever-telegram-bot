import os
import tempfile
from urllib.parse import urlparse

import yt_dlp


ALLOWED_DOMAINS = {
    "youtube.com",
    "www.youtube.com",
    "youtu.be",
    "youtube-nocookie.com",
    "www.youtube-nocookie.com",
    "instagram.com",
    "www.instagram.com",
    "facebook.com",
    "www.facebook.com",
    "fb.watch",
    "x.com",
    "www.x.com",
    "twitter.com",
    "www.twitter.com",
}


def is_allowed_url(url: str) -> bool:
    try:
        hostname = urlparse(url).hostname

        if not hostname:
            return False

        hostname = hostname.lower().rstrip(".")

        return hostname in ALLOWED_DOMAINS

    except Exception:
        return False


def download_media(url: str):
    if not is_allowed_url(url):
        raise ValueError(
            "Only YouTube, Instagram, Facebook and X/Twitter "
            "links are supported."
        )

    temp_dir = tempfile.mkdtemp(
        prefix="all_saver_"
    )

    output_template = os.path.join(
        temp_dir,
        "%(title).80s_%(id)s.%(ext)s"
    )

    options = {
        "outtmpl": output_template,
        "format": "bv*+ba/b",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(
                url,
                download=True
            )

        files = []

        for filename in os.listdir(temp_dir):
            file_path = os.path.join(
                temp_dir,
                filename
            )

            if os.path.isfile(file_path):
                files.append(file_path)

        if not files:
            raise FileNotFoundError(
                "Downloaded file was not found."
            )

        file_path = max(
            files,
            key=os.path.getsize
        )

        extension = os.path.splitext(
            file_path
        )[1].lower()

        if extension in (
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".gif",
        ):
            media_type = "image"

        elif extension in (
            ".mp4",
            ".mkv",
            ".webm",
            ".mov",
            ".avi",
        ):
            media_type = "video"

        else:
            media_type = "document"

        return file_path, media_type, temp_dir

    except Exception:
        # Caller will remove temp_dir.
        raise
