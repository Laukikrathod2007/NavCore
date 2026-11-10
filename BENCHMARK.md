# NavCore Benchmark

## Full evaluation run

The benchmark runner evaluated all 200 queries in `evaluation/test_set_200.json` against three conditions. The test set contains 50 queries for each of English, Hindi, Marathi, and code-mixed Hindi-English. Results below come from the latest complete run saved in `evaluation/results/benchmark_results.json`.

| Metric | Keyword baseline | Flat semantic | NavCore dual-memory |
|---|---:|---:|---:|
| Queries | 200 | 200 | 200 |
| Destination accuracy | 39.0% | 76.0% | **76.0%** |
| Exact path accuracy | Not applicable | Not applicable | **76.0%** |
| Junction next-edge accuracy | No route | No route | **77.86%** |
| Average latency | Not measured | 105.61 ms | **108.88 ms** |
| P50 latency | Not measured | Not reported | **94.20 ms** |
| P95 latency | Not measured | Not reported | **163.33 ms** |

NavCore and flat semantic retrieval reached the same destination accuracy on this test set. The graph pipeline adds a computed route: its exact path matched the annotated expected path on 76% of the queries. At annotated junctions, the predicted route selected the same next graph node as the expected route 77.86% of the time. Keyword matching reached 39% destination accuracy.

The junction metric compares the next node after each annotated junction in the expected route with the next node in the predicted route. Missing junctions and missing routes count as incorrect. The flat-semantic and keyword baselines do not produce routes, so path and turn metrics are not applicable to those conditions.

## Per-language destination accuracy

| Language | Queries | Keyword | Flat semantic | NavCore |
|---|---:|---:|---:|---:|
| English | 50 | 60.0% | 88.0% | **88.0%** |
| Hindi | 50 | 40.0% | 66.0% | **66.0%** |
| Marathi | 50 | 0.0% | 74.0% | **74.0%** |
| Code-mixed Hindi-English | 50 | 56.0% | 76.0% | **76.0%** |

## Run conditions

- Embedding model: `intfloat/multilingual-e5-small` (384 dimensions).
- Execution: CPU embedding inference; the model was loaded from the local Hugging Face cache.
- Ollama was not running, so NavCore used its template direction fallback. The flat-semantic baseline ran without an available Ollama model.
- NavCore latency is measured around each workflow invocation after dependencies and models are loaded. It includes query embedding, retrieval, routing, and direction generation; it excludes model startup and browser/audio transcription.
- The isolated benchmark Qdrant store was populated from the sample hospital graph and aliases before the run. The live NavCore Qdrant directory was left untouched.
- Run date: 2026-11-07.

These figures describe this 200-query evaluation against the sample facility data and this run configuration. They are not a substitute for validating the graph, aliases, speech path, or accessible routes in a target facility.

## Reproduce

Install the project dependencies and required embedding model, then run ingestion followed by the benchmark:

```powershell
python -m ingestion.ingest
python run_benchmark.py
```

To keep the benchmark's local Qdrant files separate from an API process that is using `qdrant_storage`, set a dedicated path for both commands:

```powershell
$env:NAVCORE_QDRANT_PATH = "C:\path\to\navcore\qdrant_benchmark_storage"
python -m ingestion.ingest
python run_benchmark.py
```

The runner rewrites `evaluation/results/benchmark_results.json` with per-query records, aggregate metrics, and language accuracy. The current implementation requires the embedding model to be available locally or downloadable during setup. Ollama directions are optional; when the service is unavailable, NavCore uses its configured fallback.
