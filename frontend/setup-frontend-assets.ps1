# setup-frontend-assets.ps1
# Creates modular assets directory structure and downloads/customizes assets from moss.dev for NavCore

$baseDir = "c:\Users\LAUKIK\Desktop\Research_Work\NavCore\navcore\frontend"
$publicAssets = "$baseDir\public\assets"
$dirs = @(
    "$publicAssets\brand",
    "$publicAssets\moss",
    "$publicAssets\icons",
    "$publicAssets\diagrams",
    "$publicAssets\maps",
    "$publicAssets\badges",
    "$baseDir\components\ui",
    "$baseDir\components\layout",
    "$baseDir\components\landing",
    "$baseDir\components\navcore",
    "$baseDir\components\admin",
    "$baseDir\hooks",
    "$baseDir\lib"
)

foreach ($d in $dirs) {
    if (-not (Test-Path $d)) {
        New-Item -ItemType Directory -Path $d -Force | Out-Null
        Write-Host "Created directory: $d"
    } else {
        Write-Host "Directory already exists: $d"
    }
}

# Download assets from moss.dev
$mossAssets = @{
    "langchain.svg" = "https://www.moss.dev/design/integrations/langchain.svg"
    "nextjs.svg" = "https://www.moss.dev/design/integrations/nextjs.svg"
    "elevenlabs.svg" = "https://www.moss.dev/design/integrations/elevenlabs.svg"
    "mcp-server.svg" = "https://www.moss.dev/design/integrations/mcp-server.svg"
    "microsoft.svg" = "https://www.moss.dev/design/logos/trust/microsoft.svg"
    "berkeley.svg" = "https://www.moss.dev/design/logos/trust/berkeley.svg"
    "stanford.svg" = "https://www.moss.dev/design/logos/trust/stanford.svg"
    "cmu.svg" = "https://www.moss.dev/design/logos/trust/cmu.svg"
    "coderabbit.svg" = "https://www.moss.dev/design/logos/trust/coderabbit.svg"
    "zomato.svg" = "https://www.moss.dev/design/logos/trust/zomato.svg"
    "grammarly.svg" = "https://www.moss.dev/design/logos/trust/grammarly.svg"
    "logo-word.svg" = "https://www.moss.dev/design/logo-word.svg"
}

foreach ($item in $mossAssets.GetEnumerator()) {
    $outFile = "$publicAssets\moss\$($item.Key)"
    try {
        Invoke-WebRequest -Uri $item.Value -OutFile $outFile -UserAgent "Mozilla/5.0" -TimeoutSec 10
        Write-Host "Downloaded $($item.Key) -> $outFile"
    } catch {
        Write-Warning "Could not download $($item.Key): $_"
    }
}

Write-Host "Frontend asset structure setup complete!"

