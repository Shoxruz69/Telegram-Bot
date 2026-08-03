@echo off
cd /d "%~dp0"
taskkill /f /im pythonw.exe >nul 2>&1
start "" "venv\Scripts\pythonw.exe" admin_app.py
start "" "venv\Scripts\pythonw.exe" bot.py
echo Ilovalar orqa fonda ishga tushirildi!
