# Stop existing instances of bot.py and admin_app.py
Get-Process | Where-Object { $_.CommandLine -like "*bot.py*" -or $_.CommandLine -like "*admin_app.py*" } | ForEach-Object {
    Write-Host "Stopping process: $($_.Id)"
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

$ScriptDir = "C:\Users\avt\Desktop\Telegram bot"
$PythonPath = "$ScriptDir\venv\Scripts\pythonw.exe"

# Start admin_app.py persistently
Start-Process -FilePath $PythonPath -ArgumentList "admin_app.py" -WindowStyle Hidden -WorkingDirectory "$ScriptDir"
Write-Host "admin_app.py has been started persistently."

# Start bot.py persistently
Start-Process -FilePath $PythonPath -ArgumentList "bot.py" -WindowStyle Hidden -WorkingDirectory "$ScriptDir"
Write-Host "bot.py has been started persistently."
