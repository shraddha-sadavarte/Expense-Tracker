# PowerShell equivalent of the root Makefile.
# Usage: ./infra/dev.ps1 up | down | test | lint | migrate | revision "message"
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('up', 'down', 'test', 'lint', 'migrate', 'revision')]
    [string]$Target,
    [string]$Message
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Compose = @('compose', '-f', (Join-Path $Root 'infra/docker-compose.yml'))

function Invoke-Step([string]$Exe, [string[]]$Arguments) {
    # Native tools (docker, uv) write progress to stderr; Windows PowerShell 5.1
    # would turn that into a terminating error under 'Stop'. Judge by exit code instead.
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { & $Exe @Arguments } finally { $ErrorActionPreference = $previous }
    if ($LASTEXITCODE -ne 0) { throw "$Exe $($Arguments -join ' ') failed ($LASTEXITCODE)" }
}

Push-Location $Root
try {
    switch ($Target) {
        'up' {
            if (-not (Test-Path '.env')) { Copy-Item '.env.example' '.env' }
            Invoke-Step docker ($Compose + @('up', '-d', '--build'))
        }
        'down' { Invoke-Step docker ($Compose + @('down')) }
        'test' {
            Set-Location backend
            Invoke-Step uv @('run', 'pytest')
        }
        'lint' {
            Set-Location backend
            Invoke-Step uv @('run', 'ruff', 'check', '.')
            Invoke-Step uv @('run', 'ruff', 'format', '--check', '.')
            Invoke-Step uv @('run', 'mypy')
            Invoke-Step uv @('run', 'lint-imports')
        }
        'migrate' { Invoke-Step docker ($Compose + @('run', '--rm', 'api', 'alembic', 'upgrade', 'head')) }
        'revision' {
            if (-not $Message) { throw 'usage: ./infra/dev.ps1 revision "describe the change"' }
            Invoke-Step docker ($Compose + @('run', '--rm', 'api', 'alembic', 'revision', '--autogenerate', '-m', $Message))
        }
    }
}
finally {
    Pop-Location
}
