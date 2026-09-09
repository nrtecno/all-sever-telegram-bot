import os
import shutil
import tempfile
from urllib.parse import urlparse

import yt_dlp


ALLOWED_DOMAINS = {
    # YouTube
    "youtube.com",
    "www.youtube.com",
    "youtu.be",
    "m.youtube.com",
    "youtube-nocookie.com",
    "www.youtube-nocookie.com",

    # Instagram
    "instagram.com",
    "www.instagram.com",

    # Facebook
    "facebook.com",
    "www.facebook.com",
    "m.facebook.com",
    "fb.watch",

    # X / Twitter
    "x.com",
    "www.x.com",
    "twitter.com",
    "www.twitter.com",
}


def is_allowed_url(url: str) -> bool:
    """Check that URL belongs to a supported platform."""

    try:
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname

        if not hostname:
            return False

        hostname = hostname.lower().rstrip(".")

        return hostname in ALLOWED_DOMAINS

    except Exception:
        return False


def detect_media_type(file_path: str) -> str:
    """Detect whether downloaded file is image, video or document."""

    extension = os.path.splitext(file_path)[1].lower()

    image_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".gif",
        ".bmp",
        ".avif",
    }

    video_extensions = {
        ".mp4",
        ".mkv",
        ".webm",
        ".mov",
        ".avi",
        ".m4v",
        ".flv",
    }

    if extension in image_extensions:
        return "image"

    if extension in video_extensions:
        return "video"

    return "document"


def get_downloaded_files(temp_dir: str):
    """Return actual downloaded media files."""

    files = []

    if not os.path.exists(temp_dir):
        return files

    for root, _, filenames in os.walk(temp_dir):

        for filename in filenames:

            # Ignore temporary / metadata files
            if filename.endswith(
                (
                    ".part",
                    ".ytdl",
                    ".temp",
                    ".json",
                    ".description",
                    ".vtt",
                    ".srt",
                    ".ass",
                )
            ):
                continue

            file_path = os.path.join(
                root,
                filename
            )

            if os.path.isfile(file_path):
                files.append(file_path)

    return files


def download_media(url: str):
    """
    Download public media from supported platforms.

    Returns:
        file_path,
        media_type,
        temp_dir
    """

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

    options = {
        # Best available quality.
        # If separate video/audio streams are available,
        # yt-dlp will try to merge them.
        "format": (
            "bv*+ba/"
            "b/"
            "best[ext=mp4]/"
            "best"
        ),

        "outtmpl": output_template,

        # Don't download playlists.
        "noplaylist": True,

        # Merge into MP4 when possible.
        "merge_output_format": "mp4",

        # Don't print huge logs.
        "quiet": True,
        "no_warnings": True,

        # Better filenames for Linux/Render.
        "restrictfilenames": True,

        # Avoid unnecessary files.
        "writethumbnail": False,
        "writeinfojson": False,
        "writesubtitles": False,
        "writeautomaticsub": False,

        # Network settings.
        "socket_timeout": 30,
        "retries": 3,
        "fragment_retries": 3,

        # Continue even if a particular format fails.
        "ignoreerrors": False,
    }

    try:

        with yt_dlp.YoutubeDL(options) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

        # Find downloaded files.
        files = get_downloaded_files(
            temp_dir
        )

        if not files:

            raise FileNotFoundError(
                "Downloaded media file was not found."
            )

        # Prefer common media files.
        media_files = [
            file
            for file in files
            if detect_media_type(file)
            in ("video", "image")
        ]

        if media_files:
            files = media_files

        # Pick largest file.
        file_path = max(
            files,
            key=os.path.getsize
        )

        if not os.path.isfile(file_path):

            raise FileNotFoundError(
                "Downloaded file does not exist."
            )

        if os.path.getsize(file_path) <= 0:

            raise ValueError(
                "Downloaded file is empty."
            )

        media_type = detect_media_type(
            file_path
        )

        return (
            file_path,
            media_type,
            temp_dir
        )

    except Exception:

        # Clean up if downloading fails.
        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )

        raise
