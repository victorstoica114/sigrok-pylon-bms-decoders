param(
    [string]$PulseViewExe = "C:\Program Files\sigrok\PulseView\pulseview.exe",
    [string]$BuiltinDecoderDir = "C:\Program Files\sigrok\PulseView\share\libsigrokdecode\decoders"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path $scriptDir
$buildDir = Join-Path $repoRoot "build"
$bundleDir = Join-Path $buildDir "pulseview-decoders"
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

$customDecoders = @(Get-CustomDecoderDirs -Root $customDecoderDir)
if (-not $customDecoders) {
    throw "No custom decoders found in: $customDecoderDir"
}

if (-not (Test-Path $PulseViewExe)) {
    throw "PulseView executable not found: $PulseViewExe"
}

if (-not (Test-Path $BuiltinDecoderDir)) {
    throw "PulseView built-in decoder directory not found: $BuiltinDecoderDir"
}

if (-not (Test-Path $buildDir)) {
    New-Item -ItemType Directory -Path $buildDir | Out-Null
}

if (Test-Path $bundleDir) {
    $resolvedBundle = (Resolve-Path $bundleDir).Path
    $resolvedBuild = (Resolve-Path $buildDir).Path
    if (-not $resolvedBundle.StartsWith($resolvedBuild, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove unexpected path: $resolvedBundle"
    }
    Remove-Item -LiteralPath $resolvedBundle -Recurse -Force
}

New-Item -ItemType Directory -Path $bundleDir | Out-Null
Copy-BuiltinDecoders -SourceRoot $BuiltinDecoderDir -DestinationRoot $bundleDir

foreach ($decoder in $customDecoders) {
    Copy-DecoderDir -Source $decoder.FullName -Destination (Join-Path $bundleDir $decoder.Name)
}

$decoderNames = ($customDecoders | ForEach-Object { $_.Name }) -join ", "

$env:SIGROKDECODE_DIR = $bundleDir
Start-Process -FilePath $PulseViewExe -WorkingDirectory (Split-Path -Parent $PulseViewExe)

Write-Host "PulseView started with SIGROKDECODE_DIR=$bundleDir"
Write-Host "Custom decoders: $decoderNames"
