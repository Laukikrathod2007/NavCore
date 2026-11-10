# NavCore Full Audit Checklist
# Run from navcore\ directory with API running on port 8001

$BASE = "http://localhost:8001"
$pass = 0
$fail = 0

function Check-Item {
    param([string]$id, [string]$description, [bool]$result, [string]$detail = "")
    if ($result) {
        Write-Host "  [PASS] $id — $description" -ForegroundColor Green
        $script:pass++
    } else {
        Write-Host "  [FAIL] $id — $description $detail" -ForegroundColor Red
        $script:fail++
    }
}

Write-Host ""
Write-Host "NavCore Audit Checklist" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan

# ── API CHECKS ───────────────────────────────────────────────────────
Write-Host ""
Write-Host "Backend API Checks" -ForegroundColor Yellow

# 1. Health check
try {
    $h = Invoke-RestMethod -Uri "$BASE/health" -UseBasicParsing
    $ok = $h.status -eq "healthy" -and $h.qdrant_ok -eq $true -and $h.graph_ok -eq $true
    Check-Item "01" "Health endpoint returns healthy" $ok "status=$($h.status) qdrant=$($h.qdrant_ok) graph=$($h.graph_ok)"
} catch { Check-Item "01" "Health endpoint returns healthy" $false $_.Exception.Message }

# 2. English query
try {
    $b = '{"query":"where is cardiology","current_node":"main_entrance"}'
    $r = Invoke-RestMethod -Uri "$BASE/query/text" -Method POST -Body $b -ContentType "application/json" -UseBasicParsing
    $ok = $r.destination_node_id -eq "cardiology_opd" -and $r.path_nodes.Count -eq 4
    Check-Item "02" "English query -> cardiology_opd (4 steps)" $ok "dest=$($r.destination_node_id) steps=$($r.path_nodes.Count)"
} catch { Check-Item "02" "English query" $false $_.Exception.Message }

# 3. Hindi query
try {
    $b = '{"query":"dil ke doctor kahaan hain","current_node":"main_entrance"}'
    $r = Invoke-RestMethod -Uri "$BASE/query/text" -Method POST -Body $b -ContentType "application/json" -UseBasicParsing
    $ok = $r.destination_node_id -eq "cardiology_opd"
    Check-Item "03" "Hindi query -> cardiology_opd" $ok "dest=$($r.destination_node_id) lang=$($r.detected_language)"
} catch { Check-Item "03" "Hindi query" $false $_.Exception.Message }

