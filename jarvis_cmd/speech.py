from __future__ import annotations

from pathlib import Path


class SpeechError(RuntimeError):
    """Raised when speech transcription is unavailable or failed."""


def transcribe_audio(file_path: str) -> str:
    """
    Transcribe an audio file into text using faster-whisper.

    Requires:
    - faster-whisper package installed
    """
    path = Path(file_path)
    if not path.exists():
        raise SpeechError("Аудиофайл не найден.")

    try:
        from faster_whisper import WhisperModel
    except Exception as exc:  # pragma: no cover - optional dependency
        raise SpeechError(
            "Распознавание голоса недоступно: установи faster-whisper."
        ) from exc

    model_name = "small"
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, _info = model.transcribe(str(path), language="ru")
    text = " ".join(segment.text.strip() for segment in segments).strip()
    if not text:
        raise SpeechError("Не удалось распознать речь в сообщении.")
    return text
