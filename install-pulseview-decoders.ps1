param(
    [string]$BuiltinDecoderDir = "C:\Program Files\sigrok\PulseView\share\libsigrokdecode\decoders",
    [string]$InstallDecoderDir = "C:\ProgramData\libsigrokdecode\decoders",
    [string]$PulseViewExe = "C:\Program Files\sigrok\PulseView\pulseview.exe",
    [switch]$SkipShortcuts
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$customDecoderDir = Join-Path $scriptDir "decoders"

function Get-CustomDecoderDirs {
    param([string]$Root)

    Get-ChildItem -LiteralPath $Root -Directory | Where-Object {
        (Test-Path (Join-Path $_.FullName "pd.py")) -and
        (Test-Path (Join-Path $_.FullName "__init__.py"))
    } | Sort-Object Name
}

function Copy-DecoderDir {
    param(
        [string]$Source,
        [string]$Destination
    )

    if (Test-Path $Destination) {
        Remove-Item -LiteralPath $Destination -Recurse -Force
    }
    Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
    Get-ChildItem -LiteralPath $Destination -Recurse -Directory -Filter "__pycache__" | ForEach-Object {
        Remove-Item -LiteralPath $_.FullName -Recurse -Force
    }
}

function Copy-BuiltinDecoders {
    param(
        [string]$SourceRoot,
        [string]$DestinationRoot
    )

    Get-ChildItem -LiteralPath $SourceRoot | Where-Object {
        $_.Name -notmatch "^(pylon_|growatt_|jkbms_)"
    } | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $DestinationRoot -Recurse -Force
    }
}

if (-not (Test-Path $customDecoderDir)) {
    throw "Custom decoder directory not found: $customDecoderDir"
}

$customDecoders = @(Get-CustomDecoderDirs -Root $customDecoderDir)
if (-not $customDecoders) {
    throw "No custom decoders found in: $customDecoderDir"
}

if (-not (Test-Path $BuiltinDecoderDir)) {
    throw "PulseView built-in decoder directory not found: $BuiltinDecoderDir"
}

$installParent = Split-Path -Parent $InstallDecoderDir
if (-not (Test-Path $installParent)) {
    New-Item -ItemType Directory -Force -Path $installParent | Out-Null
}

if (Test-Path $InstallDecoderDir) {
    $resolvedInstall = (Resolve-Path $InstallDecoderDir).Path
    if ($resolvedInstall -notlike "*\libsigrokdecode\decoders") {
        throw "Refusing to remove unexpected decoder directory: $resolvedInstall"
    }
    Remove-Item -LiteralPath $resolvedInstall -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $InstallDecoderDir | Out-Null
Copy-BuiltinDecoders -SourceRoot $BuiltinDecoderDir -DestinationRoot $InstallDecoderDir

foreach ($decoder in $customDecoders) {
    Copy-DecoderDir -Source $decoder.FullName -Destination (Join-Path $InstallDecoderDir $decoder.Name)
}

$decoderNames = ($customDecoders | ForEach-Object { $_.Name }) -join ", "

[Environment]::SetEnvironmentVariable("SIGROKDECODE_DIR", $InstallDecoderDir, "User")
$env:SIGROKDECODE_DIR = $InstallDecoderDir

if (-not $SkipShortcuts) {
    $launcher = Join-Path $scriptDir "start-pulseview.ps1"
    $powershell = Join-Path $env:WINDIR "System32\WindowsPowerShell\v1.0\powershell.exe"
    $shortcutTargets = @(
        (Join-Path ([Environment]::GetFolderPath("Desktop")) "PulseView BMS.lnk"),
        (Join-Path ([Environment]::GetFolderPath("Desktop")) "PulseView BMS Decoders.lnk"),
        (Join-Path ([Environment]::GetFolderPath("Desktop")) "PulseView Pylon.lnk"),
        (Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\PulseView BMS.lnk"),
        (Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\PulseView BMS Decoders.lnk"),
        (Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\PulseView Pylon.lnk")
    )

    $ws = New-Object -ComObject WScript.Shell
    foreach ($shortcutPath in $shortcutTargets) {
        $shortcut = $ws.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = $powershell
        $shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$launcher`""
        $shortcut.WorkingDirectory = (Resolve-Path $scriptDir).Path
        $shortcut.Description = "PulseView with built-in and custom BMS decoders from sigrok-pylon-bms-decoders"
        if (Test-Path $PulseViewExe) {
            $shortcut.IconLocation = "$PulseViewExe,0"
        }
        $shortcut.Save()
    }
}

Write-Host "Installed PulseView decoders to $InstallDecoderDir"
Write-Host "Custom decoders: $decoderNames"
Write-Host "User SIGROKDECODE_DIR=$InstallDecoderDir"
Write-Host "Restart PulseView before checking the decoder selector."
