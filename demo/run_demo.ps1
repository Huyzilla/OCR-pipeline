$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$env:STREAMLIT_SERVER_FILE_WATCHER_TYPE = "none"
$env:STREAMLIT_SERVER_RUN_ON_SAVE = "false"
$env:TOKENIZERS_PARALLELISM = "false"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

$PythonExe = Join-Path $env:USERPROFILE "miniconda3\envs\huy\python.exe"
if (-not (Test-Path $PythonExe)) {
    throw "Không tìm thấy Python env huy tại $PythonExe"
}

& $PythonExe -m streamlit run demo/frontend/app.py --server.fileWatcherType none
