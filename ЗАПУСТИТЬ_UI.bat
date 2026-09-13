@echo off
title JarvisUltra v4.0
cd /d "C:\Users\bear_\.gemini\antigravity\scratch\JarvisUltra_Flash"
echo ================================
echo   ?????? JarvisUltra v4.0
echo ================================
pip install plyer --quiet 2>nul
python jarvis_ultra_ui.py
if errorlevel 1 (
    echo.
    echo === ?????? === ?????? ????
    pause
)
