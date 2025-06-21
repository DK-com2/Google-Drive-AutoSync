@echo off
chcp 65001 > nul
cd /d "S:\python\BirdNET-AutoPipeline"

echo ========================================
echo    BirdNET AutoPipeline 実行開始
echo ========================================
echo 実行時刻: %date% %time%
echo.

REM Python仮想環境があれば使用
if exist "venv\Scripts\activate.bat" (
    echo 仮想環境を有効化中...
    call venv\Scripts\activate.bat
)

REM メインプログラム実行
echo プログラム実行中...
python src\main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo    処理が正常に完了しました
    echo ========================================
) else (
    echo.
    echo ========================================
    echo    エラーが発生しました (Code: %ERRORLEVEL%)
    echo ========================================
    echo ログファイルを確認してください:
    echo   S:\python\BirdNET-AutoPipeline\logs\
    echo.
)

echo 終了時刻: %date% %time%
echo.
echo キーを押すと終了します...
pause > nul
