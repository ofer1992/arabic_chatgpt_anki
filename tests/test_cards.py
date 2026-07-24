from pathlib import Path

import pytest

from arabic_anki.cards import load_cards


def test_load_cards_and_derived_transcript(tmp_path: Path) -> None:
    path = tmp_path / "cards.jsonl"
    path.write_text(
        '{"id":"x","arabic":"كلمة","english":"word","example_arabic":"هاي كلمة"}\n',
        encoding="utf-8",
    )
    card = load_cards(path)[0]
    assert card.transcript == "كلمة\n\nهاي كلمة"


def test_duplicate_ids_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "cards.jsonl"
    path.write_text(
        '{"id":"x","arabic":"أ","english":"a"}\n'
        '{"id":"x","arabic":"ب","english":"b"}\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Duplicate card id"):
        load_cards(path)