# 4. Marathi query
try {
    $b = "{`"query`":`"ह्रदय रोग विभाग कुठे आहे`",`"current_node`":`"main_entrance`"}"
    $r = Invoke-RestMethod -Uri "$BASE/query/text" -Method POST -Body $b -ContentType "application/json" -UseBasicParsing
    $ok = $r.destination_node_id -eq "cardiology_opd"
    Check-Item "04" "Marathi query -> cardiology_opd" $ok "dest=$($r.destination_node_id)"
} catch { Check-Item "04" "Marathi query" $false $_.Exception.Message }

# 5. Code-mixed query
try {
    $b = '{"query":"mujhe Dr. Mehta se milna hai cardiology me","current_node":"main_entrance"}'
    $r = Invoke-RestMethod -Uri "$BASE/query/text" -Method POST -Body $b -ContentType "application/json" -UseBasicParsing
    $ok = $r.destination_node_id -eq "cardiology_opd"
    Check-Item "05" "Code-mixed query -> cardiology_opd" $ok "dest=$($r.destination_node_id)"
} catch { Check-Item "05" "Code-mixed query" $false $_.Exception.Message }

# 6. Directions field non-empty
try {
    $b = '{"query":"where is emergency","current_node":"main_entrance"}'
    $r = Invoke-RestMethod -Uri "$BASE/query/text" -Method POST -Body $b -ContentType "application/json" -UseBasicParsing
    $ok = $r.directions.Length -gt 10
    Check-Item "06" "Directions text non-empty" $ok "len=$($r.directions.Length)"
} catch { Check-Item "06" "Directions non-empty" $false $_.Exception.Message }

# 7. Admin availability toggle
try {
    $b = '{"is_available":false,"reason":"Dr. Mehta on leave"}'
    $r = Invoke-RestMethod -Uri "$BASE/locations/cardiology_opd/availability" -Method PATCH -Body $b -ContentType "application/json" -UseBasicParsing
    Check-Item "07" "Admin toggle sets unavailable" $r.success "success=$($r.success)"
} catch { Check-Item "07" "Admin toggle" $false $_.Exception.Message }

# 8. Query after toggle shows warning
try {
    $b = '{"query":"where is cardiology","current_node":"main_entrance"}'
    $r = Invoke-RestMethod -Uri "$BASE/query/text" -Method POST -Body $b -ContentType "application/json" -UseBasicParsing
    $ok = $r.warnings.Count -gt 0
    Check-Item "08" "Query after toggle shows warning" $ok "warnings=$($r.warnings.Count)"
} catch { Check-Item "08" "Warning after toggle" $false $_.Exception.Message }

# 9. Reset availability
try {
    $b = '{"is_available":true}'
    $r = Invoke-RestMethod -Uri "$BASE/locations/cardiology_opd/availability" -Method PATCH -Body $b -ContentType "application/json" -UseBasicParsing
    Check-Item "09" "Availability reset" $r.success "success=$($r.success)"
} catch { Check-Item "09" "Availability reset" $false $_.Exception.Message }

# 10. Locations list returns 20 nodes
try {
    $r = Invoke-RestMethod -Uri "$BASE/locations" -UseBasicParsing
    $ok = $r.total -eq 20
    Check-Item "10" "GET /locations returns 20 nodes" $ok "total=$($r.total)"
} catch { Check-Item "10" "Locations list" $false $_.Exception.Message }

# 11. QR endpoint
try {
    $b = '{"qr_data":"node:reception"}'
    $r = Invoke-RestMethod -Uri "$BASE/query/qr" -Method POST -Body $b -ContentType "application/json" -UseBasicParsing
    $ok = $r.confirmed -eq $true -and $r.current_location -eq "reception"
    Check-Item "11" "QR scan sets location" $ok "loc=$($r.current_location) confirmed=$($r.confirmed)"
} catch { Check-Item "11" "QR endpoint" $false $_.Exception.Message }

# ── BENCHMARK CHECKS ─────────────────────────────────────────────────
Write-Host ""
Write-Host "Benchmark Checks" -ForegroundColor Yellow

# 12. Benchmark results file exists
$resultsPath = "evaluation\results\benchmark_results.json"
$exists = Test-Path $resultsPath
Check-Item "12" "Benchmark results file exists" $exists

# 13. Results has all 3 conditions
if ($exists) {
    $r = Get-Content $resultsPath | ConvertFrom-Json
    $ok = ($null -ne $r.keyword_baseline) -and ($null -ne $r.flat_semantic) -and ($null -ne $r.navcore_dual_memory) -and ($null -ne $r.comparison)
    Check-Item "13" "Results has all 3 conditions + comparison" $ok
} else { Check-Item "13" "Results has all 3 conditions" $false "File missing" }

# 14. NavCore beats keyword baseline
if ($exists) {
    $r = Get-Content $resultsPath | ConvertFrom-Json
    $nc = $r.navcore_dual_memory.destination_accuracy
    $kw = $r.keyword_baseline.destination_accuracy
    $ok = $nc -gt $kw
    Check-Item "14" "NavCore beats keyword baseline" $ok "NavCore=$([math]::Round($nc*100,1))% Keyword=$([math]::Round($kw*100,1))%"
} else { Check-Item "14" "NavCore beats keyword" $false "File missing" }

# 15. NavCore has junction accuracy > 0
if ($exists) {
    $r = Get-Content $resultsPath | ConvertFrom-Json
    $ok = $r.navcore_dual_memory.junction_accuracy -gt 0
    Check-Item "15" "NavCore has junction accuracy > 0" $ok "junction=$([math]::Round($r.navcore_dual_memory.junction_accuracy*100,1))%"
} else { Check-Item "15" "Junction accuracy" $false "File missing" }

# 16. NavCore has path accuracy > 0
if ($exists) {
    $r = Get-Content $resultsPath | ConvertFrom-Json
    $ok = $r.navcore_dual_memory.path_accuracy -gt 0
    Check-Item "16" "NavCore has path accuracy > 0" $ok "path=$([math]::Round($r.navcore_dual_memory.path_accuracy*100,1))%"
} else { Check-Item "16" "Path accuracy" $false "File missing" }

# ── DOCUMENTATION CHECKS ─────────────────────────────────────────────
Write-Host ""
Write-Host "Documentation Checks" -ForegroundColor Yellow

Check-Item "17" "README.md exists" (Test-Path "README.md")
$readmeLines = if (Test-Path "README.md") { (Get-Content "README.md").Count } else { 0 }
Check-Item "18" "README.md has >50 lines" ($readmeLines -gt 50) "lines=$readmeLines"
Check-Item "19" "BENCHMARK.md exists" (Test-Path "BENCHMARK.md")
$bmLines = if (Test-Path "BENCHMARK.md") { (Get-Content "BENCHMARK.md").Count } else { 0 }
Check-Item "20" "BENCHMARK.md has >50 lines" ($bmLines -gt 50) "lines=$bmLines"
Check-Item "21" ".env.example exists" (Test-Path ".env.example")
Check-Item "22" "requirements.txt exists" (Test-Path "requirements.txt")
Check-Item "23" "Dockerfile exists" (Test-Path "Dockerfile")
Check-Item "24" "docker-compose.yml exists" (Test-Path "docker-compose.yml")
Check-Item "25" ".gitignore exists" (Test-Path ".gitignore")

# ── PYTHON TEST SUITE ─────────────────────────────────────────────────
Write-Host ""
Write-Host "Test Suite Check" -ForegroundColor Yellow
$testResult = python -m pytest tests/ -q --tb=no 2>&1 | Select-String "passed"
$ok = $testResult -match "90 passed"
Check-Item "26" "90/90 Python tests pass" $ok "$testResult"

# ── FRONTEND CHECKS ───────────────────────────────────────────────────
Write-Host ""
Write-Host "Frontend Checks" -ForegroundColor Yellow

Check-Item "27" "frontend/package.json exists" (Test-Path "frontend\package.json")
Check-Item "28" "frontend/pages/index.tsx exists" (Test-Path "frontend\pages\index.tsx")
Check-Item "29" "frontend/pages/admin.tsx exists" (Test-Path "frontend\pages\admin.tsx")
Check-Item "30" "frontend/components/FloorMap.tsx exists" (Test-Path "frontend\components\FloorMap.tsx")
Check-Item "31" "frontend/components/VoiceInput.tsx exists" (Test-Path "frontend\components\VoiceInput.tsx")
Check-Item "32" "frontend/components/DirectionsPanel.tsx exists" (Test-Path "frontend\components\DirectionsPanel.tsx")

# TypeScript check
$tscResult = npx --prefix frontend tsc --noEmit 2>&1
$ok = $LASTEXITCODE -eq 0
Check-Item "33" "TypeScript compiles with zero errors" $ok

# ── DATA CHECKS ───────────────────────────────────────────────────────
Write-Host ""
Write-Host "Data Checks" -ForegroundColor Yellow

Check-Item "34" "data/hospitals/sample_hospital/graph.json exists" (Test-Path "data\hospitals\sample_hospital\graph.json")
Check-Item "35" "data/hospitals/sample_hospital/aliases.json exists" (Test-Path "data\hospitals\sample_hospital\aliases.json")
Check-Item "36" "evaluation/test_set_200.json exists" (Test-Path "evaluation\test_set_200.json")

# Test set has 200 queries
if (Test-Path "evaluation\test_set_200.json") {
    $ts = Get-Content "evaluation\test_set_200.json" | ConvertFrom-Json
    Check-Item "37" "Test set has 200 queries" ($ts.Count -eq 200) "count=$($ts.Count)"
} else { Check-Item "37" "Test set has 200 queries" $false }

# ── SUMMARY ───────────────────────────────────────────────────────────
Write-Host ""
Write-Host "==============================" -ForegroundColor Cyan
Write-Host "AUDIT SUMMARY" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host "  PASSED: $pass" -ForegroundColor Green
Write-Host "  FAILED: $fail" -ForegroundColor $(if ($fail -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($fail -eq 0) {
    Write-Host "ALL CHECKS PASSED. NavCore is production-ready." -ForegroundColor Green
} else {
    Write-Host "$fail checks failed. Fix them before deployment." -ForegroundColor Red
}
