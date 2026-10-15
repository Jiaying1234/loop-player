from urllib.parse import urlparse

from flask import Flask, jsonify, render_template, request, send_from_directory
from yt_dlp.utils import DownloadError

from downloader import DOWNLOAD_DIR, download_audio


# Create the website.
app = Flask(__name__)


# Check whether the address is an acceptable TikTok URL.
def is_tiktok_url(value: str) -> bool:
    """Return whether value is an HTTPS URL hosted on tiktok.com."""
    parsed = urlparse(value.strip())
    hostname = (parsed.hostname or "").lower()
    return (
        parsed.scheme == "https"
        and hostname in {"tiktok.com", "www.tiktok.com"}
        and bool(parsed.path.strip("/"))
    )


# Show the homepage.
@app.get("/")
def index():
    tracks = [
        {"filename": path.name, "title": path.stem.replace("_", " ")}
        for path in sorted(DOWNLOAD_DIR.glob("*.mp3"))
    ]
    return render_template("index.html", tracks=tracks)


# Send a saved MP3 to the browser.
@app.get("/audio/<path:filename>")
def audio(filename: str):
    return send_from_directory(DOWNLOAD_DIR, filename)


# Check a submitted URL, download it, and return its saved details.
@app.post("/convert")
def convert():
    url = request.form.get("url", "")
    if not is_tiktok_url(url):
        return jsonify({"message": "URL not accepted. Try again.", "accepted": False}), 400

    try:
        track = download_audio(url)
    except (DownloadError, OSError) as error:
        app.logger.error("Could not download TikTok audio: %s", error)
        return jsonify({"message": "Could not convert this URL. Try again.", "accepted": False}), 500

    return jsonify({"accepted": True, "track": track})


# Start the website when this file is run.
if __name__ == "__main__":
    app.run(debug=True)
