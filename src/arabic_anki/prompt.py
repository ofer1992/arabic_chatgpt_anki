from __future__ import annotations

import hashlib
import json

from .cards import Card
from .config import TTSConfig


def build_tts_prompt(transcript: str, config: TTSConfig) -> str:
    return (
        "Read the following transcript based on the audio profile.\n\n"
        "# Audio Profile\n"
        f"{config.audio_profile}\n\n"
        "## Scene:\n"
        f"{config.scene}\n\n"
        "## Transcript:\n"
        f"{transcript.strip()}"
    )


def audio_fingerprint(card: Card, config: TTSConfig) -> str:
    payload = {
        "model": config.model,
        "voice": config.voice,
        "sample_rate_hz": config.sample_rate_hz,
        "prompt_version": config.prompt_version,
        "prompt": build_tts_prompt(card.transcript, config),
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def audio_filename(card: Card, config: TTSConfig) -> str:
    return f"pal_{audio_fingerprint(card, config)[:20]}.mp3"
