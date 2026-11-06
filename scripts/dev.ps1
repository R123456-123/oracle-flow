[CmdletBinding()]
param(
    [ValidateSet("run", "test", "lint")]
    [string]$Task = "run"
)

$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repositoryRoot

switch ($Task) {
    "run" {
        Set-Location (Join-Path $repositoryRoot "backend")
        python -m uvicorn main:app --reload
    }
    "test" {
        python -m pytest
    }
    "lint" {
        python -m ruff check backend
        python -m ruff format --check backend
        python -m mypy
    }
}
