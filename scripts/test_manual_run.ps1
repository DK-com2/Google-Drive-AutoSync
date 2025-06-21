# BirdNET AutoPipeline TEST PowerShell script
# This script shows output for manual testing

param(
    [switch]$Silent = $false  # Default to verbose mode for testing
)

# Set encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Move to project directory
Set-Location "S:\python\BirdNET-AutoPipeline"

Write-Host "========================================"
Write-Host "   BirdNET AutoPipeline TEST EXECUTION"
Write-Host "========================================"
Write-Host "Execute Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""
Write-Host "This is a TEST run - output will be displayed"
Write-Host "Normal scheduled runs will be silent"
Write-Host "========================================"
Write-Host ""

try {
    # Check and activate virtual environment
    if (Test-Path "venv\Scripts\Activate.ps1") {
        Write-Host "Activating virtual environment..."
        & "venv\Scripts\Activate.ps1"
    }
    
    # Execute main program
    Write-Host "Running program..."
    Write-Host ""
    
    $result = & python "src\main.py" 2>&1
    Write-Host $result
    
    Write-Host ""
    Write-Host "========================================"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   TEST COMPLETED SUCCESSFULLY"
        
        # Check result files
        $resultFiles = Get-ChildItem "data\results" -Filter "*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 3
        
        if ($resultFiles) {
            Write-Host ""
            Write-Host "Latest analysis results:"
            foreach ($file in $resultFiles) {
                Write-Host "  - $($file.Name) ($(Get-Date $file.LastWriteTime -Format 'MM-dd HH:mm'))"
            }
        }
        
    } else {
        Write-Host "   TEST FAILED (Error Code: $LASTEXITCODE)"
        Write-Host "   Check log files in logs\ folder"
        
        # Check error flag file
        $errorFlag = "data\error_flag.txt"
        if (Test-Path $errorFlag) {
            $errorContent = Get-Content $errorFlag -Raw -ErrorAction SilentlyContinue
            Write-Host ""
            Write-Host "Error details:"
            Write-Host "  $errorContent"
        }
    }
    Write-Host "========================================"
    Write-Host "End Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host ""
    Write-Host "Press Enter to close..."
    Read-Host
    
} catch {
    Write-Host ""
    Write-Host "========================================"
    Write-Host "   Unexpected error occurred"
    Write-Host "========================================"
    Write-Host "Error: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Press Enter to close..."
    Read-Host
    exit 1
}
