Set-Location $PSScriptRoot

if (-not (Test-Path build)) {
    New-Item -ItemType Directory -Path build | Out-Null
}

latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build DoAn.tex

if ($LASTEXITCODE -ne 0) {
    Write-Error "latexmk failed with exit code $LASTEXITCODE. DoAn.pdf was not updated."
    exit $LASTEXITCODE
}

if (-not (Test-Path build\DoAn.pdf)) {
    Write-Error "build\DoAn.pdf was not created. DoAn.pdf was not updated."
    exit 1
}

Copy-Item -Path build\DoAn.pdf -Destination DoAn.pdf -Force

$rootArtifacts = @(
    'DoAn.aux',
    'DoAn.bbl',
    'DoAn.bcf',
    'DoAn.blg',
    'DoAn-blx.bib',
    'DoAn.fdb_latexmk',
    'DoAn.fls',
    'DoAn.lof',
    'DoAn.log',
    'DoAn.lot',
    'DoAn.out',
    'DoAn.run.xml',
    'DoAn.synctex.gz',
    'DoAn.toc',
    'DoAn.xdv'
)

foreach ($artifact in $rootArtifacts) {
    if (Test-Path $artifact) {
        Remove-Item $artifact -Force
    }
}
