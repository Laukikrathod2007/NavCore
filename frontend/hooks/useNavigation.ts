import { useState, useCallback } from "react";
import { resolveQueryOffline } from "../lib/hospitalData";
import { apiUrl } from "../lib/urls";

export interface NavigationResult {
  destination: string;
  destination_node_id: string;
  room_number?: string | null;
  floor: number;
  detected_language: string;
  directions: string;
  path_nodes: string[];
  warnings: string[];
  requires_disambiguation: boolean;
  latency_ms: number;
}

export function useNavigation(defaultStart = "main_entrance") {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<NavigationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(
    async (queryText: string, startNode = defaultStart) => {
      if (!queryText.trim()) return;
      setLoading(true);
      setError(null);

      try {
        const res = await fetch(apiUrl("/query/text"), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query: queryText,
            current_node: startNode,
          }),
        });

        if (!res.ok) {
          throw new Error(`Server returned ${res.status}`);
        }

        const data: NavigationResult = await res.json();
        setResult(data);
      } catch (err) {
        // Fallback to local offline resolution
        const offlineRes = resolveQueryOffline(queryText, startNode);
        setResult(offlineRes);
      } finally {
        setLoading(false);
      }
    },
    [defaultStart]
  );

  return {
    query,
    setQuery,
    loading,
    result,
    error,
    search,
  };
}

