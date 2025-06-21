@echo off
chcp 65001 > nul
cd /d "S:\python\BirdNET-AutoPipeline"

echo ========================================
echo    BirdNET AutoPipeline TEST EXECUTION
echo ========================================
echo Execute Time: %date% %time%
echo.
echo This is a TEST run - output will be displayed
echo Normal scheduled runs will be silent
echo ========================================
echo.

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Execute main program
echo Running program...
echo.
python src\main.py

echo.
echo ========================================
if %ERRORLEVEL% EQU 0 (
    echo    TEST COMPLETED SUCCESSFULLY
) else (
    echo    TEST FAILED (Error Code: %ERRORLEVEL%)
    echo    Check log files in logs\ folder
)
echo ========================================
echo End Time: %date% %time%
echo.
echo Press any key to close...
pause > nul
