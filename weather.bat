@echo off
set curdir=%cd%
cd %~dp0
call env\Scripts\activate
python weather.py
call deactivate
cd %curdir%