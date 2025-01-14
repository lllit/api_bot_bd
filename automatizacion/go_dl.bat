@echo off
cd /d D:\LLLIT\Code-W11\PY\api_bot_bd
call venv\Scripts\activate
python automatizacion\automatic_down_csv.py
python automatizacion\gitupdate.py
pause