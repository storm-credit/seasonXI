import type { Season, SearchResult, EngineCheck, YouTubeMetadata, PromptResult, Settings } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8800";

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "Unknown error");
    throw new Error(`API Error ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export async function searchPlayers(query: string): Promise<SearchResult[]> {
  if (!query.trim()) return [];
  return fetchJSON<SearchResult[]>(`${API_URL}/api/search?q=${encodeURIComponent(query)}`);
}

export async function loadSeason(playerId: string, season: string): Promise<Season> {
  return fetchJSON<Season>(`${API_URL}/api/season/${encodeURIComponent(playerId)}/${encodeURIComponent(season)}`);
}

export async function assemblePrompt(playerId: string, season: string, scene: string): Promise<PromptResult> {
  return fetchJSON<PromptResult>(
    `${API_URL}/api/prompt/${encodeURIComponent(playerId)}/${encodeURIComponent(season)}?scene=${encodeURIComponent(scene)}`
  );
}

export async function triggerRender(playerId: string, season: string): Promise<{ status: string }> {
  return fetchJSON<{ status: string }>(
    `${API_URL}/api/render/${encodeURIComponent(playerId)}/${encodeURIComponent(season)}`,
    { method: "POST" }
  );
}

export async function uploadYouTube(playerId: string, season: string): Promise<{ status: string; url?: string }> {
  return fetchJSON<{ status: string; url?: string }>(
    `${API_URL}/api/upload-youtube/${encodeURIComponent(playerId)}/${encodeURIComponent(season)}`,
    { method: "POST" }
  );
}

export async function getYouTubeMetadata(playerId: string, season: string): Promise<YouTubeMetadata> {
  return fetchJSON<YouTubeMetadata>(
    `${API_URL}/api/youtube-metadata/${encodeURIComponent(playerId)}/${encodeURIComponent(season)}`
  );
}

export async function uploadImage(file: File): Promise<{ path: string }> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_URL}/api/upload-image`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "Upload failed");
    throw new Error(`Upload Error ${res.status}: ${text}`);
  }
  return res.json() as Promise<{ path: string }>;
}

export async function engineCheck(): Promise<EngineCheck[]> {
  return fetchJSON<EngineCheck[]>(`${API_URL}/api/engine-check`);
}

export async function exportJSON(playerId: string, season: string): Promise<{ status: string; path?: string }> {
  return fetchJSON<{ status: string; path?: string }>(
    `${API_URL}/api/export/${encodeURIComponent(playerId)}/${encodeURIComponent(season)}`,
    { method: "POST" }
  );
}

export interface AssetStatus {
  exists: boolean;
  filename?: string;
  size?: number;
}

export async function checkAssets(playerId: string, season: string): Promise<Record<string, AssetStatus>> {
  return fetchJSON<Record<string, AssetStatus>>(
    `${API_URL}/api/assets/${encodeURIComponent(playerId)}/${encodeURIComponent(season)}`
  );
}

export async function getSettings(): Promise<Settings> {
  return fetchJSON<Settings>(`${API_URL}/api/settings`);
}

export async function saveSettings(settings: Partial<Settings>): Promise<{ status: string }> {
  return fetchJSON<{ status: string }>(`${API_URL}/api/settings`, {
    method: "POST",
    body: JSON.stringify(settings),
  });
}
