@echo off
title Установка Jarvis - Автоматическая
color 0A

echo.
echo ========================================
echo   JARVIS - Автоматическая установка
echo ========================================
echo.
echo Это займет 15-20 минут
echo Не закрывай это окно!
echo.
pause

cd /d "%~dp0"

echo.
echo [1/4] Обновление pip...
python -m pip install --upgrade pip --quiet

echo [2/4] Установка Python зависимостей...
echo - pyttsx3 (синтез речи)
python -m pip install --user pyttsx3 --quiet
echo - pyaudio (микрофон)
python -m pip install --user pyaudio --quiet
echo - pvporcupine (wake word)
python -m pip install --user pvporcupine --quiet
echo - faster-whisper (распознавание)
python -m pip install --user faster-whisper --quiet
echo - anthropic (Claude API)
python -m pip install --user anthropic --quiet
echo - requests (HTTP)
python -m pip install --user "requests[socks]" --quiet
echo - pyyaml (конфиг)
python -m pip install --user pyyaml --quiet

echo.
echo [3/4] Проверка Ollama...
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama не установлен!
    echo.
    echo Запускаю установщик Ollama...
    echo После установки Ollama вернись сюда и нажми любую клавишу
    echo.
    start /wait "" "%USERPROFILE%\Downloads\OllamaSetup.exe"
    echo.
    echo Ожидание запуска Ollama...
    timeout /t 15 /nobreak
) else (
    echo Ollama уже установлен!
)

echo.
echo [4/4] Скачивание моделей Ollama...
echo Это займет ~10-15 минут (скачивается 8.5 GB)
echo.
echo - qwen2.5:7b (для общения)
ollama pull qwen2.5:7b
echo.
echo - deepseek-coder:6.7b (для кодинга)
ollama pull deepseek-coder:6.7b

echo.
echo ========================================
echo   УСТАНОВКА ЗАВЕРШЕНА!
echo ========================================
echo.
echo Jarvis готов к работе!
echo.
echo Запусти: start_voice_jarvis.bat
echo Скажи "Jarvis" и произнеси команду
echo.
echo Нажми любую клавишу для выхода...
pause >nul
