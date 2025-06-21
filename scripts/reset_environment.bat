@echo off
chcp 65001 > nul
cd /d "S:\python\BirdNET-AutoPipeline"

echo ========================================
echo    BirdNET AutoPipeline RESET TOOL
echo ========================================
echo.
echo This will DELETE:
echo   - Downloaded audio files (data\downloads\)
echo   - Analysis results (data\results\)
echo   - Log files (logs\)
echo   - Processing state files
echo.
echo This will KEEP:
echo   - Configuration files (config\)
echo   - Google authentication (credentials.json, token.pickle)
echo   - Main program files (src\)
echo.
echo ========================================
echo WARNING: This action cannot be undone!
echo ========================================
set /p confirm="Are you sure you want to reset? (y/N): "

if /i not "%confirm%"=="y" (
    echo.
    echo Reset cancelled.
    echo.
    pause
    exit /b 0
)

echo.
echo Starting reset process...
echo.

REM Delete downloaded files
if exist "data\downloads\*" (
    echo Deleting downloaded files...
    del /q "data\downloads\*" 2>nul
    echo   - Downloaded files deleted
) else (
    echo   - No downloaded files to delete
)

REM Delete analysis results
if exist "data\results\*" (
    echo Deleting analysis results...
    del /q "data\results\*" 2>nul
    echo   - Analysis results deleted
) else (
    echo   - No analysis results to delete
)

REM Delete log files
if exist "logs\*" (
    echo Deleting log files...
    del /q "logs\*" 2>nul
    echo   - Log files deleted
) else (
    echo   - No log files to delete
)

REM Delete state files
echo Resetting processing state...
if exist "data\processed_files.txt" (
    del /q "data\processed_files.txt" 2>nul
    echo   - Processed files list cleared
)

if exist "data\page_token.txt" (
    del /q "data\page_token.txt" 2>nul
    echo   - Page token reset (will check all files on next run)
)

if exist "data\last_run.txt" (
    del /q "data\last_run.txt" 2>nul
    echo   - Last run time cleared
)

if exist "data\error_flag.txt" (
    del /q "data\error_flag.txt" 2>nul
    echo   - Error flag cleared
)

REM Clean temp directory
if exist "data\temp\*" (
    echo Cleaning temporary files...
    del /q "data\temp\*" 2>nul
    echo   - Temporary files cleaned
)

echo.
echo ========================================
echo    RESET COMPLETED SUCCESSFULLY
echo ========================================
echo.
echo The system has been reset to initial state.
echo Next run will process all files in Google Drive folder.
echo.
echo Configuration and authentication preserved:
echo   - config\config.json (settings)
echo   - config\credentials.json (Google auth)
echo   - data\token.pickle (auth token)
echo.
echo Press any key to exit...
pause > nul
