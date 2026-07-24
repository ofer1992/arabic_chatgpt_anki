from __future__ import annotations

import html
from pathlib import Path

from .cards import Card
from .config import DeckConfig, TTSConfig
from .prompt import audio_filename


CARD_CSS = r"""
.card {
  font-family: Arial, sans-serif;
  font-size: 20px;
  text-align: center;
  color: #1f1f1f;
  background: #ffffff;
  padding: 18px;
}
.arabic {
  direction: rtl;
  font-family: "Noto Naskh Arabic", "Noto Sans Arabic", Arial, sans-serif;
  font-size: 38px;
  line-height: 1.7;
  margin: 12px 0;
}
.english {
  font-size: 23px;
  margin: 14px 0;
}
.example-arabic {
  direction: rtl;
  font-family: "Noto Naskh Arabic", "Noto Sans Arabic", Arial, sans-serif;
  font-size: 29px;
  line-height: 1.6;
  margin-top: 22px;
}
.example-english {
  font-size: 18px;
  color: #555;
  margin-top: 8px;
}
.audio {
  margin-top: 14px;
}
hr#answer {
  margin: 22px 0;
}
"""


def build_deck(
    cards: list[Card],
    tts_config: TTSConfig,
    deck_config: DeckConfig,
    media_dir: Path,
    output_path: Path,
    *,
    require_audio: bool = True,
) -> Path:
    try:
        import genanki
    except ImportError as exc:
        raise RuntimeError("genanki is required; install dependencies from requirements.txt") from exc

    model = genanki.Model(
        deck_config.model_id,
        deck_config.model_name,
        fields=[
            {"name": "Arabic"},
            {"name": "English"},
            {"name": "ExampleArabic"},
            {"name": "ExampleEnglish"},
            {"name": "Audio"},
            {"name": "SourceID"},
        ],
        templates=[
            {
                "name": "Arabic → English",
                "qfmt": (
                    '<div class="arabic">{{Arabic}}</div>'
                    '{{#ExampleArabic}}<div class="example-arabic">{{ExampleArabic}}</div>{{/ExampleArabic}}'
                    '{{#Audio}}<div class="audio">{{Audio}}</div>{{/Audio}}'
                ),
                "afmt": (
                    '{{FrontSide}}<hr id="answer">'
                    '<div class="english">{{English}}</div>'
                    '{{#ExampleEnglish}}<div class="example-english">{{ExampleEnglish}}</div>{{/ExampleEnglish}}'
                ),
            },
            {
                "name": "English → Arabic",
                "qfmt": (
                    '<div class="english">{{English}}</div>'
                    '{{#ExampleEnglish}}<div class="example-english">{{ExampleEnglish}}</div>{{/ExampleEnglish}}'
                ),
                "afmt": (
                    '{{FrontSide}}<hr id="answer">'
                    '<div class="arabic">{{Arabic}}</div>'
                    '{{#ExampleArabic}}<div class="example-arabic">{{ExampleArabic}}</div>{{/ExampleArabic}}'
                    '{{#Audio}}<div class="audio">{{Audio}}</div>{{/Audio}}'
                ),
            },
        ],
        css=CARD_CSS,
        sort_field_index=0,
    )

    deck = genanki.Deck(deck_config.deck_id, deck_config.deck_name)
    media_files: list[str] = []

    for card in cards:
        filename = audio_filename(card, tts_config)
        media_path = media_dir / filename
        if not media_path.exists():
            if require_audio:
                raise FileNotFoundError(
                    f"Missing audio for card '{card.id}': {media_path}. Run generate-audio first."
                )
            audio_field = ""
        else:
            audio_field = f"[sound:{filename}]"
            media_files.append(str(media_path))

        note = genanki.Note(
            model=model,
            fields=[
                html.escape(card.arabic),
                html.escape(card.english),
                html.escape(card.example_arabic),
                html.escape(card.example_english),
                audio_field,
                html.escape(card.id),
            ],
            tags=list(card.tags),
            guid=genanki.guid_for(card.id),
        )
        deck.add_note(note)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    package = genanki.Package(deck)
    package.media_files = media_files
    package.write_to_file(str(output_path))
    return output_path
