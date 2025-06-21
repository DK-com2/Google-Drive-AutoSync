# BirdNET AutoPipeline Environment Reset Script
# PowerShell version with detailed output

param(
    [switch]$Force = $false  # Skip confirmation if -Force is used
)

# Set encoding and location
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Set-Location "S:\python\BirdNET-AutoPipeline"

Write-Host "========================================"
Write-Host "   BirdNET AutoPipeline RESET TOOL"
Write-Host "========================================"
Write-Host ""

# Show what will be deleted
Write-Host "This will DELETE:" -ForegroundColor Yellow
Write-Host "  - Downloaded audio files (data\downloads\)" -ForegroundColor Red
Write-Host "  - Analysis results (data\results\)" -ForegroundColor Red  
Write-Host "  - Log files (logs\)" -ForegroundColor Red
Write-Host "  - Processing state files" -ForegroundColor Red
Write-Host ""

Write-Host "This will KEEP:" -ForegroundColor Green
Write-Host "  - Configuration files (config\)" -ForegroundColor Green
Write-Host "  - Google authentication files" -ForegroundColor Green
Write-Host "  - Main program files (src\)" -ForegroundColor Green
Write-Host ""

# Count files to be deleted
$downloadCount = (Get-ChildItem "data\downloads" -File -ErrorAction SilentlyContinue).Count
$resultCount = (Get-ChildItem "data\results" -File -ErrorAction SilentlyContinue).Count
$logCount = (Get-ChildItem "logs" -File -ErrorAction SilentlyContinue).Count

Write-Host "Files to be deleted:"
Write-Host "  - Downloads: $downloadCount files"
Write-Host "  - Results: $resultCount files"
Write-Host "  - Logs: $logCount files"
Write-Host ""

# Confirmation
if (-not $Force) {
    Write-Host "========================================"
    Write-Host "WARNING: This action cannot be undone!" -ForegroundColor Red
    Write-Host "========================================"
    $confirm = Read-Host "Are you sure you want to reset? (y/N)"
    
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host ""
        Write-Host "Reset cancelled." -ForegroundColor Yellow
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 0
    }
}

Write-Host ""
Write-Host "Starting reset process..." -ForegroundColor Cyan
Write-Host ""

$deletedCount = 0

try {
    # Delete downloaded files
    if (Test-Path "data\downloads\*") {
        Write-Host "Deleting downloaded files..." -ForegroundColor Yellow
        $files = Get-ChildItem "data\downloads" -File
        foreach ($file in $files) {
            Remove-Item $file.FullName -Force
            Write-Host "  - Deleted: $($file.Name)" -ForegroundColor Gray
            $deletedCount++
        }
    } else {
        Write-Host "  - No downloaded files to delete" -ForegroundColor Gray
    }

    # Delete analysis results
    if (Test-Path "data\results\*") {
        Write-Host "Deleting analysis results..." -ForegroundColor Yellow
        $files = Get-ChildItem "data\results" -File
        foreach ($file in $files) {
            Remove-Item $file.FullName -Force
            Write-Host "  - Deleted: $($file.Name)" -ForegroundColor Gray
            $deletedCount++
        }
    } else {
        Write-Host "  - No analysis results to delete" -ForegroundColor Gray
    }

    # Delete log files
    if (Test-Path "logs\*") {
        Write-Host "Deleting log files..." -ForegroundColor Yellow
        $files = Get-ChildItem "logs" -File
        foreach ($file in $files) {
            Remove-Item $file.FullName -Force
            Write-Host "  - Deleted: $($file.Name)" -ForegroundColor Gray
            $deletedCount++
        }
    } else {
        Write-Host "  - No log files to delete" -ForegroundColor Gray
    }

    # Delete state files
    Write-Host "Resetting processing state..." -ForegroundColor Yellow
    
    $stateFiles = @(
        "data\processed_files.txt",
        "data\page_token.txt", 
        "data\last_run.txt",
        "data\error_flag.txt"
    )
    
    foreach ($file in $stateFiles) {
        if (Test-Path $file) {
            Remove-Item $file -Force
            Write-Host "  - Deleted: $(Split-Path $file -Leaf)" -ForegroundColor Gray
            $deletedCount++
        }
    }

    # Clean temp directory
    if (Test-Path "data\temp\*") {
        Write-Host "Cleaning temporary files..." -ForegroundColor Yellow
        $files = Get-ChildItem "data\temp" -File
        foreach ($file in $files) {
            Remove-Item $file.FullName -Force
            Write-Host "  - Deleted: $($file.Name)" -ForegroundColor Gray
            $deletedCount++
        }
    } else {
        Write-Host "  - No temporary files to clean" -ForegroundColor Gray
    }

    Write-Host ""
    Write-Host "========================================"
    Write-Host "   RESET COMPLETED SUCCESSFULLY" -ForegroundColor Green
    Write-Host "========================================"
    Write-Host ""
    Write-Host "Summary:" -ForegroundColor Cyan
    Write-Host "  - Total files deleted: $deletedCount"
    Write-Host "  - System reset to initial state"
    Write-Host "  - Next run will process all files in Google Drive"
    Write-Host ""
    Write-Host "Preserved files:" -ForegroundColor Green
    Write-Host "  - config\config.json (settings)"
    Write-Host "  - config\credentials.json (Google auth)"
    Write-Host "  - data\token.pickle (auth token)"
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "ERROR during reset process:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
}

if (-not $Force) {
    Read-Host "Press Enter to exit"
}
