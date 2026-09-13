@echo off
echo ========================================
echo   Установка зависимостей Jarvis
echo ========================================
echo.

cd /d "%~dp0"

echo Устанавливаю Python зависимости...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ========================================
echo   Установка завершена!
echo ========================================
echo.
pause
