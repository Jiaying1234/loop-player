from pathlib import Path

import yt_dlp
from yt_dlp.networking.impersonate import ImpersonateTarget


DOWNLOAD_DIR = Path(__file__).parent / "downloads"


def download_audio(url: str) -> dict[str, str]:
    """Download one TikTok video as an MP3 and return its display details."""
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    options = {
        "format": "bestaudio/best",
        "outtmpl": str(DOWNLOAD_DIR / "%(id)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "noplaylist": True,
        "impersonate": ImpersonateTarget.from_str("chrome"),
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(options) as downloader:
        info = downloader.extract_info(url, download=True)

    video_id = info["id"]
    return {
        "filename": f"{video_id}.mp3",
        "title": info.get("title") or "TikTok sound",
    }
