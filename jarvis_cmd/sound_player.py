import os
import sys
import subprocess
import threading

class SoundPlayer:
    """Модуль воспроизведения фирменных звуков Старка / Джарвиса"""

    SOUND_MAP = {
        "activate": "Активационная.mp3",
        "time": "Время.mp3",
        "execute": "Выполняю.mp3",
        "done": "Готово.mp3",
        "diag": "Диагностика системы.mp3",
        "screen": "Информация на экране.mp3",
        "cursor": "Курсор смещен.mp3",
        "pause": "Пауза.mp3",
        "rewind": "Перемотал.mp3",
        "confirm": "Подтверждение.mp3",
        "watch": "Приятного просмотра.mp3",
        "thanks": "Спасибо.mp3",
        "brightness_up": "Увеличил яркость.mp3",
        "goodbye": "Удачи вам.mp3",
        "brightness_down": "Уменьшил яркость.mp3"
    }

    def __init__(self, sounds_dir=None):
        if sounds_dir is None:
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
                sounds_dir = os.path.join(base_dir, "assets", "sounds")
                if not os.path.exists(sounds_dir):
                    mei = getattr(sys, '_MEIPASS', os.path.join(base_dir, "_internal"))
                    sounds_dir = os.path.join(mei, "assets", "sounds")
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                sounds_dir = os.path.join(base_dir, "assets", "sounds")
        self.sounds_dir = sounds_dir
        self.cache_dir = os.path.join(self.sounds_dir, "tts_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.is_speaking = False
        self.mute_until = 0.0
        self._has_pygame = False
        try:
            import pygame
            pygame.mixer.init()
            self._has_pygame = True
        except Exception:
            self._has_pygame = False

    def is_busy(self):
        """Проверяет, звучит ли сейчас голос/звук Джарвиса или идет антиэхо пауза"""
        import time
        return self.is_speaking or (time.time() < self.mute_until)

    def play(self, sound_key, async_mode=True):
        """Воспроизводит звук по ключу или имени файла"""
        filename = self.SOUND_MAP.get(sound_key, sound_key)
        if not filename.endswith(".mp3"):
            filename += ".mp3"
        filepath = os.path.join(self.sounds_dir, filename)

        if not os.path.exists(filepath):
            print(f"[SoundPlayer] Файл не найден: {filepath}")
            return False

        if async_mode:
            threading.Thread(target=self._play_file, args=(filepath, True), daemon=True).start()
        else:
            self._play_file(filepath, async_mode=False)
        return True

    def _play_file(self, filepath, async_mode=True):
        import time
        self.is_speaking = True
        try:
            if self._has_pygame:
                import pygame
                snd = pygame.mixer.Sound(filepath)
                snd.set_volume(1.0)
                channel = snd.play()
                while channel and channel.get_busy():
                    pygame.time.Clock().tick(20)
            else:
                # Fallback: Windows Media Player via PowerShell
                ps_cmd = f'(New-Object Media.SoundPlayer "{filepath}").PlaySync();'
                if filepath.lower().endswith(".mp3"):
                    ps_cmd = f'$wm = New-Object -ComObject WMPlayer.OCX; $wm.URL = "{filepath}"; $wm.controls.play(); while($wm.playState -ne 1) {{ Start-Sleep -Milliseconds 100 }}'
                subprocess.run(["powershell", "-c", ps_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[SoundPlayer Error] {e}")
        finally:
            self.mute_until = time.time() + 0.3
            self.is_speaking = False

    def speak(self, text, async_mode=True):
        """Озвучивает произвольный текст живым мужским голосом Джарвиса"""
        if not text:
            return False
        print(f"[Jarvis Voice] «{text}»")
        if async_mode:
            threading.Thread(target=self._speak_sync, args=(text,), daemon=True).start()
        else:
            self._speak_sync(text)
        return True

    def _speak_sync(self, text):
        import time
        self.is_speaking = True
        try:
            import hashlib
            text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
            cache_file = os.path.join(self.cache_dir, f"{text_hash}.mp3")

            # 1. Попытка воспроизвести фирменный нейросетевой голос Джарвиса (DmitryNeural)
            if not os.path.exists(cache_file):
                try:
                    import edge_tts
                    import asyncio
                    communicate = edge_tts.Communicate(text, 'ru-RU-DmitryNeural', pitch='-4Hz', rate='+3%')
                    asyncio.run(communicate.save(cache_file))
                except Exception as e_edge:
                    print(f"[Neural TTS Warning] {e_edge}")

            if os.path.exists(cache_file) and self._has_pygame:
                import pygame
                snd = pygame.mixer.Sound(cache_file)
                snd.set_volume(1.0)
                channel = snd.play()
                while channel and channel.get_busy():
                    pygame.time.Clock().tick(20)
                return True

            # 2. Резервный оффлайн-синтез
            import comtypes.client
            speaker = comtypes.client.CreateObject('SAPI.SpVoice')
            for i in range(speaker.GetVoices().Count):
                v = speaker.GetVoices().Item(i)
                if 'irina' in v.GetDescription().lower() or 'russian' in v.GetDescription().lower():
                    speaker.Voice = v
                    break
            speaker.Speak(text)
            return True
        except Exception as e:
            print(f"[SoundPlayer Speak Error] {e}")
            return False
        finally:
            self.mute_until = time.time() + 0.3
            self.is_speaking = False
