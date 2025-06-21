# PowerShell実行ポリシー設定
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# BirdNET AutoPipeline PowerShell実行スクリプト
param(
    [switch]$Silent = $false
)

# 文字エンコーディング設定
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# プロジェクトディレクトリに移動
Set-Location "S:\python\BirdNET-AutoPipeline"

if (-not $Silent) {
    Write-Host "========================================"
    Write-Host "   BirdNET AutoPipeline 実行開始"
    Write-Host "========================================"
    Write-Host "実行時刻: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host ""
}

try {
    # 仮想環境の確認と有効化
    if (Test-Path "venv\Scripts\Activate.ps1") {
        if (-not $Silent) { Write-Host "仮想環境を有効化中..." }
        & "venv\Scripts\Activate.ps1"
    }
    
    # メインプログラム実行
    if (-not $Silent) { Write-Host "プログラム実行中..." }
    
    $result = & python "src\main.py" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        if (-not $Silent) {
            Write-Host ""
            Write-Host "========================================"
            Write-Host "   処理が正常に完了しました"
            Write-Host "========================================"
        }
        
        # 結果ファイルの確認
        $resultFiles = Get-ChildItem "data\results" -Filter "*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 3
        
        if ($resultFiles -and -not $Silent) {
            Write-Host ""
            Write-Host "最新の解析結果:"
            foreach ($file in $resultFiles) {
                Write-Host "  - $($file.Name) ($(Get-Date $file.LastWriteTime -Format 'MM-dd HH:mm'))"
            }
        }
        
    } else {
        Write-Host ""
        Write-Host "========================================"
        Write-Host "   エラーが発生しました (Code: $LASTEXITCODE)"
        Write-Host "========================================"
        Write-Host "ログファイルを確認してください:"
        Write-Host "  S:\python\BirdNET-AutoPipeline\logs\"
        
        # エラーフラグファイルの確認
        $errorFlag = "data\error_flag.txt"
        if (Test-Path $errorFlag) {
            $errorContent = Get-Content $errorFlag -Raw
            Write-Host ""
            Write-Host "エラー詳細:"
            Write-Host "  $errorContent"
        }
        
        if (-not $Silent) {
            Write-Host ""
            Write-Host "Enterキーを押して続行..."
            Read-Host
        }
    }
    
} catch {
    Write-Host ""
    Write-Host "========================================"
    Write-Host "   予期しないエラーが発生しました"
    Write-Host "========================================"
    Write-Host "エラー: $($_.Exception.Message)"
    
    if (-not $Silent) {
        Write-Host ""
        Write-Host "Enterキーを押して続行..."
        Read-Host
    }
}

if (-not $Silent) {
    Write-Host ""
    Write-Host "終了時刻: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
}
