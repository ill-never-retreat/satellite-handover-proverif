param(
    [string]$ProVerifExecutable = "proverif"
)

$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    $models = @(
        "CRT_baseline.pv",
        "CRT_modulus_exposure.pv",
        "CRT_serving_compromise.pv",
        "CRT_post_session_link_key_exposure.pv",
        "CRT_post_session_joint_exposure.pv"
    )

    foreach ($model in $models) {
        $output = [System.IO.Path]::GetFileNameWithoutExtension($model) + ".rerun.result.txt"
        & $ProVerifExecutable $model 2>&1 | Tee-Object -FilePath $output
        if ($LASTEXITCODE -ne 0) {
            throw "ProVerif failed for $model with exit code $LASTEXITCODE"
        }
    }
} finally {
    Pop-Location
}
