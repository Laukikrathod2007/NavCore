"""Full NavCore verification — tests every endpoint and component.
Run from navcore/ with the API on port 8001.
"""
import json
import sys
import urllib.request
import urllib.error

BASE = "http://localhost:8001"
passed = []
failed = []

def check(name, ok, detail=""):
    if ok:
        passed.append(name)
        print(f"  PASS  {name}")
    else:
        failed.append(name)
        print(f"  FAIL  {name}  {detail}")

def get(path):
    with urllib.request.urlopen(f"{BASE}{path}", timeout=10) as r:
        return json.loads(r.read())

def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE}{path}", data=data,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def patch(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE}{path}", data=data,
        headers={"Content-Type": "application/json"}, method="PATCH"
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

print("\n" + "="*55)
print("NavCore Live Verification")
print("="*55)

# ── 1. Health ─────────────────────────────────────────────
print("\n[Health]")
try:
    h = get("/health")
    check("Health status=healthy",   h["status"] == "healthy")
    check("Qdrant connected",        h["qdrant_ok"] == True)
    check("Graph loaded",            h["graph_ok"] == True)
    check("Ollama available",        h.get("ollama_ok", False) == True)
except Exception as e:
    check("Health endpoint", False, str(e))

# ── 2. English query ──────────────────────────────────────
print("\n[English Query]")
try:
    r = post("/query/text", {"query": "where is cardiology", "current_node": "main_entrance"})
    check("Returns cardiology_opd",  r["destination_node_id"] == "cardiology_opd")
    check("Path has 4 steps",        len(r["path_nodes"]) == 4)
    check("Directions non-empty",    len(r["directions"]) > 10)
    check("No warnings",             len(r["warnings"]) == 0)
    print(f"         Directions: {r['directions'][:80]}...")
except Exception as e:
    check("English query", False, str(e))

# ── 3. Hindi query ────────────────────────────────────────
print("\n[Hindi Query]")
try:
    r = post("/query/text", {"query": "dil ke doctor kahaan hain", "current_node": "main_entrance"})
    check("Hindi -> cardiology_opd",   r["destination_node_id"] == "cardiology_opd")
    check("Detected as hi-mix",        r["detected_language"] == "hi-mix")
    check("Directions non-empty",      len(r["directions"]) > 10)
    print(f"         Directions: {r['directions'][:80]}...")
except Exception as e:
    check("Hindi query", False, str(e))

# ── 4. Marathi query ──────────────────────────────────────
print("\n[Marathi Query]")
try:
    r = post("/query/text", {"query": "ह्रदय रोग विभाग कुठे आहे", "current_node": "main_entrance"})
    check("Marathi -> cardiology_opd", r["destination_node_id"] == "cardiology_opd")
    check("Detected as mr/hi-mix",     r["detected_language"] in ("mr", "hi-mix"))
except Exception as e:
    check("Marathi query", False, str(e))

# ── 5. Code-mixed query ───────────────────────────────────
print("\n[Code-Mixed Query]")
try:
    r = post("/query/text", {"query": "mujhe blood test dena hai", "current_node": "main_entrance"})
    check("Code-mixed -> lab_pathology", r["destination_node_id"] == "lab_pathology")
    check("Detected as hi-mix",         r["detected_language"] == "hi-mix")
    check("Path correct floor 2",       "floor_2_corridor_A" in r["path_nodes"])
    print(f"         Directions: {r['directions'][:80]}...")
except Exception as e:
    check("Code-mixed query", False, str(e))

# ── 6. Emergency query ────────────────────────────────────
print("\n[Emergency Query]")
try:
    r = post("/query/text", {"query": "emergency kahan hai", "current_node": "main_entrance"})
    check("Emergency -> 2 steps",    len(r["path_nodes"]) == 2)
    check("Dest = emergency",        r["destination_node_id"] == "emergency")
except Exception as e:
    check("Emergency query", False, str(e))

# ── 7. Admin: toggle unavailable ─────────────────────────
print("\n[Admin Toggle]")
try:
    r = patch("/locations/cardiology_opd/availability",
              {"is_available": False, "reason": "Dr. Mehta on leave"})
    check("Toggle returns success",  r["success"] == True)
except Exception as e:
    check("Admin toggle", False, str(e))

