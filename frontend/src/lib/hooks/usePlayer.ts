"use client";

import { useState, useCallback } from "react";
import type { Season, SearchResult } from "../types";
import { searchPlayers, loadSeason } from "../api";

export function usePlayer() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [selectedSeason, setSelectedSeason] = useState<Season | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (q: string) => {
    setQuery(q);
    if (!q.trim()) {
      setResults([]);
      return;
    }
    try {
      setLoading(true);
      setError(null);
      const data = await searchPlayers(q);
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const selectSeason = useCallback(async (playerId: string, season: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await loadSeason(playerId, season);
      setSelectedSeason(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load season");
    } finally {
      setLoading(false);
    }
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedSeason(null);
    setResults([]);
    setQuery("");
    setError(null);
  }, []);

  return {
    query,
    results,
    selectedSeason,
    loading,
    error,
    search,
    selectSeason,
    setSelectedSeason,
    clearSelection,
  };
}
