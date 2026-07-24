from arabic_anki.cards import Card
from arabic_anki.config import TTSConfig
from arabic_anki.prompt import audio_filename, build_tts_prompt


CONFIG = TTSConfig(
    model="gemini-3.1-flash-tts-preview",
    voice="Kore",
    sample_rate_hz=24000,
    prompt_version=1,
    audio_profile=(
        "Read only the supplied Arabic text. Speak in a natural urban Palestinian Arabic accent "
        "from Jerusalem. Use casual everyday pronunciation, not Modern Standard Arabic. Speak "
        "clearly and slightly slowly, like a patient language tutor. Do not add, remove, translate, "
        "or reformulate any words."
    ),
    scene="A tutor recording a flashcard audio for a lesson in Palestinian arabic",
)


def test_prompt_matches_ai_studio_shape() -> None:
    prompt = build_tts_prompt("مَعْنَوِيّاتي عالية\n\nمعنوياتي عالية اليوم.", CONFIG)
    assert prompt == (
        "Read the following transcript based on the audio profile.\n\n"
        "# Audio Profile\n"
        "Read only the supplied Arabic text. Speak in a natural urban Palestinian Arabic accent "
        "from Jerusalem. Use casual everyday pronunciation, not Modern Standard Arabic. Speak "
        "clearly and slightly slowly, like a patient language tutor. Do not add, remove, translate, "
        "or reformulate any words.\n\n"
        "## Scene:\n"
        "A tutor recording a flashcard audio for a lesson in Palestinian arabic\n\n"
        "## Transcript:\n"
        "مَعْنَوِيّاتي عالية\n\n"
        "معنوياتي عالية اليوم."
    )


def test_audio_filename_is_stable_and_content_addressed() -> None:
    card = Card(id="x", arabic="مرحبا", english="hello", tts_text="مرحبا")
    assert audio_filename(card, CONFIG) == audio_filename(card, CONFIG)
    changed = Card(id="x", arabic="مرحبا", english="hello", tts_text="مرحبا يا صاحبي")
    assert audio_filename(card, CONFIG) != audio_filename(changed, CONFIG)
