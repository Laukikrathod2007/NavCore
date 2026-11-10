# NavCore Live Latency Test
# Run from navcore\ directory after starting the API on port 8001

$queries = @(
    @{ query="dil ke doctor kahaan hain"; label="Hindi cardiology"  },
    @{ query="blood test";                label="English lab"       },
    @{ query="emergency kahan hai";       label="Hindi emergency"   },
    @{ query="haddi ka doctor";           label="Hindi orthopedic"  },
    @{ query="where is reception";        label="English reception" },
    @{ query="baccho ka doctor";          label="Hindi pediatric"   }
)

Write-Host ""
Write-Host "NavCore Latency Test"
Write-Host "===================="

$total = 0
$count = 0

foreach ($q in $queries) {
    $body = "{`"query`":`"" + $q.query + "`",`"current_node`":`"main_entrance`"}"
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8001/query/text" `
            -Method POST -Body $body -ContentType "application/json" `
            -UseBasicParsing -ErrorAction Stop
        $data = $r.Content | ConvertFrom-Json
        $ms = [int]$data.latency_ms
        $dest = $data.destination
        $total += $ms
        $count++
        Write-Host ("  " + $q.label + " -> " + $dest + " [" + $ms + "ms]")
    } catch {
        Write-Host ("  " + $q.label + " -> ERROR: " + $_.Exception.Message)
    }
}

if ($count -gt 0) {
    $avg = [int]($total / $count)
    Write-Host ""
    Write-Host ("Average: " + $avg + "ms over " + $count + " queries")
    Write-Host "Under 2500ms = LLM succeeded. Over 2500ms = fallback template used."
}
