import json
import re
import shutil
import subprocess
from pathlib import Path
from statistics import median


DOWNLOAD_DIR = Path(__file__).parent / "downloads"
VOLUME_FILE = DOWNLOAD_DIR / "volume_settings.json"
DEFAULT_TARGET_LUFS = -16.0


# Find FFmpeg so audio analysis and normalization use the installed tool.
def ffmpeg_path() -> str:
    executable = shutil.which("ffmpeg")
    if not executable:
        raise OSError("FFmpeg was not found on PATH.")
    return executable


# Measure a file's perceived loudness in LUFS.
def measure_loudness(path: Path) -> float:
    result = subprocess.run(
        [
            ffmpeg_path(),
            "-i",
            str(path),
            "-af",
            "loudnorm=print_format=json",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    match = re.search(r'"input_i"\s*:\s*"(-?\d+(?:\.\d+)?)"', result.stderr)
    if not match:
        raise OSError(f"Could not measure loudness for {path.name}.")
    return float(match.group(1))


# Choose the median loudness of existing songs as the shared target.
def target_loudness() -> float:
    if VOLUME_FILE.exists():
        with VOLUME_FILE.open(encoding="utf-8") as file:
            return float(json.load(file)["target_lufs"])

    measurements = [
        measure_loudness(path)
        for path in DOWNLOAD_DIR.glob("*.mp3")
    ]
    target = median(measurements) if measurements else DEFAULT_TARGET_LUFS
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    with VOLUME_FILE.open("w", encoding="utf-8") as file:
        json.dump({"target_lufs": target}, file, indent=2)
    return target


# Normalize one MP3 to the shared loudness target.
def normalize_audio(path: Path) -> None:
    target = target_loudness()
    temporary_path = path.with_suffix(".normalized.mp3")
    result = subprocess.run(
        [
            ffmpeg_path(),
            "-y",
            "-i",
            str(path),
            "-af",
            f"loudnorm=I={target}:TP=-1.5:LRA=11",
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(temporary_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not temporary_path.exists():
        temporary_path.unlink(missing_ok=True)
        raise OSError(f"Could not normalize {path.name}: {result.stderr[-500:]}")
    temporary_path.replace(path)
