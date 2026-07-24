from dataclasses import dataclass

from arabic_anki.config import TTSConfig
from arabic_anki.tts import _request_audio


CONFIG = TTSConfig(
    model="gemini-3.1-flash-tts-preview",
    voice="Kore",
    sample_rate_hz=24000,
    prompt_version=1,
    audio_profile="profile",
    scene="scene",
)


@dataclass
class FakeInteractions:
    kwargs: dict | None = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return object()


@dataclass
class FakeClient:
    interactions: FakeInteractions


def test_interactions_api_request_shape() -> None:
    interactions = FakeInteractions()
    client = FakeClient(interactions)

    _request_audio(client, "exact prompt", CONFIG)

    assert interactions.kwargs == {
        "model": "gemini-3.1-flash-tts-preview",
        "input": "exact prompt",
        "response_format": {"type": "audio"},
        "generation_config": {
            "speech_config": [{"voice": "Kore"}],
        },
    }
