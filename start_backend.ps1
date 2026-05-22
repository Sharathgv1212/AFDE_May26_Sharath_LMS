# Start the FastAPI backend with auto-reload.
# Run from the project root.

Set-Location -Path $PSScriptRoot
Write-Host "Starting Library Management System backend on http://localhost:8000" -ForegroundColor Cyan
py -m uvicorn backend.main:app --reload
