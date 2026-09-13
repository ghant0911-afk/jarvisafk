@echo off
echo ========================================
echo   Установка Ollama для Jarvis
echo ========================================
echo.

echo Запускаю установщик Ollama...
start /wait "" "%USERPROFILE%\Downloads\OllamaSetup.exe"

echo.
echo Ожидание запуска Ollama...
timeout /t 10 /nobreak

echo.
echo Скачиваю модель deepseek-coder:6.7b для кодинга...
ollama pull deepseek-coder:6.7b

echo.
echo Скачиваю модель qwen2.5:7b для общения...
ollama pull qwen2.5:7b

echo.
echo ========================================
echo   Установка завершена!
echo ========================================
echo.
echo Проверка:
ollama list

echo.
pause
