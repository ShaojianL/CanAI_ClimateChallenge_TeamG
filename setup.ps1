<#
.SYNOPSIS
Creates the local Python environment and installs the project requirements.
.DESCRIPTION
Run with .\setup.ps1. Reuses an existing .venv and stops if a command fails.
Requires Python on PATH and internet access for package installation.
#>
[CmdletBinding(SupportsShouldProcess)]
param()

$ErrorActionPreference = 'Stop'
$venvPath = Join-Path $PSScriptRoot '.venv'
$venvPython = Join-Path $venvPath 'Scripts\python.exe'
$requirementsPath = Join-Path $PSScriptRoot 'requirements.txt'

try {
    if (-not (Test-Path -LiteralPath $requirementsPath -PathType Leaf)) {
        throw "Missing requirements.txt in $PSScriptRoot."
    }

    if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
        # Preserve incomplete environments so setup cannot overwrite user files.
        if (Test-Path -LiteralPath $venvPath) {
            throw 'The existing .venv has no Scripts\python.exe. Inspect it before recreating the environment.'
        }

        $pythonCommand = Get-Command python -CommandType Application -ErrorAction SilentlyContinue
        if (-not $pythonCommand) {
            throw 'Python was not found. Install Python with pip and venv, then reopen PowerShell.'
        }

        if ($PSCmdlet.ShouldProcess($venvPath, 'Create Python virtual environment')) {
            & $pythonCommand.Source -m venv $venvPath
            if ($LASTEXITCODE -ne 0) {
                throw 'Virtual-environment creation failed. Check your Python installation.'
            }
            if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
                throw 'Python did not create .venv\Scripts\python.exe. Check your Python installation.'
            }
        }
    }

    if ($PSCmdlet.ShouldProcess($venvPath, 'Install packages from requirements.txt')) {
        & $venvPython -m pip install -r $requirementsPath
        if ($LASTEXITCODE -ne 0) {
            throw 'Dependency installation failed. Check the pip output above, then rerun setup.'
        }

        Write-Host 'Setup complete. From the repository root, start the app with:'
        Write-Host '.\.venv\Scripts\python.exe -m streamlit run app.py'
    }
}
catch {
    Write-Error $_ -ErrorAction Continue
    exit 1
}
