"""
Главный модуль голосового Jarvis с wake word detection
"""
import os
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

from jarvis_cmd.wake_word import WakeWordDetector
from jarvis_cmd.tts import VoiceSynthesizer
from jarvis_cmd.speech import transcribe_audio
from jarvis_cmd.brain import plan_command
from jarvis_cmd.executor import run_command
from jarvis_cmd.safety import check_command
from jarvis_cmd.logger import get_logger
from jarvis_cmd.colors import green, red, yellow, blue, cyan

import pyaudio
import wave
import tempfile

logger = get_logger()


class VoiceJarvis:
    """Голосовой ассистент Jarvis с wake word detection."""

    def __init__(self):
        self.wake_detector = WakeWordDetector(sensitivity=0.5)
        self.tts = VoiceSynthesizer(rate=160, volume=0.9)
        self.running = False

        print(cyan("=" * 70))
        print(cyan("                    JARVIS - Голосовой ассистент"))
        print(cyan("=" * 70))
        print()

    def record_command(self, duration: int = 5) -> str:
        """
        Записать голосовую команду.

        Args:
            duration: Длительность записи в секундах

        Returns:
            Распознанный текст
        """
        print(yellow("🎤 Слушаю команду..."))

        # Параметры записи
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000

        p = pyaudio.PyAudio()

        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        frames = []

        # Запись
        for i in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Сохранение во временный файл
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            temp_path = f.name

        wf = wave.open(temp_path, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        # Распознавание
        try:
            text = transcribe_audio(temp_path)
            os.unlink(temp_path)
            return text
        except Exception as e:
            os.unlink(temp_path)
            raise e

    def execute_command(self, user_text: str):
        """Выполнить голосовую команду."""
        print(blue(f"📝 Распознано: {user_text}"))
        logger.info(f"Voice command: {user_text}")

        try:
            # Планирование
            plan = plan_command(user_text)
            print(cyan(f"🧠 План: {plan.reason}"))

            # Если это просто ответ
            if plan.intent in ("chat", "answer") or not plan.command:
                self.tts.speak(plan.reason)
                return

            # Проверка безопасности
            decision = check_command(plan.command)

            if not decision.allowed:
                message = f"Команда заблокирована. {decision.reason}"
                print(red(f"⛔ {message}"))
                self.tts.speak(message)
                return

            if decision.requires_confirmation:
                message = "Команда требует подтверждения. Используй CLI для выполнения."
                print(yellow(f"⚠️ {message}"))
                self.tts.speak(message)
                return

            # Выполнение
            print(green(f"⚙️ Выполняю: {plan.command}"))
            self.tts.speak("Выполняю команду")

            result = run_command(plan.command)

            if result.exit_code == 0:
                message = "Команда выполнена успешно"
                print(green(f"✅ {message}"))
                self.tts.speak(message)

                # Показать вывод если есть
                if result.stdout:
                    print(result.stdout[:500])
            else:
                message = f"Ошибка выполнения. Код: {result.exit_code}"
                print(red(f"❌ {message}"))
                self.tts.speak(message)

                if result.stderr:
                    print(red(result.stderr[:500]))

        except Exception as e:
            message = f"Ошибка: {e}"
            print(red(f"❌ {message}"))
            self.tts.speak("Произошла ошибка")
            logger.error(f"Voice command error: {e}", exc_info=True)

    def run(self):
        """Запустить голосового ассистента."""
        self.running = True

        print(green("✅ Jarvis активирован"))
        print(yellow("💡 Скажи 'Jarvis' для активации"))
        print(yellow("💡 Нажми Ctrl+C для выхода"))
        print()

        self.tts.speak("Джарвис активирован")

        try:
            self.wake_detector.start()

            while self.running:
                # Ждем wake word
                if self.wake_detector.listen():
                    print(green("✅ Активирован! Слушаю команду..."))
                    self.tts.speak("Слушаю")

                    try:
                        # Записываем команду
                        command_text = self.record_command(duration=5)

                        if command_text.strip():
                            self.execute_command(command_text)
                        else:
                            print(yellow("⚠️ Команда не распознана"))
                            self.tts.speak("Не расслышал команду")

                    except Exception as e:
                        print(red(f"❌ Ошибка записи: {e}"))
                        self.tts.speak("Ошибка записи")

                    print()
                    print(yellow("💡 Скажи 'Jarvis' для новой команды"))
                    print()

        except KeyboardInterrupt:
            print()
            print(yellow("👋 Остановка Jarvis..."))
            self.tts.speak("До свидания")
        finally:
            self.wake_detector.stop()
            self.running = False


def main():
    """Точка входа."""
    jarvis = VoiceJarvis()
    jarvis.run()


if __name__ == "__main__":
    main()
