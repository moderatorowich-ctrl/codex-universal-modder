$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
if (Get-Command uv -ErrorAction SilentlyContinue) {
    & uv run --project $ProjectRoot python -m um @args
} else {
    $PreviousPythonPath = $env:PYTHONPATH
    try {
        $env:PYTHONPATH = $ProjectRoot + [IO.Path]::PathSeparator + $PreviousPythonPath
        if (Get-Command py -ErrorAction SilentlyContinue) { & py -3 -m um @args }
        else { & python -m um @args }
    } finally { $env:PYTHONPATH = $PreviousPythonPath }
}
exit $LASTEXITCODE
