# io/utils.py

from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import Tuple


def ensure_dir(path: Path | str) -> Path:
    """Ensure that a directory exists, creating it if necessary.

    Args:
        path (Path | str): Target directory path.

    Returns:
        Path: The verified (and possibly newly created) directory path.
    """
    if isinstance(path, str):
        path = Path(path)

    if path.exists():
        if not path.is_dir():
            raise NotADirectoryError(path)
    else:
        path.mkdir(parents=True, exist_ok=True)

    return path

def timestamp(fmt: str = "%Y-%m-%d_%H-%M-%S") -> str:
    """Generate a timestamp string suitable for filenames.

    Args:
        fmt (str, optional): Datetime format string. Defaults to "%Y-%m-%d_%H-%M-%S".

    Returns:
        str: Formatted timestamp string.
    """
    return datetime.now().strftime(fmt)


def build_path(base: Path | str, name: str, ext: str) -> Path:
    """Combine base directory, filename, and extension into a Path object.

    Args:
        base (Path | str): Base directory.
        name (str): Filename without extension.
        ext (str): File extension without leading dot.

    Returns:
        Path: Combined file path.
    """
    if isinstance(base, str):
        base = Path(base)

    full_path = base / f"{name}.{ext}" # Creates a Path (pathlib) object
    return full_path


def next_recording_path(out_dir: Path | str, prefix: str = "rec", ext: str = "wav") -> Path:
    """Generate a unique recording file path in the given directory.

    Args:
        out_dir (Path | str): Output directory where recordings are saved.
        prefix (str, optional): Filename prefix. Defaults to "rec".
        ext (str, optional): File extension. Defaults to "wav".

    Returns:
        Path: Full path to the new recording file.
    """
    if isinstance(out_dir, str):
        out_dir = Path(out_dir)

    ts = timestamp()
    return out_dir / f"{prefix}_{ts}.{ext}"


def is_audio_file(path: Path | str, exts: Tuple[str, ...] = ("wav", "flac", "mp3")) -> bool:
    """Check whether a given path points to an audio file based on its extension.

    Args:
        path (Path | str): Path to the file.
        exts (Tuple[str, ...], optional): Allowed extensions. Defaults to ("wav", "flac", "mp3").

    Returns:
        bool: True if the file has a valid audio extension, False otherwise.
    """
    if isinstance(path, str):
        path = Path(path)

    suffix = path.suffix.lstrip('.')

    return True if suffix in exts else False