# Run smoke and regression suites with HTML/JUnit reports.
param([string]$Marker = "")
$ErrorActionPreference = "Stop"

if ($Marker -eq "") {
    python -m pytest -v
} else {
    python -m pytest -m $Marker -v
}
Write-Host "Reports: reports\report.html and reports\junit.xml"
