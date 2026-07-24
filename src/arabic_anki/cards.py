from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Card:
    id: str
    arabic: str
    english: str
    example_arabic: str = ""
    example_english: str = ""
    tts_text: str = ""
    tags: tuple[str, ...] = ()

    @property
    def transcript(self) -> str:
        if self.tts_text.strip():
            return self.tts_text.strip()
        parts = [self.arabic.strip()]
        if self.example_arabic.strip():
            parts.append(self.example_arabic.strip())
        return "\n\n".join(parts)


def load_cards(path: Path) -> list[Card]:
    cards: list[Card] = []
    seen_ids: set[str] = set()

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        try:
            data = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on {path}:{line_number}: {exc}") from exc

        for required in ("id", "arabic", "english"):
            value = data.get(required)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{path}:{line_number} requires a non-empty string '{required}'")

        card_id = data["id"].strip()
        if card_id in seen_ids:
            raise ValueError(f"Duplicate card id '{card_id}' on {path}:{line_number}")
        seen_ids.add(card_id)

        tags = data.get("tags", [])
        if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            raise ValueError(f"{path}:{line_number} field 'tags' must be an array of strings")

        cards.append(
            Card(
                id=card_id,
                arabic=data["arabic"].strip(),
                english=data["english"].strip(),
                example_arabic=str(data.get("example_arabic", "")).strip(),
                example_english=str(data.get("example_english", "")).strip(),
                tts_text=str(data.get("tts_text", "")).strip(),
                tags=tuple(tag.strip() for tag in tags if tag.strip()),
            )
        )

    return cards
