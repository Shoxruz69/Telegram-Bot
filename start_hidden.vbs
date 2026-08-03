Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c cd /d ""C:\Users\avt\Desktop\Telegram bot"" && venv\Scripts\python.exe admin_app.py > admin_stdout.log 2> admin_stderr.log", 0, False
WshShell.Run "cmd /c cd /d ""C:\Users\avt\Desktop\Telegram bot"" && venv\Scripts\python.exe bot.py > bot_stdout.log 2> bot_stderr.log", 0, False
