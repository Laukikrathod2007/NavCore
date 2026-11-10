/**
 * Benchmark & Evaluation Data for NavCore
 * Sourced directly from BENCHMARK.md and NavCore 200-query test set.
 */

export interface BenchmarkModelScore {
  name: string;
  category: "NavCore (Proposed)" | "Cloud Vector RAG" | "Keyword Baseline" | "Zero-Shot LLM";
  destinationAccuracy: number; // percentage
  junctionAccuracy: number;    // percentage
  avgLatencyMs: number;
  offlineCapable: boolean;
  junctionHallucinations: number;
  hardware: string;
}

export const BENCHMARK_COMPARISONS: BenchmarkModelScore[] = [
  {
    name: "NavCore Dual-Memory",
    category: "NavCore (Proposed)",
    destinationAccuracy: 76.0,
    junctionAccuracy: 90.0,
    avgLatencyMs: 340,
    offlineCapable: true,
    junctionHallucinations: 0,
    hardware: "Local Mini-PC / Laptop (CPU only)",
  },
  {
    name: "Standalone Llama 3.2 3B",
    category: "Zero-Shot LLM",
    destinationAccuracy: 31.0,
    junctionAccuracy: 41.0,
    avgLatencyMs: 1250,
    offlineCapable: true,
    junctionHallucinations: 59,
    hardware: "Local Ollama 3B",
  },
  {
    name: "Cloud Pinecone / Weaviate RAG",
    category: "Cloud Vector RAG",
    destinationAccuracy: 64.5,
    junctionAccuracy: 68.0,
    avgLatencyMs: 1840,
    offlineCapable: false,
    junctionHallucinations: 32,
    hardware: "Cloud API + GPT-4o-mini",
  },
  {
    name: "BM25 Keyword Matching",
    category: "Keyword Baseline",
    destinationAccuracy: 23.0,
    junctionAccuracy: 47.0,
    avgLatencyMs: 45,
    offlineCapable: true,
    junctionHallucinations: 53,
    hardware: "Local CPU",
  },
];

export const LANGUAGE_PERFORMANCE = [
  { language: "Hindi (हिंदी)", queryCount: 50, accuracy: 78.0, junctionRate: 92.0 },
  { language: "Marathi (मराठी)", queryCount: 50, accuracy: 74.0, junctionRate: 88.0 },
  { language: "English", queryCount: 50, accuracy: 82.0, junctionRate: 94.0 },
  { language: "Hinglish / Code-Mixed", queryCount: 50, accuracy: 70.0, junctionRate: 86.0 },
];

export const CORE_METRICS = [
  { label: "Destination Accuracy", value: "76%", sub: "Across 200 real patient queries in 4 languages", highlight: true },
  { label: "Junction Accuracy", value: "90%", sub: "Zero topological graph hallucinations", highlight: true },
  { label: "Hot-Path Latency", value: "<15ms", sub: "Sub-15ms vector retrieval via Qdrant Edge", highlight: true },
  { label: "Edge Hardware Cost", value: "$0", sub: "Runs completely offline on commodity laptops & NavCore devices", highlight: false },
];

