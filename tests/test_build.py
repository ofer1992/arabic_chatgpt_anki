from pathlib import Path

import pytest

from arabic_anki.build import build_deck
from arabic_anki.cards import Card
from arabic_anki.config import DeckConfig, TTSConfig
from arabic_anki.prompt import audio_filename
from arabic_anki.validate import validate_apkg


def test_genanki_build_and_validate(tmp_path: Path) -> None:
    pytest.importorskip("genanki")
    card = Card(id="stable-id", arabic="مرحبا", english="hello", tts_text="مرحبا")
    tts = TTSConfig(
        model="gemini-3.1-flash-tts-preview",
        voice="Kore",
        sample_rate_hz=24000,
        prompt_version=1,
        audio_profile="profile",
        scene="scene",
    )
    deck = DeckConfig(
        deck_name="Arabic — ChatGPT Conversations",
        deck_id=2077240724,
        model_name="Arabic ChatGPT Conversation Card",
        model_id=1977240724,
        output_filename="test.apkg",
    )
    media = tmp_path / "media"
    media.mkdir()
    # genanki only needs a media file; its audio contents are not decoded during packaging.
    (media / audio_filename(card, tts)).write_bytes(b"ID3dummy")
    output = tmp_path / "test.apkg"
    build_deck([card], tts, deck, media, output)
    result = validate_apkg(output, expected_notes=1)
    assert result["notes"] == 1
    assert result["media"] == 1
