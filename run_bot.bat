@echo off
title GymBot Runner
cd /d "%~dp0"

REM Optional: activate virtual environment if you're using one
REM call venv\Scripts\activate.bat

echo Starting GymBot...
python main.py

echo(
echo Bot exited.
pause
