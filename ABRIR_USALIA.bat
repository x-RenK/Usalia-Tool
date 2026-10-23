@echo off
cd /d "%~dp0"
python -m usalia gui
if errorlevel 1 pause
