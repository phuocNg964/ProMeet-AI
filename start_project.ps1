# Script to start all JiraMeet services
# Run this script in PowerShell

$root = Get-Location

# 1. Start Main Backend (Port 8000)
Write-Host "Starting Main Backend on Port 8000..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd server; python main.py"

# 2. Start Meeting AI Agent (Port 8001)
Write-Host "Starting Meeting Analysis Server on Port 8001..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd server/AI; python meeting_server.py"

# 3. Start Project Manager AI Agent (Port 8002)
Write-Host "Starting Project Manager Agent Server on Port 8002..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd server/AI; python project_server.py"

# 4. Start Frontend (Port 5173 - default Vite)
Write-Host "Starting Frontend Client..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd client; npm run dev"

Write-Host "All services started!"
