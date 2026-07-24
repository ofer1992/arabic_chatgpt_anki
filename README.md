# Arabic — ChatGPT Conversations

Builds the **Arabic — ChatGPT Conversations** Anki deck from JSONL cards and adds Palestinian/Jerusalem-style Arabic audio using Gemini 3.1 Flash TTS.

## Workflow

1. Add cards to `cards/cards.jsonl`.
2. Push the change to `main`, or run **Build Arabic Anki deck** manually under Actions.
3. GitHub Actions generates only missing audio, commits the MP3 cache, builds the deck with `genanki`, validates the package, and publishes `Arabic-ChatGPT-Conversations.apkg` in the `latest` GitHub Release.
4. Download and import that file into Anki.

The audio filename is derived from the transcript, model, voice, and complete TTS prompt. Unchanged cards reuse their audio; changing any pronunciation setting automatically creates a new clip.

## One-time setup

Open:

**Settings → Secrets and variables → Actions → New repository secret**

Create this secret:

- Name: `GEMINI_API_KEY`
- Value: your Google AI Studio API key

Then run:

**Actions → Build Arabic Anki deck → Run workflow**

The workflow requests `contents: write` so it can commit generated audio and publish the release. If GitHub blocks that, open **Settings → Actions → General → Workflow permissions** and select **Read and write permissions**.

## Card format

`cards/cards.jsonl` contains one JSON object per line:

```json
{"id":"2026-07-24-01","arabic":"مَعْنَوِيّاتي عالية","english":"My morale is high / I'm in high spirits","example_arabic":"معنوياتي عالية اليوم.","example_english":"My morale is high today.","tts_text":"مَعْنَوِيّاتي عالية\n\nمعنوياتي عالية اليوم.","tags":["chatgpt-conversation"]}
```

Required fields:

- `id`: stable, unique identifier. Never reuse an ID for a different card.
- `arabic`: target word or expression.
- `english`: English meaning.

Optional fields:

- `example_arabic`
- `example_english`
- `tts_text`: exact transcript sent to TTS. When omitted, it is constructed from `arabic`, a blank line, and `example_arabic`.
- `tags`: JSON array of strings.

The repository includes the phrase used to test Gemini AI Studio as its first card. Replace or extend it with the ten cards from each Arabic conversation.

Each source record creates two Anki cards:

- **Arabic → English:** the Arabic phrase, Arabic example, and audio are on the front; the English meaning and English example are on the back.
- **English → Arabic:** the English meaning and English example are on the front; the Arabic phrase, Arabic example, and audio are on the back.

Each example stays with its language, so the audio transcript matches the complete Arabic side.

## Exact Gemini request

The program sends the complete prompt as `input` to `gemini-3.1-flash-tts-preview`. Voice selection is a separate API parameter.

```python
interaction = client.interactions.create(
    model="gemini-3.1-flash-tts-preview",
    input=prompt,
    response_format={"type": "audio"},
    generation_config={
        "speech_config": [{"voice": "Kore"}],
    },
)
```

The exact Audio Profile and Scene are stored in `config/tts.json`. The prompt generated for each card is:

```text
Read the following transcript based on the audio profile.

# Audio Profile
Read only the supplied Arabic text. Speak in a natural urban Palestinian Arabic accent from Jerusalem. Use casual everyday pronunciation, not Modern Standard Arabic. Speak clearly and slightly slowly, like a patient language tutor. Do not add, remove, translate, or reformulate any words.

## Scene:
A tutor recording a flashcard audio for a lesson in Palestinian arabic

## Transcript:
<the card's tts_text>
```

`Kore` is the default voice. Change `voice` in `config/tts.json` if the voice you selected in AI Studio was different.

## Local use

Requires Python 3.11+ and `ffmpeg`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
export GEMINI_API_KEY='...'

python -m arabic_anki check
python -m arabic_anki show-prompt 2026-07-24-morale
python -m arabic_anki generate-audio
python -m arabic_anki build
python -m arabic_anki validate
```

The generated deck is written to `dist/Arabic-ChatGPT-Conversations.apkg`.

## Stable Anki updates

The deck name is fixed as **Arabic — ChatGPT Conversations**. The deck ID and model ID are fixed in `config/deck.json`. Each note GUID is derived only from its stable card `id`, so editing a translation, example, or audio clip does not create a duplicate note on later imports.
