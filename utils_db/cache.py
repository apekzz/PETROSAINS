"""Save and reload cropped-object embeddings (val cache, etc.)."""

from __future__ import annotations

import pickle
from pathlib import Path

DEFAULT_VAL_OBJECTS_PATH = Path("val_objects.pkl")


def save_query_objects(objects: list[dict], path: str | Path = DEFAULT_VAL_OBJECTS_PATH) -> Path:
    """Write ``objects`` to a pickle using a temp file so a crash cannot leave 0 bytes."""
    dest = Path(path)
    tmp_path = dest.with_suffix(dest.suffix + ".tmp")
    payload = []
    for obj in objects:
        rec = dict(obj)
        if "path" in rec:
            rec["path"] = str(rec["path"])
        payload.append(rec)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tmp_path.open("wb") as handle:
        pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)
    tmp_path.replace(dest)
    print(f"saved {len(payload)} crops ({dest.stat().st_size} bytes) to {dest}")
    return dest


def load_query_objects(path: str | Path = DEFAULT_VAL_OBJECTS_PATH) -> list[dict]:
    """Load objects previously written by ``save_query_objects``."""
    dest = Path(path)
    if not dest.exists() or dest.stat().st_size == 0:
        raise FileNotFoundError(
            f"{dest} is missing or empty. Embed the crops first, then call save_query_objects()."
        )
    with dest.open("rb") as handle:
        payload = pickle.load(handle)
    for rec in payload:
        if "path" in rec and rec["path"] is not None:
            rec["path"] = Path(rec["path"])
    print(f"loaded {len(payload)} crops ({dest.stat().st_size} bytes) from {dest}")
    return payload
