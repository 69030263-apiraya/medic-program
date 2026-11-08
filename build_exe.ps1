$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install application dependencies."
}

python -m pip install "pyinstaller>=6.10,<7"
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install PyInstaller."
}

python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name MedicProgram `
    --collect-all customtkinter `
    --collect-all winotify `
    launcher.py
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed to build MedicProgram.exe."
}

Write-Host "Built dist\MedicProgram.exe"
