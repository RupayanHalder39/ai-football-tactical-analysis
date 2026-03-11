export interface ApiEvent {
  timestamp?: string;
  timestamp_seconds?: number;
  event: string;
  team?: string;
  player?: string;
  confidence?: number;
  x?: number;
  y?: number;
  outcome?: string;
}

export interface ApiPossessionSummary {
  [team: string]: number;
}

export interface ApiPossessionSegment {
  team: string;
  start: string;
  end: string;
}

export interface ApiJobResponse {
  job_id: string;
}

export interface ApiJobStatus {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

export interface ApiJobResult {
  match_metadata?: Record<string, unknown>;
  frames?: ApiFrameResult[];
  events?: ApiEvent[];
  possession_summary?: ApiPossessionSummary;
  possession_segments?: ApiPossessionSegment[];
  status?: string;
}

export interface ApiFrameResult {
  frame_index?: number;
  timestamp_seconds?: number | null;
  timestamp_match_clock?: string | null;
  players?: ApiPlayer[];
  ball?: ApiBall | null;
  analytics?: Record<string, unknown>;
}

export interface ApiPlayer {
  track_id?: number;
  bbox?: number[];
  team?: string;
  x?: number;
  y?: number;
  pitch_x?: number | null;
  pitch_y?: number | null;
  pitch_point?: [number, number] | null;
}

export interface ApiBall {
  bbox?: number[];
  x?: number;
  y?: number;
  pitch_x?: number | null;
  pitch_y?: number | null;
}

export interface UIEvent {
  id: string;
  timestamp: number;
  type: 'pass' | 'dribble' | 'shot' | 'tackle' | 'interception' | 'goal' | string;
  team: 'Team_A' | 'Team_B' | string;
  player: string;
  x: number;
  y: number;
  outcome: 'success' | 'failed' | string;
}

export interface UIPossessionSummary {
  team: string;
  possession: number;
}

export interface UIPossessionSegment {
  team: 'Team_A' | 'Team_B' | string;
  startTime: number;
  endTime: number;
}

export interface UIPlayerAnalytics {
  playerId: string;
  playerName: string;
  team: 'Team_A' | 'Team_B' | string;
  x: number;
  y: number;
  speed: number;
  distance: number;
  heatmapIntensity: number;
}

export interface UIJob {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  fileName: string;
  createdAt: string;
  progress: number;
  resultLink?: string;
}
