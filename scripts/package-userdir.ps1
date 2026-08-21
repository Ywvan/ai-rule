[CmdletBinding()]
param(
    [string]$OutputDirectory
)

$ErrorActionPreference = 'Stop'

function Join-NativePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$BasePath,
        [Parameter(Mandatory = $true)]
        [string[]]$Segments
    )

    $path = $BasePath
    foreach ($segment in $Segments) {
        $path = Join-Path -Path $path -ChildPath $segment
    }
    return $path
}

$repositoryRoot = (Resolve-Path -LiteralPath (Split-Path -Parent $PSScriptRoot)).Path
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = $repositoryRoot
}

$manifestPath = Join-NativePath -BasePath $repositoryRoot -Segments @('plugins', 'hly-codex-guards', '.codex-plugin', 'plugin.json')
$marketplacePath = Join-NativePath -BasePath $repositoryRoot -Segments @('.agents', 'plugins', 'marketplace.json')
$skillsPath = Join-NativePath -BasePath $repositoryRoot -Segments @('plugins', 'hly-codex-guards', 'skills')
$validatorPath = Join-NativePath -BasePath $repositoryRoot -Segments @('scripts', 'validate_plugin.py')

$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ($manifest.name -ne 'hly-codex-guards') {
    throw 'plugin.json name must be hly-codex-guards.'
}
if ($null -eq $manifest.version -or $manifest.version -eq '') {
    throw 'plugin.json version must not be empty.'
}

$outputPath = (Resolve-Path -LiteralPath $OutputDirectory).Path
$archivePath = Join-Path -Path $outputPath -ChildPath "hly-codex-guards-userdir-v$($manifest.version).zip"
if (Test-Path -LiteralPath $archivePath) {
    throw "Archive already exists and will not be overwritten: $archivePath"
}

$stagingPath = Join-Path -Path ([System.IO.Path]::GetTempPath()) -ChildPath ("hly-codex-guards-userdir-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $stagingPath | Out-Null

try {
    $runtimeFiles = @(
        (Get-Item -LiteralPath $marketplacePath),
        (Get-Item -LiteralPath $manifestPath)
    ) + @(Get-ChildItem -LiteralPath $skillsPath -Recurse -File)

    foreach ($file in $runtimeFiles) {
        $relativePath = $file.FullName.Substring($repositoryRoot.Length).TrimStart(
            [System.IO.Path]::DirectorySeparatorChar,
            [System.IO.Path]::AltDirectorySeparatorChar
        )
        $destinationPath = Join-Path -Path $stagingPath -ChildPath $relativePath
        $destinationDirectory = Split-Path -Parent $destinationPath
        New-Item -ItemType Directory -Force -Path $destinationDirectory | Out-Null
        Copy-Item -LiteralPath $file.FullName -Destination $destinationPath
    }

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory(
        $stagingPath,
        $archivePath,
        [System.IO.Compression.CompressionLevel]::Optimal,
        $false
    )

    $pythonCandidates = if ([System.Environment]::OSVersion.Platform -eq [System.PlatformID]::Win32NT) {
        @('python', 'py', 'python3')
    }
    else {
        @('python3', 'python')
    }

    $pythonCommand = $null
    foreach ($candidate in $pythonCandidates) {
        if (Get-Command $candidate -ErrorAction SilentlyContinue) {
            $pythonCommand = $candidate
            break
        }
    }
    if ($null -eq $pythonCommand) {
        throw 'Python interpreter not found. Install Python or expose python/python3/py in PATH.'
    }

    & $pythonCommand $validatorPath --zip $archivePath
    if ($LASTEXITCODE -ne 0) {
        throw "Archive validation failed: $archivePath"
    }

    Write-Output "Archive created and validated: $archivePath"
}
finally {
    if (Test-Path -LiteralPath $stagingPath) {
        Remove-Item -LiteralPath $stagingPath -Recurse -Force
    }
}
