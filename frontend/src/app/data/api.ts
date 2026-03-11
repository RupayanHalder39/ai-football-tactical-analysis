import {
  ApiEvent,
  ApiJobResponse,
  ApiJobResult,
  ApiJobStatus,
  ApiPossessionSegment,
  ApiPossessionSummary,
} from './types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function createJob(file: File): Promise<ApiJobResponse> {
  const form = new FormData();
  form.append('file', file);

  const res = await fetch(`${API_BASE}/analyze-video`, {
    method: 'POST',
    body: form,
  });

  if (!res.ok) {
    throw new Error('Failed to create job');
  }

  return res.json();
}

export async function getJobStatus(jobId: string): Promise<ApiJobStatus> {
  const res = await fetch(`${API_BASE}/job-status/${jobId}`);
  if (!res.ok) {
    throw new Error('Failed to fetch job status');
  }
  return res.json();
}

export async function getJobResult(jobId: string, matchId?: string): Promise<ApiJobResult> {
  const url = matchId ? `${API_BASE}/job-result/${jobId}?match_id=${encodeURIComponent(matchId)}` : `${API_BASE}/job-result/${jobId}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error('Failed to fetch job result');
  }
  return res.json();
}

export async function getEvents(matchId?: string): Promise<ApiEvent[]> {
  const url = matchId ? `${API_BASE}/events?match_id=${encodeURIComponent(matchId)}` : `${API_BASE}/events`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error('Failed to fetch events');
  }
  return res.json();
}

export async function getPossession(matchId?: string): Promise<ApiPossessionSummary> {
  const url = matchId ? `${API_BASE}/possession?match_id=${encodeURIComponent(matchId)}` : `${API_BASE}/possession`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error('Failed to fetch possession');
  }
  return res.json();
}

export async function getPossessionTimeline(matchId?: string): Promise<ApiPossessionSegment[]> {
  const url = matchId
    ? `${API_BASE}/possession-timeline?match_id=${encodeURIComponent(matchId)}`
    : `${API_BASE}/possession-timeline`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error('Failed to fetch possession timeline');
  }
  return res.json();
}
