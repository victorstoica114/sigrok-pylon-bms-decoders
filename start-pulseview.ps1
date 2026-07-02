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
$customDecoders = Get-ChildItem -LiteralPath $customDecoderDir -Directory | Where-Object {
    Test-Path (Join-Path $_.FullName "pd.py")
} | Sort-Object Name

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
Copy-Item -Path (Join-Path $BuiltinDecoderDir "*") -Destination $bundleDir -Recurse -Force

foreach ($decoder in $customDecoders) {
    Copy-Item -Path $decoder.FullName -Destination (Join-Path $bundleDir $decoder.Name) -Recurse -Force
}

$decoderNames = ($customDecoders | ForEach-Object { $_.Name }) -join ", "

$env:SIGROKDECODE_DIR = $bundleDir
Start-Process -FilePath $PulseViewExe -WorkingDirectory (Split-Path -Parent $PulseViewExe)

Write-Host "PulseView started with SIGROKDECODE_DIR=$bundleDir"
Write-Host "Custom decoders: $decoderNames"
