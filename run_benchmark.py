"""Standalone benchmark runner — executes all 3 conditions and saves results.

Run from navcore/ directory:
    python run_benchmark.py
"""

import sys
import json
import time

sys.path.insert(0, ".")

from core.config import Config, setup_logging
setup_logging()

import logging
logger = logging.getLogger(__name__)

print("\n" + "=" * 60)
print("NavCore Benchmark — Starting")
print("=" * 60)

# ── Initialize all dependencies ──────────────────────────────
print("\n[1/5] Loading infrastructure...")
t0 = time.time()
from core.qdrant_client import QdrantManager
from core.embeddings import EmbeddingManager
from core.graph import SpatialGraph
from core.ollama_client import OllamaManager

qdrant  = QdrantManager()
embedder = EmbeddingManager()
graph   = SpatialGraph()
graph.load_from_json(f"{Config.DATA_DIR}/graph.json")
print(f"       Infrastructure loaded in {(time.time()-t0)*1000:.0f}ms")

print("\n[2/5] Initializing agents...")
from agents.retrieval          import init_retrieval
from agents.path_planner       import init_path_planner
from agents.direction_generator import init_direction_generator
from agents.disambiguation     import init_disambiguation
from agents.workflow           import build_workflow

ollama = None
try:
    ollama = OllamaManager()
    if ollama.check_health():
        print("       Ollama: available (Llama 3.2 3B)")
    else:
        ollama = None
        print("       Ollama: NOT available — will use fallback directions")
except Exception:
    print("       Ollama: NOT available — will use fallback directions")

init_retrieval(qdrant, embedder)
init_path_planner(graph)
init_direction_generator(ollama, graph)
init_disambiguation(graph)
workflow = build_workflow()
print("       LangGraph workflow compiled")

# ── Run benchmark ─────────────────────────────────────────────
print("\n[3/5] Running 3-condition benchmark (200 queries each)...")
print("      This takes ~5-10 minutes on CPU. Progress logged below.\n")

from evaluation.benchmark import run_benchmark

results = run_benchmark(
    qdrant=qdrant,
    embedder=embedder,
    graph=graph,
    workflow=workflow,
)

# ── Print results summary ─────────────────────────────────────
kw  = results["keyword_baseline"]
fl  = results["flat_semantic"]
nc  = results["navcore_dual_memory"]
cmp = results["comparison"]

print("\n" + "=" * 60)
print("BENCHMARK RESULTS")
print("=" * 60)
print(f"\n{'Condition':<30} {'Dest Acc':>10} {'Path Acc':>10} {'Junc Acc':>10}")
print("-" * 62)
print(f"{'A — Keyword Baseline':<30} {kw['destination_accuracy']:>9.1%} {'N/A':>10} {'N/A':>10}")
print(f"{'B — Flat Semantic RAG':<30} {fl['destination_accuracy']:>9.1%} {'N/A':>10} {'N/A':>10}")
print(f"{'C — NavCore Dual-Memory':<30} {nc['destination_accuracy']:>9.1%} {nc['path_accuracy']:>9.1%} {nc['junction_accuracy']:>9.1%}")
print("=" * 62)
print(f"\nNavCore vs Flat Semantic: {cmp['destination_accuracy_delta']}")
print(f"NavCore Junction Accuracy: {cmp['junction_accuracy_delta']}")
print(f"NavCore beats Flat Semantic: {cmp['navcore_beats_flat_semantic']}")
print(f"NavCore beats Keyword: {cmp['navcore_beats_keyword']}")

print("\nPer-Language Destination Accuracy (NavCore):")
for lang, acc in nc["language_accuracy"].items():
    label = {"hi": "Hindi", "mr": "Marathi", "en": "English", "hi-mix": "Code-mixed"}.get(lang, lang)
    print(f"  {label:<15}: {acc:.1%}")

print(f"\nLatency (NavCore): P50={nc['p50_latency_ms']:.0f}ms  P95={nc['p95_latency_ms']:.0f}ms  Avg={nc['avg_latency_ms']:.0f}ms")
print(f"Results saved to: evaluation/results/benchmark_results.json")
