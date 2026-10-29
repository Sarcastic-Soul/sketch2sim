import hashlib
import json
from pathlib import Path
from typing import Any

from backend.config import CACHE_DIR


def _key(namespace: str, payload: bytes) -> str:
    return hashlib.sha256(namespace.encode() + b"\\0" + payload).hexdigest()


def cache_path(namespace: str, payload: bytes, ext: str) -> Path:
    root = Path(CACHE_DIR)
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{namespace}_{_key(namespace, payload)}.{ext}"


def get_json(namespace: str, payload: bytes) -> Any | None:
    path = cache_path(namespace, payload, "json")
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def put_json(namespace: str, payload: bytes, value: Any) -> None:
    cache_path(namespace, payload, "json").write_text(
        json.dumps(value, sort_keys=True), encoding="utf-8"
    )


def get_bytes(namespace: str, payload: bytes, ext: str) -> bytes | None:
    path = cache_path(namespace, payload, ext)
    return path.read_bytes() if path.exists() else None


def put_bytes(namespace: str, payload: bytes, value: bytes, ext: str) -> None:
    cache_path(namespace, payload, ext).write_bytes(value)
