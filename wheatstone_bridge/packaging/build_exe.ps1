# Build script for Wheatstone Bridge Executable
# Run this from the project root: ./packaging/build_exe.ps1

# Ensure we are in the correct directory (the root of the project)
$RootPath = Resolve-Path "$PSScriptRoot\.."
Set-Location $RootPath

Write-Host "Building Wheatstone Bridge..." -ForegroundColor Cyan

# Run PyInstaller using the spec file
# We specify --distpath and --workpath to keep temp files in the packaging folder
python -m PyInstaller `
    --clean `
    --noconfirm `
    --distpath "packaging/dist" `
    --workpath "packaging/build" `
    "packaging/WheatstoneBridge.spec"

# Move the final executable to the root
if (Test-Path "packaging/dist/WheatstoneBridge.exe") {
    Move-Item -Path "packaging/dist/WheatstoneBridge.exe" -Destination "WheatstoneBridge.exe" -Force
    Write-Host "Build complete! Executable is in the project root." -ForegroundColor Green
} else {
    Write-Host "Build failed! Executable not found." -ForegroundColor Red
}
