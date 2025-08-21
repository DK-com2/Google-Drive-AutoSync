@echo off
chcp 65001 > nul
cd /d "%~dp0"

REM 仮想環境がある場合は使用
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe main.py
) else (
    python main.py
)