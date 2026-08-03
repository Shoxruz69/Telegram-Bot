@echo off
cd /d "%~dp0"
echo ================================================
echo   CafeExpress Bot - Ishga tushirilmoqda...
echo ================================================
echo.

REM Avval barcha eski python jarayonlarini to'xtatish
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1
taskkill /f /im ngrok.exe >nul 2>&1

echo [1/3] Admin panel va Webhook server ishga tushirilmoqda...
start "Admin Panel (port 5000)" cmd /k "title Admin Panel ^& cd /d %~dp0 ^& venv\Scripts\activate.bat ^& python admin_app.py"

echo Bir oz kutilmoqda (server tayyor bo'lsin)...
timeout /t 3 /nobreak >nul

echo [2/3] Ngrok tunnel ishga tushirilmoqda...
start "Ngrok Tunnel" cmd /k "title Ngrok Tunnel ^& cd /d %~dp0 ^& venv\Scripts\activate.bat ^& python run_ngrok.py"

timeout /t 2 /nobreak >nul

echo [3/3] Telegram Bot ishga tushirilmoqda...
start "Telegram Bot" cmd /k "title Telegram Bot ^& cd /d %~dp0 ^& venv\Scripts\activate.bat ^& python bot.py"

echo.
echo ================================================
echo  Barchasi muvaffaqiyatli ishga tushirildi!
echo  Admin panel: http://127.0.0.1:5000/admin
echo ================================================
echo.
pause
