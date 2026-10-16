import json
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, jsonify, render_template, request, send_from_directory
from yt_dlp.utils import DownloadError

from downloader import DOWNLOAD_DIR, download_audio


# Create the website.
app = Flask(__name__)
TRACKS_FILE = DOWNLOAD_DIR / "tracks.json"
ORDER_FILE = DOWNLOAD_DIR / "track_order.json"


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


# Remove a sound name from saved metadata.
def remove_track_name(filename: str) -> None:
    names = load_track_names()
    names.pop(filename, None)
    with TRACKS_FILE.open("w", encoding="utf-8") as file:
        json.dump(names, file, indent=2)


# Read the saved order of the sounds.
def load_track_order() -> list[str]:
    if not ORDER_FILE.exists():
        return []
    with ORDER_FILE.open(encoding="utf-8") as file:
        return json.load(file)


# Save the order of the sounds.
def save_track_order(filenames: list[str]) -> None:
    with ORDER_FILE.open("w", encoding="utf-8") as file:
        json.dump(filenames, file, indent=2)


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
    audio_files = {
        path.name: path for path in DOWNLOAD_DIR.glob("*.mp3")
    }
    newest_first = sorted(
        audio_files,
        key=lambda filename: audio_files[filename].stat().st_mtime,
        reverse=True,
    )
    saved_order = load_track_order()
    ordered_filenames = [
        filename for filename in saved_order if filename in audio_files
    ]
    ordered_filenames.extend(
        filename for filename in newest_first if filename not in ordered_filenames
    )
    tracks = [
        {
            "filename": filename,
            "title": names.get(filename, Path(filename).stem.replace("_", " ")),
        }
        for filename in ordered_filenames
    ]
    return render_template("index.html", tracks=tracks)


# Send a saved MP3 to the browser.
@app.get("/audio/<path:filename>")
def audio(filename: str):
    return send_from_directory(DOWNLOAD_DIR, filename)


# Delete one saved sound.
@app.post("/delete")
def delete():
    filename = request.form.get("filename", "")
    if not filename or not (DOWNLOAD_DIR / filename).is_file() or "/" in filename or "\\" in filename:
        return jsonify({"message": "Audio not found.", "accepted": False}), 404

    try:
        (DOWNLOAD_DIR / filename).unlink()
        remove_track_name(filename)
        save_track_order([item for item in load_track_order() if item != filename])
    except OSError as error:
        app.logger.error("Could not delete audio: %s", error)
        return jsonify({"message": "Could not delete this audio. Try again.", "accepted": False}), 500

    return jsonify({"accepted": True})


# Save a new order for the sounds.
@app.post("/reorder")
def reorder():
    filenames = request.get_json(silent=True)
    current_files = {path.name for path in DOWNLOAD_DIR.glob("*.mp3")}
    if (
        not isinstance(filenames, list)
        or any(not isinstance(filename, str) or "/" in filename or "\\" in filename for filename in filenames)
        or set(filenames) != current_files
    ):
        return jsonify({"message": "Invalid audio order.", "accepted": False}), 400

    try:
        save_track_order(filenames)
    except OSError as error:
        app.logger.error("Could not save audio order: %s", error)
        return jsonify({"message": "Could not save the audio order. Try again.", "accepted": False}), 500

    return jsonify({"accepted": True})


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
        save_track_order(
            [track["filename"]]
            + [filename for filename in load_track_order() if filename != track["filename"]]
        )
    except (DownloadError, OSError) as error:
        app.logger.error("Could not download TikTok audio: %s", error)
        return jsonify({"message": "Could not convert this URL. Try again.", "accepted": False}), 500

    track["title"] = name
    return jsonify({"accepted": True, "track": track})


# Start the website when this file is run.
if __name__ == "__main__":
    app.run(debug=True)
