# Windows PowerShell setup for the API automation framework.
$ErrorActionPreference = "Stop"

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt

if (-Not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "Created .env from .env.example. Edit JWT_SECRET_KEY before any non-local use."
}
Write-Host "Setup complete. Run scripts\run-tests.ps1."
