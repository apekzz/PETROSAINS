"""Google Drive path helpers for local Drive Desktop and Colab."""

from __future__ import annotations

import re
from pathlib import Path

try:
    from google.colab import drive

    drive.mount("/content/drive")
    MY_DRIVE = Path("/content/drive/MyDrive")
    SHORTCUTS_DIR = Path("/content/drive/.shortcut-targets-by-id")
except ImportError:
    MY_DRIVE = Path(r"G:\My Drive")
    SHORTCUTS_DIR = Path(r"G:\.shortcut-targets-by-id")

if not MY_DRIVE.exists():
    raise FileNotFoundError(
        f"Google Drive not found at {MY_DRIVE}. "
        "Open Google Drive for Desktop, then retry."
    )

BASE_DIR = MY_DRIVE


def _looks_like_dataset(path: Path) -> bool:
    return (
        path.is_dir()
        and (path / "images").exists()
        and (path / "labels").exists()
        and (path / "data.yaml").exists()
    )


def _resolve_lnk(lnk: Path) -> Path | None:
    """Resolve a Windows .lnk (Google Drive shortcuts show up this way)."""
    if not lnk.exists() or lnk.suffix.lower() != ".lnk":
        return None

    try:
        import win32com.client

        target = win32com.client.Dispatch("WScript.Shell").CreateShortCut(str(lnk)).Targetpath
        if target:
            p = Path(target)
            return p if p.exists() else None
    except Exception:
        pass

    data = lnk.read_bytes()
    for text in (
        data.decode("utf-16le", errors="ignore"),
        data.decode("latin-1", errors="ignore"),
    ):
        match = re.search(
            r"G:\\.shortcut-targets-by-id\\[A-Za-z0-9_-]+(?:\\[^\x00\\/:*?\"<>|\r\n]+)*",
            text,
        )
        if match:
            p = Path(match.group(0).split("\x00", 1)[0])
            if p.exists():
                return p
    return None


def drive_folder(url_or_id_or_name: str = "dataset") -> Path:
    """Find a Drive folder, including Shared-with-me shortcuts saved as .lnk."""
    text = str(url_or_id_or_name).strip()
    match = re.search(r"/folders/([a-zA-Z0-9_-]+)", text)
    folder_id = match.group(1) if match else None
    if folder_id is None and re.fullmatch(r"[a-zA-Z0-9_-]{20,}", text):
        folder_id = text

    candidates: list[Path] = []
    if folder_id:
        candidates.append(SHORTCUTS_DIR / folder_id)
        candidates.append(SHORTCUTS_DIR / folder_id / "dataset")
    if text and not text.startswith("http"):
        candidates.append(MY_DRIVE / text)
        lnk = _resolve_lnk(MY_DRIVE / f"{text}.lnk")
        if lnk is not None:
            candidates.append(lnk)

    for path in candidates:
        if not path.exists():
            continue
        if _looks_like_dataset(path):
            return path
        nested = path / "dataset"
        if _looks_like_dataset(nested):
            return nested
        if path.is_dir():
            return path

    for lnk_path in MY_DRIVE.glob("*.lnk"):
        target = _resolve_lnk(lnk_path)
        if target is None:
            continue
        if _looks_like_dataset(target):
            return target
        nested = target / "dataset"
        if _looks_like_dataset(nested):
            return nested

    raise FileNotFoundError(
        f"Could not find {text!r} on My Drive. "
        "Make sure the dataset shortcut is in G:\\My Drive and retry."
    )
