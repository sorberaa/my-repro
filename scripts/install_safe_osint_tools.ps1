$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$toolsDir = Join-Path $root "tools"
New-Item -ItemType Directory -Force -Path $toolsDir | Out-Null

$repos = @(
    @{ Name = "sherlock"; Url = "https://github.com/sherlock-project/sherlock"; Path = "tools/sherlock" },
    @{ Name = "subfinder"; Url = "https://github.com/projectdiscovery/subfinder"; Path = "tools/subfinder" },
    @{ Name = "amass"; Url = "https://github.com/OWASP-Amass/Amass"; Path = "tools/amass" },
    @{ Name = "theharvester"; Url = "https://github.com/laramies/theHarvester"; Path = "tools/theHarvester" },
    @{ Name = "spiderfoot"; Url = "https://github.com/smicallef/spiderfoot"; Path = "tools/spiderfoot" }
)

foreach ($repo in $repos) {
    $target = Join-Path $root $repo.Path
    if (Test-Path $target) {
        Write-Host "[skip] $($repo.Name) already installed at $target"
        continue
    }

    Write-Host "[clone] $($repo.Name) -> $($repo.Url)"
    git clone $repo.Url $target
}

Write-Host ""
Write-Host "Installed safe public-data OSINT tools under: $toolsDir"
Write-Host "Use them as local launch entries in the panel by pointing each tool to its own command/script."
