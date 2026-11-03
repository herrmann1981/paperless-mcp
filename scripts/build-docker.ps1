param(
    [string]$ImageName = "paperless-mcp:local"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
docker build --tag $ImageName $repoRoot
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
