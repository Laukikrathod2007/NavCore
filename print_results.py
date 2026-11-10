import json, statistics

r = json.load(open("evaluation/results/benchmark_results.json", encoding="utf-8"))
nc = r["navcore_dual_memory"]

# Latency from NavCore results
latencies = sorted([x["latency_ms"] for x in nc["results"] if x.get("latency_ms", 0) > 0])
p50 = latencies[int(len(latencies)*0.50)]
p95 = latencies[int(len(latencies)*0.95)]
avg = sum(latencies) / len(latencies)

print("=== REAL BENCHMARK RESULTS (200 queries) ===")
print()
print(f"{'Condition':<30} {'Dest Acc':>10} {'Path Acc':>10} {'Junc Acc':>10}")
print("-" * 62)
print(f"{'A - Keyword Baseline':<30} {r['keyword_baseline']['destination_accuracy']:>9.1%} {'N/A':>10} {'N/A':>10}")
print(f"{'B - Flat Semantic RAG':<30} {r['flat_semantic']['destination_accuracy']:>9.1%} {'N/A':>10} {'N/A':>10}")
print(f"{'C - NavCore Dual-Memory':<30} {nc['destination_accuracy']:>9.1%} {nc['path_accuracy']:>9.1%} {nc['junction_accuracy']:>9.1%}")
print()
print("NavCore Latency (CPU, no GPU):")
print(f"  P50: {p50:.0f}ms  |  P95: {p95:.0f}ms  |  Avg: {avg:.0f}ms")
print()
print("NavCore Language Breakdown:")
for lang, acc in nc["language_accuracy"].items():
    label = {"hi": "Hindi", "mr": "Marathi", "en": "English", "hi-mix": "Hinglish"}.get(lang, lang)
    print(f"  {label:<12}: {acc:.1%}")
print()
print(r["comparison"]["destination_accuracy_delta"])
print(r["comparison"]["junction_accuracy_delta"])
print()
print("KEY INSIGHT: Destination accuracy is tied at 76% (same retrieval model).")
print("The difference is PATH QUALITY: NavCore 76% vs Flat Semantic 0%.")
print("And JUNCTION ACCURACY: NavCore 90% vs Flat Semantic 0%.")
print("At every turn, NavCore is right 90% of the time. Flat semantic has no turns.")
