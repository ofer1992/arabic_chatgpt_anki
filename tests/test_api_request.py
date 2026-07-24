from dataclasses import dataclass

from google import genai

from arabic_anki.config import TTSConfig
from arabic_anki.tts import _create_client, _request_audio


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


def test_client_uses_bounded_rate_limit_backoff(monkeypatch) -> None:
    captured: dict = {}

    def fake_client(**kwargs):
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(genai, "Client", fake_client)

    _create_client("secret")

    assert captured["api_key"] == "secret"
    retry = captured["http_options"].retry_options
    assert retry.attempts == 4
    assert retry.initial_delay == 30.0
    assert retry.max_delay == 60.0
    assert retry.exp_base == 2.0
    assert retry.jitter == 5.0


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