# ── 8. Query shows warning after toggle ───────────────────
print("\n[Warning After Toggle]")
try:
    r = post("/query/text", {"query": "where is cardiology", "current_node": "main_entrance"})
    check("Warning shown",           len(r["warnings"]) > 0)
    check("Still navigates to dest", r["destination_node_id"] == "cardiology_opd")
    if r["warnings"]:
        print(f"         Warning: {r['warnings'][0][:80]}")
except Exception as e:
    check("Warning after toggle", False, str(e))

# ── 9. Reset availability ─────────────────────────────────
print("\n[Reset Availability]")
try:
    r = patch("/locations/cardiology_opd/availability", {"is_available": True})
    check("Reset returns success",   r["success"] == True)
    # Verify no warning after reset
    r2 = post("/query/text", {"query": "where is cardiology", "current_node": "main_entrance"})
    check("No warning after reset",  len(r2["warnings"]) == 0)
except Exception as e:
    check("Reset availability", False, str(e))

# ── 10. QR endpoint ───────────────────────────────────────
print("\n[QR Scan]")
try:
    r = post("/query/qr", {"qr_data": "node:reception"})
    check("QR confirmed",            r["confirmed"] == True)
    check("QR sets reception",       r["current_location"] == "reception")
    check("Display name correct",    r["display_name"] == "Reception")
except Exception as e:
    check("QR endpoint", False, str(e))

# ── 11. Location from QR used in next query ───────────────
print("\n[Location Continuity]")
try:
    # From reception (1 hop to pharmacy vs 3 hops from main_entrance)
    r = post("/query/text", {"query": "where can I get medicines", "current_node": "reception"})
    check("From reception to pharmacy", r["destination_node_id"] == "pharmacy")
    check("Path shorter from reception", len(r["path_nodes"]) <= 3)
except Exception as e:
    check("Location continuity", False, str(e))

# ── 12. Locations list ────────────────────────────────────
print("\n[Locations List]")
try:
    r = get("/locations")
    check("Returns 20 locations",   r["total"] == 20)
    node_ids = [loc["node_id"] for loc in r["locations"]]
    check("Has cardiology_opd",     "cardiology_opd" in node_ids)
    check("Has emergency",          "emergency" in node_ids)
except Exception as e:
    check("Locations list", False, str(e))

# ── 13. Benchmark results file ────────────────────────────
print("\n[Benchmark Results]")
import os
from pathlib import Path
results_path = Path("evaluation/results/benchmark_results.json")
check("benchmark_results.json exists", results_path.exists())
if results_path.exists():
    with open(results_path, "r", encoding="utf-8") as f:
        bm = json.load(f)
    nc = bm["navcore_dual_memory"]
    kw = bm["keyword_baseline"]
    check("NavCore beats keyword baseline",
          nc["destination_accuracy"] > kw["destination_accuracy"])
    check("NavCore junction accuracy > 80%",
          nc["junction_accuracy"] >= 0.80)
    check("NavCore path accuracy > 0%",
          nc["path_accuracy"] > 0)
    print(f"         Keyword: {kw['destination_accuracy']:.1%}  "
          f"NavCore: {nc['destination_accuracy']:.1%}  "
          f"Junction: {nc['junction_accuracy']:.1%}")

# ── 14. File structure ────────────────────────────────────
print("\n[Required Files]")
required = [
    "core/config.py", "core/embeddings.py", "core/qdrant_client.py",
    "core/graph.py", "core/ollama_client.py",
    "agents/workflow.py", "agents/state.py",
    "api/main.py", "api/routes/query.py",
    "evaluation/benchmark.py", "evaluation/metrics.py",
    "evaluation/keyword_baseline.py", "evaluation/flat_semantic_baseline.py",
    "evaluation/test_set_200.json",
    "data/hospitals/sample_hospital/graph.json",
    "data/hospitals/sample_hospital/aliases.json",
    "frontend/pages/index.tsx", "frontend/pages/admin.tsx",
    "frontend/components/FloorMap.tsx", "frontend/components/VoiceInput.tsx",
    "README.md", "BENCHMARK.md", "Dockerfile", "docker-compose.yml",
    "requirements.txt", ".gitignore",
]
for f in required:
    check(f, os.path.exists(f))

# ── Summary ───────────────────────────────────────────────
print("\n" + "="*55)
print(f"PASSED: {len(passed)}   FAILED: {len(failed)}")
if failed:
    print("\nFailed checks:")
    for f in failed:
        print(f"  - {f}")
else:
    print("\nAll checks passed.")
print("="*55)
sys.exit(0 if not failed else 1)
