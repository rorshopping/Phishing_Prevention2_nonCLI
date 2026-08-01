param(
    [string]$ApiKey
)

$root = "C:\Users\Richard\Documents\Projects\Phishing_Prevention2_nonCLI"
$gophishDir = Join-Path $root "gophish"
$errLog = Join-Path $gophishDir "gophish_err.txt"
$outLog = Join-Path $gophishDir "gophish_out.txt"
$envFile = Join-Path $root ".env"

# Kill any existing gophish process
Get-Process -Name "gophish" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1

# Clear old logs
@() | Set-Content $errLog -Encoding ASCII
@() | Set-Content $outLog -Encoding ASCII

# Start Gophish
Start-Process -WindowStyle Hidden -FilePath (Join-Path $gophishDir "gophish.exe") `
    -WorkingDirectory $gophishDir `
    -RedirectStandardOutput $outLog `
    -RedirectStandardError $errLog

# Wait for startup (up to 45s)
Write-Host "Waiting for Gophish to start..." -NoNewline
$ready = $false
for ($i = 0; $i -lt 45; $i++) {
    Start-Sleep -Seconds 1
    Write-Host "." -NoNewline
    $log = Get-Content $errLog -Tail 1 -ErrorAction SilentlyContinue
    if ($log -match "admin server at https://127.0.0.1:3333") {
        $ready = $true
        break
    }
}
Write-Host ""

if (-not $ready) {
    Write-Host "ERROR: Gophish failed to start."
    Get-Content $errLog -ErrorAction SilentlyContinue | ForEach-Object { Write-Host "  $_" }
    exit 1
}

Write-Host "Gophish is ready at https://127.0.0.1:3333"

# Set API key
if (-not $ApiKey) {
    $ApiKey = [System.Guid]::NewGuid().ToString("N").Substring(0, 32)
}

# Write the key into Gophish DB
python tests/set_gophish_key.py $ApiKey 2>&1 | ForEach-Object { Write-Host "  $_" }

# Update .env
$content = Get-Content $envFile -Raw -ErrorAction SilentlyContinue
if ($content -match "(?<=GOPHISH_API_KEY=).*") {
    $content = $content -replace "(?<=GOPHISH_API_KEY=).*", $ApiKey
    Set-Content $envFile $content -Encoding ASCII -NoNewline
    Write-Host "  Updated .env GOPHISH_API_KEY=$ApiKey"
} else {
    Write-Host "  WARNING: Could not find GOPHISH_API_KEY in .env"
}

# Set environment
$env:PYTHONPATH = $root
Set-Location -LiteralPath $root

Write-Host ""
Write-Host "Ready. Run: python debug_execution2.py"
