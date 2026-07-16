# FlowSense AI Startup Script
# Run this script in PowerShell to launch both the Backend and Frontend servers in parallel.

Write-Host "--------------------------------------------------" -ForegroundColor Cyan
Write-Host "FlowSense AI - Launching Services" -ForegroundColor Cyan
Write-Host "--------------------------------------------------" -ForegroundColor Cyan

# 1. Start the FastAPI Backend in a new window
Write-Host "[1/3] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Starting FastAPI Backend...' -ForegroundColor Green; .venv\Scripts\activate; uvicorn backend.app.main:app --reload --port 8000"

# 2. Start the Vite React Frontend in a new window
Write-Host "[2/3] Starting Vite React Frontend on http://localhost:5173..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Starting Vite Frontend...' -ForegroundColor Green; cd frontend; npm run dev"

# Wait a brief moment for servers to spin up
Start-Sleep -Seconds 3

# 3. Launch Dashboard in default browser
Write-Host "[3/3] Launching web browser dashboard..." -ForegroundColor Yellow
Start-Process "http://localhost:5173"

Write-Host "--------------------------------------------------" -ForegroundColor Cyan
Write-Host "All services started successfully!" -ForegroundColor Green
Write-Host "FastAPI Swagger: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "React Dashboard: http://localhost:5173" -ForegroundColor Gray
Write-Host "--------------------------------------------------" -ForegroundColor Cyan
