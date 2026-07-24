from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TTSConfig:
    model: str
    voice: str
    sample_rate_hz: int
    prompt_version: int
    audio_profile: str
    scene: str


@dataclass(frozen=True)
class DeckConfig:
    deck_name: str
    deck_id: int
    model_name: str
    model_id: int
    output_filename: str


def load_tts_config(path: Path) -> TTSConfig:
    data = json.loads(path.read_text(encoding="utf-8"))
    return TTSConfig(**data)


def load_deck_config(path: Path) -> DeckConfig:
    data = json.loads(path.read_text(encoding="utf-8"))
    return DeckConfig(**data)
