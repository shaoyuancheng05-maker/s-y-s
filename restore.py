"""Restore the split wheel and verify the original coursework snapshot."""

from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "backup-manifest.jsonl"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def restore_split_files(items: list[dict]) -> None:
    for item in items:
        path = ROOT.joinpath(*item["path"].split("/"))
        if path.exists():
            continue
        parts = sorted(path.parent.glob(path.name + ".part[0-9][0-9][0-9][0-9]"))
        if not parts:
            continue
        temporary = path.with_name(path.name + ".assembling")
        try:
            with temporary.open("wb") as output:
                for part in parts:
                    with part.open("rb") as source:
                        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
                            output.write(block)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


def verify() -> None:
    empty_directories = json.loads((ROOT / "empty-dirs.json").read_text(encoding="utf-8"))
    for relative in empty_directories:
        ROOT.joinpath(*relative.split("/")).mkdir(parents=True, exist_ok=True)
    items = [json.loads(line) for line in MANIFEST.read_text(encoding="utf-8").splitlines()]
    restore_split_files(items)

    def check(item: dict) -> None:
        path = ROOT.joinpath(*item["path"].split("/"))
        if not path.is_file():
            raise FileNotFoundError(f"Missing: {item['path']}")
        if path.stat().st_size != item["size"]:
            raise ValueError(f"Size mismatch: {item['path']}")
        if sha256(path) != item["sha256"]:
            raise ValueError(f"SHA-256 mismatch: {item['path']}")

    with ThreadPoolExecutor(max_workers=16) as pool:
        for checked, _ in enumerate(pool.map(check, items), 1):
            if checked % 5000 == 0:
                print(f"Verified {checked}/{len(items)} files...", flush=True)
    print(f"Verified {len(items)} original files against SHA-256 manifest.")


if __name__ == "__main__":
    verify()
