import base64

from arabic_anki.tts import _decode_audio_data


def test_decode_base64_audio() -> None:
    pcm = b"\x01\x02\x03\x04"
    assert _decode_audio_data(base64.b64encode(pcm).decode()) == pcm


def test_preserve_wave_data() -> None:
    wav = b"RIFF" + b"\x00" * 20
    assert _decode_audio_data(wav) == wav
