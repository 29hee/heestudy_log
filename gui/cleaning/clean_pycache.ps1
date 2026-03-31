param(
    [switch]$WhatIf
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $root
Write-Host "Cleaning Python cache under: $root"

$pycacheDirs = Get-ChildItem -Path $root -Directory -Recurse -Force |
    Where-Object { $_.Name -eq "__pycache__" }

$pycFiles = Get-ChildItem -Path $root -File -Recurse -Force |
    Where-Object { $_.Extension -eq ".pyc" }

if (-not $pycacheDirs -and -not $pycFiles) {
    Write-Host "No cache files found."
    exit 0
}

foreach ($dir in $pycacheDirs) {
    Remove-Item -Path $dir.FullName -Recurse -Force -ErrorAction SilentlyContinue -WhatIf:$WhatIf
}

foreach ($file in $pycFiles) {
    Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue -WhatIf:$WhatIf
}

if ($WhatIf) {
    Write-Host "Dry-run complete. No files were deleted."
} else {
    Write-Host "Cache cleanup complete."
}
