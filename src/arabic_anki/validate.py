from __future__ import annotations

import json
import sqlite3
import tempfile
import zipfile
from pathlib import Path


def validate_apkg(
    path: Path,
    expected_notes: int | None = None,
    expected_cards: int | None = None,
) -> dict[str, int | str]:
    if not path.exists() or path.stat().st_size == 0:
        raise ValueError(f"Missing or empty package: {path}")

    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        if "collection.anki2" not in names:
            raise ValueError("Package does not contain collection.anki2")
        if "media" not in names:
            raise ValueError("Package does not contain media manifest")

        media_manifest = json.loads(archive.read("media").decode("utf-8"))
        missing_members = [member for member in media_manifest if member not in names]
        if missing_members:
            raise ValueError(f"Media manifest references missing members: {missing_members}")

        with tempfile.TemporaryDirectory(prefix="arabic-anki-validate-") as temporary_dir:
            db_path = Path(temporary_dir) / "collection.anki2"
            db_path.write_bytes(archive.read("collection.anki2"))
            connection = sqlite3.connect(db_path)
            try:
                integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
                note_count = connection.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
                card_count = connection.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
            finally:
                connection.close()

    if integrity != "ok":
        raise ValueError(f"SQLite integrity check failed: {integrity}")
    if expected_notes is not None and note_count != expected_notes:
        raise ValueError(f"Expected {expected_notes} notes, found {note_count}")
    if expected_cards is not None and card_count != expected_cards:
        raise ValueError(f"Expected {expected_cards} cards, found {card_count}")

    return {
        "integrity": integrity,
        "notes": note_count,
        "cards": card_count,
        "media": len(media_manifest),
    }
