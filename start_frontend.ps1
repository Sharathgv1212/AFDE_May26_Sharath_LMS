# Start the Vite dev server.
# Run from the project root.

Set-Location -Path (Join-Path $PSScriptRoot 'frontend')

# Configure npm to use PowerShell because cmd.exe is disabled in the
# target environment. Safe to run repeatedly.
npm config set script-shell "powershell.exe" | Out-Null

if (-not (Test-Path 'node_modules')) {
    Write-Host "Installing frontend dependencies (one-time)…" -ForegroundColor Cyan
    npm install
}

Write-Host "Starting frontend on http://localhost:5173" -ForegroundColor Cyan
npm run dev
