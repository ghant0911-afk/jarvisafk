"""
Голосовое управление с активацией по имени "Jarvis"
Использует pvporcupine для wake word detection
"""
import os
import struct
import pyaudio
from pathlib import Path

try:
    import pvporcupine
    PORCUPINE_AVAILABLE = True
except ImportError:
    PORCUPINE_AVAILABLE = False


class WakeWordDetector:
    """Детектор wake word 'Jarvis'."""

    def __init__(self, sensitivity: float = 0.5):
        """
        Args:
            sensitivity: Чувствительность (0.0 - 1.0)
        """
        if not PORCUPINE_AVAILABLE:
            raise ImportError("pvporcupine не установлен. Установи: pip install pvporcupine")

        self.sensitivity = sensitivity
        self.porcupine = None
        self.audio_stream = None
        self.pa = None

    def start(self):
        """Запустить детектор."""
        # Инициализация Porcupine с встроенным wake word "jarvis"
        self.porcupine = pvporcupine.create(
            keywords=["jarvis"],
            sensitivities=[self.sensitivity]
        )

        # Инициализация PyAudio
        self.pa = pyaudio.PyAudio()
        self.audio_stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

    def listen(self) -> bool:
        """
        Слушать микрофон и детектировать wake word.

        Returns:
            True если обнаружено "Jarvis"
        """
        if not self.audio_stream:
            raise RuntimeError("Детектор не запущен. Вызови start() сначала.")

        pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

        keyword_index = self.porcupine.process(pcm)
        return keyword_index >= 0

    def stop(self):
        """Остановить детектор."""
        if self.audio_stream:
            self.audio_stream.close()
        if self.pa:
            self.pa.terminate()
        if self.porcupine:
            self.porcupine.delete()


def listen_for_wake_word(sensitivity: float = 0.5, callback=None):
    """
    Постоянно слушать wake word "Jarvis".

    Args:
        sensitivity: Чувствительность детектора
        callback: Функция, вызываемая при обнаружении wake word
    """
    print("🎤 Слушаю wake word 'Jarvis'...")
    print("💡 Скажи 'Jarvis' чтобы активировать")

    detector = WakeWordDetector(sensitivity=sensitivity)

    try:
        detector.start()

        while True:
            if detector.listen():
                print("✅ Wake word обнаружен!")
                if callback:
                    callback()

    except KeyboardInterrupt:
        print("\n👋 Остановка детектора...")
    finally:
        detector.stop()


if __name__ == "__main__":
    def on_wake_word():
        print("🤖 Jarvis активирован! Слушаю команду...")

    listen_for_wake_word(callback=on_wake_word)
