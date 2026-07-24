from __future__ import annotations

import argparse
from pathlib import Path

from .build import build_deck
from .cards import load_cards
from .config import load_deck_config, load_tts_config
from .prompt import audio_filename, build_tts_prompt
from .tts import generate_audio
from .validate import validate_apkg


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the Arabic ChatGPT Anki deck")
    parser.add_argument("--root", type=Path, default=project_root())
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("check", help="Validate cards and configuration")

    prompt_parser = subparsers.add_parser("show-prompt", help="Print the exact Gemini prompt for a card")
    prompt_parser.add_argument("card_id")

    audio_parser = subparsers.add_parser("generate-audio", help="Generate missing Gemini TTS audio")
    audio_parser.add_argument("--force", action="store_true", help="Regenerate all audio")

    build_parser_ = subparsers.add_parser("build", help="Build the .apkg with genanki")
    build_parser_.add_argument("--allow-missing-audio", action="store_true")

    subparsers.add_parser("validate", help="Validate the generated .apkg")
    subparsers.add_parser("all", help="Generate audio, build, and validate")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    cards = load_cards(root / "cards" / "cards.jsonl")
    tts_config = load_tts_config(root / "config" / "tts.json")
    deck_config = load_deck_config(root / "config" / "deck.json")
    media_dir = root / "media"
    output_path = root / "dist" / deck_config.output_filename

    if args.command == "check":
        print(f"Validated {len(cards)} cards")
        for card in cards:
            print(f"- {card.id}: {audio_filename(card, tts_config)}")
        return 0

    if args.command == "show-prompt":
        card = next((item for item in cards if item.id == args.card_id), None)
        if card is None:
            raise SystemExit(f"Unknown card id: {args.card_id}")
        print(build_tts_prompt(card.transcript, tts_config))
        return 0

    if args.command == "generate-audio":
        generated, reused = generate_audio(cards, tts_config, media_dir, force=args.force)
        print(f"Generated {generated}; reused {reused}")
        return 0

    if args.command == "build":
        path = build_deck(
            cards,
            tts_config,
            deck_config,
            media_dir,
            output_path,
            require_audio=not args.allow_missing_audio,
        )
        print(path)
        return 0

    if args.command == "validate":
        result = validate_apkg(output_path, expected_notes=len(cards))
        print(result)
        return 0

    if args.command == "all":
        generated, reused = generate_audio(cards, tts_config, media_dir)
        print(f"Generated {generated}; reused {reused}")
        build_deck(cards, tts_config, deck_config, media_dir, output_path)
        print(validate_apkg(output_path, expected_notes=len(cards)))
        return 0

    raise AssertionError(f"Unhandled command: {args.command}")
