import {
  ApiEvent,
  ApiPossessionSummary,
  ApiPossessionSegment,
  ApiFrameResult,
  UIEvent,
  UIPossessionSummary,
  UIPossessionSegment,
  UIPlayerAnalytics,
} from './types';

const TEAM_COLOR_MAP: Record<string, string> = {
  Team_A: 'Team_A',
  Team_B: 'Team_B',
};

// Map backend event schema to UI timeline events used by overlays and panels.
export function adaptEvents(events: ApiEvent[]): UIEvent[] {
  return events.map((e, idx) => ({
    id: String(idx + 1),
    timestamp: e.timestamp_seconds ?? 0,
    type: e.event ?? 'pass',
    team: TEAM_COLOR_MAP[e.team ?? 'Team_A'] || e.team || 'Team_A',
    player: e.player ?? 'unknown',
    x: (e as any).x ?? 0,
    y: (e as any).y ?? 0,
    outcome: (e as any).outcome ?? 'success',
  }));
}

// Convert backend { team: percent } to chart-friendly array.
export function adaptPossessionSummary(summary: ApiPossessionSummary): UIPossessionSummary[] {
  return Object.entries(summary).map(([team, possession]) => ({
    team,
    possession,
  }));
}

// Convert backend clock strings into seconds for UI timeline rendering.
export function adaptPossessionSegments(segments: ApiPossessionSegment[]): UIPossessionSegment[] {
  return segments.map((s) => ({
    team: s.team,
    startTime: parseClockToSeconds(s.start),
    endTime: parseClockToSeconds(s.end),
  }));
}

// Build player analytics from frame-level tracking data.
export function buildPlayerAnalytics(frames: ApiFrameResult[]): UIPlayerAnalytics[] {
  const byPlayer: Record<string, UIPlayerAnalytics> = {};

  frames.forEach((frame) => {
    (frame.players || []).forEach((p, idx) => {
      const id = String(p.track_id ?? idx);
      const x = p.pitch_x ?? p.x ?? 0;
      const y = p.pitch_y ?? p.y ?? 0;

      if (!byPlayer[id]) {
        byPlayer[id] = {
          playerId: id,
          playerName: `Player ${id}`,
          team: (p.team as string) || 'Team_A',
          x,
          y,
          speed: 0,
          distance: 0,
          heatmapIntensity: 5,
        };
      } else {
        byPlayer[id].x = x;
        byPlayer[id].y = y;
      }
    });
  });

  return Object.values(byPlayer);
}

function parseClockToSeconds(clock: string): number {
  if (!clock) return 0;
  const parts = clock.split(':').map((v) => parseInt(v, 10));
  if (parts.length === 2) {
    return parts[0] * 60 + parts[1];
  }
  return 0;
}
