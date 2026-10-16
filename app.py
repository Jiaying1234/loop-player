import json
from urllib.parse import urlparse

from flask import Flask, jsonify, render_template, request, send_from_directory
from yt_dlp.utils import DownloadError

from downloader import DOWNLOAD_DIR, download_audio


# Create the website.
app = Flask(__name__)
TRACKS_FILE = DOWNLOAD_DIR / "tracks.json"


# Read saved names for downloaded sounds.
def load_track_names() -> dict[str, str]:
    if not TRACKS_FILE.exists():
        return {}
    with TRACKS_FILE.open(encoding="utf-8") as file:
        return json.load(file)


# Save a sound name so it remains after restarting the app.
def save_track_name(filename: str, name: str) -> None:
    names = load_track_names()
    names[filename] = name
    with TRACKS_FILE.open("w", encoding="utf-8") as file:
        json.dump(names, file, indent=2)


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
    names = load_track_names()
    tracks = [
        {
            "filename": path.name,
            "title": names.get(path.name, path.stem.replace("_", " ")),
        }
        for path in sorted(
            DOWNLOAD_DIR.glob("*.mp3"),
            key=lambda audio_path: audio_path.stat().st_mtime,
            reverse=True,
        )
    ]
    return render_template("index.html", tracks=tracks)


# Send a saved MP3 to the browser.
@app.get("/audio/<path:filename>")
def audio(filename: str):
    return send_from_directory(DOWNLOAD_DIR, filename)


# Rename one saved sound.
@app.post("/rename")
def rename():
    filename = request.form.get("filename", "")
    name = request.form.get("name", "").strip()
    if not name:
        return jsonify({"message": "Please enter a name for this audio.", "accepted": False}), 400
    if not filename or not (DOWNLOAD_DIR / filename).is_file() or "/" in filename or "\\" in filename:
        return jsonify({"message": "Audio not found.", "accepted": False}), 404

    try:
        save_track_name(filename, name)
    except OSError as error:
        app.logger.error("Could not save audio name: %s", error)
        return jsonify({"message": "Could not rename this audio. Try again.", "accepted": False}), 500

    return jsonify({"accepted": True})


# Check a submitted URL, download it, and return its saved details.
@app.post("/convert")
def convert():
    url = request.form.get("url", "")
    name = request.form.get("name", "").strip()
    if not is_tiktok_url(url):
        return jsonify({"message": "URL not accepted. Try again.", "accepted": False}), 400
    if not name:
        return jsonify({"message": "Please enter a name for this audio.", "accepted": False}), 400

    try:
        track = download_audio(url)
        save_track_name(track["filename"], name)
    except (DownloadError, OSError) as error:
        app.logger.error("Could not download TikTok audio: %s", error)
        return jsonify({"message": "Could not convert this URL. Try again.", "accepted": False}), 500

    track["title"] = name
    return jsonify({"accepted": True, "track": track})


# Start the website when this file is run.
if __name__ == "__main__":
    app.run(debug=True)
