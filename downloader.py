import os
import tempfile
import yt_dlp


ALLOWED_DOMAINS = (
    "youtube.com",
    "youtu.be",
    "youtube-nocookie.com",
    "instagram.com",
    "facebook.com",
    "fb.watch",
    "x.com",
    "twitter.com",
)


def is_allowed_url(url: str) -> bool:
    url = url.lower()

    return any(
        domain in url
        for domain in ALLOWED_DOMAINS
    )


def download_media(url: str):
    if not is_allowed_url(url):
        raise ValueError(
            "Only YouTube, Instagram, Facebook and X/Twitter links are supported."
        )

    temp_dir = tempfile.mkdtemp(prefix="all_saver_")

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

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(
            url,
            download=True
        )

        requested = info.get("requested_downloads") or []

        if requested:
            extensions = [
                item.get("ext")
                for item in requested
                if item.get("ext")
            ]
        else:
            extensions = [info.get("ext")]

    files = [
        os.path.join(temp_dir, filename)
        for filename in os.listdir(temp_dir)
    ]

    files = [
        file
        for file in files
        if os.path.isfile(file)
    ]

    if not files:
        raise FileNotFoundError(
            "Downloaded file was not found."
        )

    file_path = max(
        files,
        key=os.path.getsize
    )

    media_type = "video"

    if file_path.lower().endswith(
        (".jpg", ".jpeg", ".png", ".webp")
    ):
        media_type = "image"

    return file_path, media_type
