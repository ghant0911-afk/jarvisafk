@echo off
echo ========================================
echo   JARVIS - Голосовой ассистент
echo ========================================
echo.

cd /d "%~dp0"

echo Запускаю голосового Jarvis...
echo.
echo Скажи "Jarvis" для активации
echo Нажми Ctrl+C для выхода
echo.

python jarvis_voice.py

echo.
pause
