@echo off
cd /d D:\LLLIT\Code-W11\PY\api_bot_bd
call venv\Scripts\activate
python automatizacion\automatic_down_csv.py

start python main.py
timeout /t 10 /nobreak

for /f "tokens=2" %%i in ('tasklist ^| findstr python.exe') do set UVICORN_PID=%%i
taskkill /PID %UVICORN_PID% /F

taskkill /IM python.exe /F
python automatizacion\gitupdate.py
pause