# BirdNET AutoPipeline PowerShell execution script
param(
    [switch]$Silent = $true  # Default to silent mode for scheduled execution
)

# Set encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Move to project directory
Set-Location "S:\python\BirdNET-AutoPipeline"

try {
    # Check and activate virtual environment
    if (Test-Path "venv\Scripts\Activate.ps1") {
        & "venv\Scripts\Activate.ps1"
    }
    
    # Execute main program
    $result = & python "src\main.py" 2>&1
    
    # Exit with the same error code as python
    exit $LASTEXITCODE
    
} catch {
    # Exit with error code 1 if exception occurs
    exit 1
}
