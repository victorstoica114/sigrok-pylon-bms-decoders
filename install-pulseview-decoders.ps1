param(
    [string]$BuiltinDecoderDir = "C:\Program Files\sigrok\PulseView\share\libsigrokdecode\decoders",
    [string]$InstallDecoderDir = "C:\ProgramData\libsigrokdecode\decoders",
    [string]$PulseViewExe = "C:\Program Files\sigrok\PulseView\pulseview.exe",
    [switch]$SkipShortcuts
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$customDecoderDir = Join-Path $scriptDir "decoders"
$customDecoders = Get-ChildItem -LiteralPath $customDecoderDir -Directory | Where-Object {
    Test-Path (Join-Path $_.FullName "pd.py")
} | Sort-Object Name

if (-not $customDecoders) {
    throw "No custom decoders found in: $customDecoderDir"
}

if (-not (Test-Path $BuiltinDecoderDir)) {
    throw "PulseView built-in decoder directory not found: $BuiltinDecoderDir"
}

New-Item -ItemType Directory -Force -Path $InstallDecoderDir | Out-Null

Copy-Item -Path (Join-Path $BuiltinDecoderDir "*") -Destination $InstallDecoderDir -Recurse -Force

foreach ($decoder in $customDecoders) {
    $dst = Join-Path $InstallDecoderDir $decoder.Name
    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    Copy-Item -Path (Join-Path $decoder.FullName "*") -Destination $dst -Recurse -Force
}

$decoderNames = ($customDecoders | ForEach-Object { $_.Name }) -join ", "

[Environment]::SetEnvironmentVariable("SIGROKDECODE_DIR", $InstallDecoderDir, "User")
$env:SIGROKDECODE_DIR = $InstallDecoderDir

if (-not $SkipShortcuts) {
    $launcher = Join-Path $scriptDir "start-pulseview.ps1"
    $powershell = Join-Path $env:WINDIR "System32\WindowsPowerShell\v1.0\powershell.exe"
    $shortcutTargets = @(
        (Join-Path ([Environment]::GetFolderPath("Desktop")) "PulseView BMS.lnk"),
        (Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\PulseView BMS.lnk")
    )

    $ws = New-Object -ComObject WScript.Shell
    foreach ($shortcutPath in $shortcutTargets) {
        $shortcut = $ws.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = $powershell
        $shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$launcher`""
        $shortcut.WorkingDirectory = (Resolve-Path $scriptDir).Path
        $shortcut.Description = "PulseView with built-in and custom BMS decoders"
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
