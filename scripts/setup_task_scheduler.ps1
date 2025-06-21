# BirdNET AutoPipeline Task Scheduler Setup Script
# Run as Administrator

param(
    [string]$TaskName = "BirdNET AutoPipeline",
    [string]$ScriptPath = "S:\python\BirdNET-AutoPipeline\scripts\run_pipeline_en.bat",
    [string]$WorkingDirectory = "S:\python\BirdNET-AutoPipeline"
)

Write-Host "Setting up Task Scheduler for BirdNET AutoPipeline..."

try {
    # Create task action
    $Action = New-ScheduledTaskAction -Execute $ScriptPath -WorkingDirectory $WorkingDirectory
    
    # Create task trigger (daily at 8:00 AM, repeat every 30 minutes for 4 hours)
    $Trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM
    $Trigger.Repetition = New-ScheduledTaskTrigger -Once -At 8:00AM -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration (New-TimeSpan -Hours 4)
    
    # Create task settings
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
    
    # Create task principal
    $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
    
    # Register the task
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Automatic audio file processing system for Raspberry Pi recordings"
    
    Write-Host "✅ Task Scheduler setup completed successfully!"
    Write-Host "Task Name: $TaskName"
    Write-Host "Schedule: Daily 8:00-12:00 (every 30 minutes)"
    Write-Host "Script: $ScriptPath"
    
    # Show the created task
    Get-ScheduledTask -TaskName $TaskName | Format-Table -AutoSize
    
} catch {
    Write-Host "❌ Error occurred during setup: $($_.Exception.Message)"
    Write-Host "Please set up manually using Task Scheduler GUI."
}

Write-Host ""
Write-Host "To verify the task:"
Write-Host "1. Open Task Scheduler (taskschd.msc)"
Write-Host "2. Look for '$TaskName' in the task list"
Write-Host "3. Right-click and select 'Run' to test"
