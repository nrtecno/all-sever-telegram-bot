import os
import shutil
import tempfile
from urllib.parse import urlparse

import yt_dlp


ALLOWED_DOMAINS = {
    "youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com",
    "youtube-nocookie.com", "www.youtube-nocookie.com",

    "instagram.com", "www.instagram.com",

    "facebook.com", "www.facebook.com", "m.facebook.com", "fb.watch",

    "x.com", "www.x.com", "twitter.com", "www.twitter.com",
}


def is_allowed_url(url: str) -> bool:
    try:
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname

        if not hostname:
            return False

        return hostname.lower().rstrip(".") in ALLOWED_DOMAINS

    except Exception:
        return False


def is_instagram_url(url: str) -> bool:
    try:
        hostname = urlparse(url).hostname

        return bool(hostname) and hostname.lower().rstrip(".") in {
            "instagram.com",
            "www.instagram.com",
        }

    except Exception:
        return False


def detect_media_type(file_path: str) -> str:

    extension = os.path.splitext(
        file_path
    )[1].lower()

    if extension in {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".gif",
        ".bmp",
        ".avif",
    }:
        return "image"

    if extension in {
        ".mp4",
        ".mkv",
        ".webm",
        ".mov",
        ".avi",
        ".m4v",
        ".flv",
    }:
        return "video"

    return "document"


def get_downloaded_files(temp_dir: str):

    files = []

    ignored_extensions = {
        ".part",
        ".ytdl",
        ".temp",
        ".json",
        ".description",
        ".vtt",
        ".srt",
        ".ass",
        ".lrc",
    }

    for root, _, filenames in os.walk(temp_dir):

        for filename in filenames:

            if (
                os.path.splitext(filename)[1].lower()
                in ignored_extensions
            ):
                continue

            file_path = os.path.join(
                root,
                filename
            )

            if os.path.isfile(file_path):
                files.append(file_path)

    return files


def _create_cookie_file(temp_dir: str):

    cookie_data = os.getenv(
        "INSTAGRAM_COOKIES",
        ""
    ).strip()

    if not cookie_data:
        return None

    cookie_file = os.path.join(
        temp_dir,
        "instagram_cookies.txt"
    )

    with open(
        cookie_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(cookie_data)

    return cookie_file


def _build_options(
    output_template: str,
    cookie_file
):

    options = {

        "format":
            "bv*+ba/b/best[ext=mp4]/best",

        "outtmpl":
            output_template,

        "noplaylist":
            True,

        "merge_output_format":
            "mp4",

        "quiet":
            True,

        "no_warnings":
            True,

        "restrictfilenames":
            True,

        "writethumbnail":
            False,

        "writeinfojson":
            False,

        "writesubtitles":
            False,

        "writeautomaticsub":
            False,

        "socket_timeout":
            30,

        "retries":
            3,

        "fragment_retries":
            3,
    }

    if cookie_file:

        options["cookiefile"] = cookie_file

    return options


def download_media(url: str):

    if not is_allowed_url(url):

        raise ValueError(
            "Only YouTube, Instagram, Facebook "
            "and X/Twitter links are supported."
        )

    temp_dir = tempfile.mkdtemp(
        prefix="all_saver_"
    )

    output_template = os.path.join(
        temp_dir,
        "%(title).80s_%(id)s.%(ext)s"
    )

    try:

        cookie_file = None

        if is_instagram_url(url):

            cookie_file = _create_cookie_file(
                temp_dir
            )

        options = _build_options(
            output_template,
            cookie_file
        )

        with yt_dlp.YoutubeDL(
            options
        ) as ydl:

            ydl.extract_info(
                url,
                download=True
            )

        files = get_downloaded_files(
            temp_dir
        )

        media_files = [
            file
            for file in files
            if detect_media_type(file)
            in ("video", "image")
        ]

        if media_files:
            files = media_files

        if not files:

            raise FileNotFoundError(
                "Downloaded media file was not found."
            )

        file_path = max(
            files,
            key=os.path.getsize
        )

        if os.path.getsize(
            file_path
        ) <= 0:

            raise ValueError(
                "Downloaded file is empty."
            )

        return (
            file_path,
            detect_media_type(file_path),
            temp_dir
        )

    except Exception:

        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )

        raise
