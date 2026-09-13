@echo off
echo ========================================
echo   Автоматическая установка Jarvis
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Установка Python зависимостей...
python -m pip install --upgrade pip
python -m pip install pyttsx3
python -m pip install pyaudio
python -m pip install pvporcupine
python -m pip install faster-whisper
python -m pip install anthropic
python -m pip install "requests[socks]"
python -m pip install pyyaml

echo.
echo [2/3] Проверка установки Ollama...
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama не найден. Устанавливаю...
    start /wait "" "%USERPROFILE%\Downloads\OllamaSetup.exe"
    timeout /t 10 /nobreak
) else (
    echo Ollama уже установлен
)

echo.
echo [3/3] Скачивание моделей Ollama...
ollama pull qwen2.5:7b
ollama pull deepseek-coder:6.7b

echo.
echo ========================================
echo   Установка завершена!
echo ========================================
echo.
echo Запусти: start_voice_jarvis.bat
echo.
pause
