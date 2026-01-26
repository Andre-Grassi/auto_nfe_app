# Activate virtual environment
$venvPath = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & $venvPath
} else {
    Write-Host "Virtual environment not found at $venvPath" -ForegroundColor Red
    exit 1
}

# Delete build folder
$buildPath = ".\build"
if (Test-Path $buildPath) {
    Write-Host "Deleting build folder..." -ForegroundColor Yellow
    try {
        # Kill any processes that might be locking files
        Get-Process | Where-Object {$_.Path -like "*auto_nfe_app*"} | Stop-Process -Force -ErrorAction SilentlyContinue
        
        Start-Sleep -Seconds 2
        
        Remove-Item -Recurse -Force $buildPath -ErrorAction Stop
        Write-Host "Build folder deleted successfully." -ForegroundColor Green
    } catch {
        Write-Host "Warning: Could not fully delete build folder. Continuing anyway..." -ForegroundColor Yellow
        Write-Host $_.Exception.Message -ForegroundColor Yellow
    }
}

# Install auto_nfe package
Write-Host "Installing auto_nfe package..." -ForegroundColor Green
pip install ..\nfe_automatico\

# Build with Flet
Write-Host "Building with Flet..." -ForegroundColor Green
flet build windows

Write-Host "Build complete!" -ForegroundColor Green