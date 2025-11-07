# Simple PowerShell helper to run the Gradio demo in demo mode
param()

Write-Host "Starting demo in DEMO_MODE..."
$env:DEMO_MODE = "1"
python .\app.py
