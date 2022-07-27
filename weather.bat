@echo off
cd %~dp0
call env\Scripts\activate
python weather.py
