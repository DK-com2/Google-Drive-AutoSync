@echo off
cd /d "S:\python\BirdNET-AutoPipeline"

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Execute main program
python src\main.py

REM Exit automatically without pause
exit /b %ERRORLEVEL%
