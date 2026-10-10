param(
    [string]$ProVerifExecutable = "proverif",
    [string]$PythonExecutable = "python"
)

$ErrorActionPreference = "Stop"
& $PythonExecutable (Join-Path $PSScriptRoot "Supplementary_Material_S1/run_models.py") --proverif $ProVerifExecutable
if ($LASTEXITCODE -ne 0) {
    throw "Current S1 reproduction failed with exit code $LASTEXITCODE"
}
