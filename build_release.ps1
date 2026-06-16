$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$DistRoot = Join-Path $ProjectRoot "dist"
$ReleaseRoot = Join-Path $DistRoot "web_analysis_exam_trainer"
$ZipPath = Join-Path $DistRoot "web_analysis_exam_trainer.zip"

if (Test-Path $ReleaseRoot) {
    Remove-Item -LiteralPath $ReleaseRoot -Recurse -Force
}

if (Test-Path $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}

New-Item -ItemType Directory -Path $ReleaseRoot -Force | Out-Null

$itemsToCopy = @(
    "data",
    "docs",
    "notebooks",
    "src",
    "tests",
    "README.md",
    "requirements.txt",
    "launch_web_trainer.bat",
    "launch_web_trainer_mac.command",
    "RELEASE_INSTRUCTIONS.txt"
)

foreach ($item in $itemsToCopy) {
    $source = Join-Path $ProjectRoot $item
    if (-not (Test-Path $source)) {
        throw "Required release item is missing: $item"
    }

    $destination = Join-Path $ReleaseRoot $item
    Copy-Item -LiteralPath $source -Destination $destination -Recurse -Force
}

$excludedDirectories = @("__pycache__", ".pytest_cache")
foreach ($directoryName in $excludedDirectories) {
    Get-ChildItem -LiteralPath $ReleaseRoot -Recurse -Directory -Force |
        Where-Object { $_.Name -eq $directoryName } |
        Remove-Item -Recurse -Force
}

$excludedFiles = @("progress.json", "streamlit_progress.json")
foreach ($fileName in $excludedFiles) {
    Get-ChildItem -LiteralPath $ReleaseRoot -Recurse -File -Force |
        Where-Object { $_.Name -eq $fileName } |
        Remove-Item -Force
}

Compress-Archive -LiteralPath $ReleaseRoot -DestinationPath $ZipPath -Force

Write-Host ""
Write-Host "Release zip created:"
Write-Host $ZipPath
Write-Host ""
Write-Host "Instructions:"
Write-Host "1. Copy the zip to another computer."
Write-Host "2. Extract it."
Write-Host "3. Windows: double-click launch_web_trainer.bat."
Write-Host "4. Mac: double-click launch_web_trainer_mac.command."
