from __future__ import annotations

import base64
import os
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

from .cards import Card
from .config import TTSConfig
from .prompt import audio_filename, build_tts_prompt


def _create_client(api_key: str) -> object:
    from google import genai
    from google.genai import types

    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(
                attempts=4,
                initial_delay=30.0,
                max_delay=60.0,
                exp_base=2.0,
                jitter=5.0,
            )
        ),
    )


def _decode_audio_data(data: object) -> bytes:
    if isinstance(data, str):
        return base64.b64decode(data)
    if isinstance(data, (bytes, bytearray)):
        raw = bytes(data)
        if raw.startswith((b"RIFF", b"ID3")):
            return raw
        try:
            return base64.b64decode(raw, validate=True)
        except Exception:
            return raw
    raise TypeError(f"Unsupported Gemini audio data type: {type(data).__name__}")


def _write_pcm_wave(path: Path, pcm: bytes, sample_rate_hz: int) -> None:
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate_hz)
        output.writeframes(pcm)


def _convert_to_mp3(source: Path, destination: Path) -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required to convert Gemini PCM audio to MP3")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-codec:a",
            "libmp3lame",
            "-q:a",
            "4",
            str(destination),
        ],
        check=True,
    )


def _request_audio(client: object, prompt: str, config: TTSConfig) -> object:
    return client.interactions.create(
        model=config.model,
        input=prompt,
        response_format={"type": "audio"},
        generation_config={
            "speech_config": [
                {"voice": config.voice},
            ]
        },
    )


def synthesize_card(
    card: Card,
    config: TTSConfig,
    media_dir: Path,
    *,
    force: bool = False,
    api_key: str | None = None,
) -> tuple[Path, bool]:
    destination = media_dir / audio_filename(card, config)
    if destination.exists() and destination.stat().st_size > 0 and not force:
        return destination, False

    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    try:
        client = _create_client(key)
    except ImportError as exc:
        raise RuntimeError("Install dependencies with: pip install -r requirements.txt") from exc

    interaction = _request_audio(client, build_tts_prompt(card.transcript, config), config)

    output_audio = getattr(interaction, "output_audio", None)
    data = getattr(output_audio, "data", None)
    if data is None:
        raise RuntimeError("Gemini returned no output_audio.data")

    raw_audio = _decode_audio_data(data)
    media_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="arabic-anki-tts-") as temporary_dir:
        temporary = Path(temporary_dir)
        if raw_audio.startswith(b"RIFF"):
            source = temporary / "audio.wav"
            source.write_bytes(raw_audio)
        elif raw_audio.startswith(b"ID3"):
            source = temporary / "audio.mp3"
            source.write_bytes(raw_audio)
        else:
            source = temporary / "audio.wav"
            _write_pcm_wave(source, raw_audio, config.sample_rate_hz)

        partial = destination.with_name(destination.name + ".tmp.mp3")
        _convert_to_mp3(source, partial)
        partial.replace(destination)

    return destination, True


def generate_audio(
    cards: list[Card],
    config: TTSConfig,
    media_dir: Path,
    *,
    force: bool = False,
) -> tuple[int, int]:
    generated = 0
    reused = 0
    for index, card in enumerate(cards, 1):
        path, was_generated = synthesize_card(card, config, media_dir, force=force)
        status = "generated" if was_generated else "reused"
        print(f"[{index}/{len(cards)}] {status}: {card.id} -> {path.name}")
        generated += int(was_generated)
        reused += int(not was_generated)
    return generated, reused
