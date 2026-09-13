"""
Синтез речи (TTS) для голосовых ответов Jarvis
Использует pyttsx3 для офлайн синтеза речи
"""
import pyttsx3
from typing import Optional


class VoiceSynthesizer:
    """Синтезатор речи для Jarvis."""

    def __init__(self, rate: int = 150, volume: float = 0.9, voice_id: Optional[str] = None):
        """
        Args:
            rate: Скорость речи (слов в минуту)
            volume: Громкость (0.0 - 1.0)
            voice_id: ID голоса (None = по умолчанию)
        """
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)

        # Установка голоса
        if voice_id:
            self.engine.setProperty('voice', voice_id)
        else:
            # Попытка найти русский голос
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'russian' in voice.name.lower() or 'ru' in voice.languages:
                    self.engine.setProperty('voice', voice.id)
                    break

    def speak(self, text: str, wait: bool = True):
        """
        Произнести текст.

        Args:
            text: Текст для произнесения
            wait: Ждать завершения произнесения
        """
        self.engine.say(text)
        if wait:
            self.engine.runAndWait()

    def speak_async(self, text: str):
        """Произнести текст асинхронно."""
        self.speak(text, wait=False)

    def stop(self):
        """Остановить текущее произнесение."""
        self.engine.stop()

    def list_voices(self):
        """Вывести список доступных голосов."""
        voices = self.engine.getProperty('voices')
        print("Доступные голоса:")
        for i, voice in enumerate(voices):
            print(f"{i}. {voice.name} ({voice.id})")
            print(f"   Языки: {voice.languages}")
            print(f"   Пол: {voice.gender}")
            print()


def speak(text: str, rate: int = 150, volume: float = 0.9):
    """
    Быстрая функция для произнесения текста.

    Args:
        text: Текст для произнесения
        rate: Скорость речи
        volume: Громкость
    """
    synthesizer = VoiceSynthesizer(rate=rate, volume=volume)
    synthesizer.speak(text)


if __name__ == "__main__":
    # Тест
    print("Тестирование синтеза речи...")

    synth = VoiceSynthesizer()

    print("\nДоступные голоса:")
    synth.list_voices()

    print("\nТест произнесения:")
    synth.speak("Привет! Я Джарвис, твой голосовой ассистент.")
    synth.speak("Готов выполнять команды.")
