"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import {
  Search,
  Download,
  FileJson,
  Video,
  Upload,
  Loader2,
} from "lucide-react";
import type { SearchResult, Season } from "@/lib/types";
import { searchPlayers } from "@/lib/api";

interface HeaderProps {
  selectedSeason: Season | null;
  onSelectSeason: (playerId: string, season: string) => void;
  onExportJSON: () => void;
  onRender: () => void;
  onUpload: () => void;
  loading?: boolean;
}

export default function Header({
  selectedSeason,
  onSelectSeason,
  onExportJSON,
  onRender,
  onUpload,
  loading,
}: HeaderProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [searching, setSearching] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleSearch = useCallback((value: string) => {
    setQuery(value);
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    if (!value.trim()) {
      setResults([]);
      setShowDropdown(false);
      return;
    }
    timeoutRef.current = setTimeout(async () => {
      try {
        setSearching(true);
        const data = await searchPlayers(value);
        setResults(data);
        setShowDropdown(data.length > 0);
      } catch {
        setResults([]);
      } finally {
        setSearching(false);
      }
    }, 300);
  }, []);

  const handleSelectResult = (playerId: string, season: string) => {
    onSelectSeason(playerId, season);
    setShowDropdown(false);
    setQuery("");
    setResults([]);
  };

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="flex items-center gap-4 px-6 py-4 border-b border-[rgba(201,162,74,0.15)] bg-[rgba(11,13,18,0.8)] backdrop-blur-sm">
      {/* Search */}
      <div className="relative flex-1 max-w-md" ref={dropdownRef}>
        <div className="relative">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-sxi-white/30"
          />
          <input
            type="text"
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="Search player..."
            className="w-full pl-10 pr-4 py-2 bg-[rgba(245,247,250,0.05)] border border-[rgba(201,162,74,0.15)] rounded-lg text-sm text-sxi-white placeholder:text-sxi-white/30 focus:outline-none focus:border-sxi-gold/40 transition-colors"
          />
          {searching && (
            <Loader2
              size={14}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-sxi-gold animate-spin"
            />
          )}
        </div>

        {showDropdown && (
          <div className="absolute top-full left-0 right-0 mt-1 glass-panel p-1 z-50 max-h-64 overflow-y-auto">
            {results.map((r) =>
              r.seasons.map((s) => (
                <button
                  key={`${r.player_id}-${s}`}
                  onClick={() => handleSelectResult(r.player_id, s)}
                  className="w-full text-left px-3 py-2 rounded-md text-sm hover:bg-[rgba(201,162,74,0.1)] transition-colors flex items-center justify-between"
                >
                  <span className="text-sxi-white">{r.player_name}</span>
                  <span className="text-sxi-white/40 text-xs">{s}</span>
                </button>
              ))
            )}
          </div>
        )}
      </div>

      {/* Selected indicator */}
      {selectedSeason && (
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[rgba(201,162,74,0.08)] border border-sxi-gold/20">
          <span className="text-sm text-sxi-gold font-medium">
            {selectedSeason.display_name}
          </span>
          <span className="text-xs text-sxi-white/40">
            {selectedSeason.season_label}
          </span>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={onExportJSON}
          disabled={!selectedSeason || loading}
          className="btn-outline flex items-center gap-2 text-sm disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <FileJson size={14} />
          <span className="hidden sm:inline">Export</span>
        </button>
        <button
          onClick={onRender}
          disabled={!selectedSeason || loading}
          className="btn-outline flex items-center gap-2 text-sm disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <Video size={14} />
          <span className="hidden sm:inline">Render</span>
        </button>
        <button
          onClick={onUpload}
          disabled={!selectedSeason || loading}
          className="btn-gold flex items-center gap-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? <Loader2 size={14} className="animate-spin" /> : <Upload size={14} />}
          <span className="hidden sm:inline">Upload</span>
        </button>
      </div>
    </header>
  );
}
