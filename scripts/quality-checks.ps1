# Local equivalent of the CI quality gates.
$ErrorActionPreference = "Stop"

ruff check .
ruff format --check .
mypy app qa_framework
python -m pytest -q
Write-Host "All quality checks passed."
