Set-Location $PSScriptRoot

if (-not (Test-Path build)) {
    New-Item -ItemType Directory -Path build | Out-Null
}

latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build DoAn.tex

Copy-Item -Path build\DoAn.pdf -Destination DoAn.pdf -Force

$rootArtifacts = @(
    'DoAn.aux',
    'DoAn.bbl',
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
    'DoAn.xdv',
)

foreach ($artifact in $rootArtifacts) {
    if (Test-Path $artifact) {
        Remove-Item $artifact -Force
    }
}
