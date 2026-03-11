import { useEffect, useMemo, useState } from 'react';
import { Card } from '../components/Card';
import { PossessionChart } from '../components/PossessionChart';
import { PossessionTimeline } from '../components/PossessionTimeline';
import { PlayerHeatmap } from '../components/PlayerHeatmap';
import { EventTimelinePanel } from '../components/EventTimelinePanel';
import { getJobResult } from '../data/api';
import { adaptEvents, adaptPossessionSegments, adaptPossessionSummary, buildPlayerAnalytics } from '../data/adapters';
import { UIEvent, UIPossessionSegment, UIPossessionSummary, UIPlayerAnalytics } from '../data/types';
import { TrendingUp, Activity, Users, Target } from 'lucide-react';

export function TacticalAnalysisTool() {
  const [events, setEvents] = useState<UIEvent[]>([]);
  const [possessionSummary, setPossessionSummary] = useState<UIPossessionSummary[]>([]);
  const [possessionSegments, setPossessionSegments] = useState<UIPossessionSegment[]>([]);
  const [players, setPlayers] = useState<UIPlayerAnalytics[]>([]);
  const [selectedMatch, setSelectedMatch] = useState('latest');

  useEffect(() => {
    const fetchData = async () => {
      const matchId = selectedMatch === 'latest' ? localStorage.getItem('lastJobId') : selectedMatch;
      if (!matchId) {
        setEvents([]);
        setPossessionSummary([]);
        setPossessionSegments([]);
        setPlayers([]);
        return;
      }

      const result = await getJobResult(matchId, matchId);
      setEvents(adaptEvents(result.events || []));
      setPossessionSummary(adaptPossessionSummary(result.possession_summary || {}));
      setPossessionSegments(adaptPossessionSegments(result.possession_segments || []));
      setPlayers(buildPlayerAnalytics(result.frames || []));
    };

    fetchData();
  }, [selectedMatch]);

  const teamAPlayers = useMemo(() => players.filter((p) => p.team === 'Team_A'), [players]);
  const teamBPlayers = useMemo(() => players.filter((p) => p.team === 'Team_B'), [players]);

  const avgSpeedTeamA = teamAPlayers.length
    ? (teamAPlayers.reduce((sum, p) => sum + p.speed, 0) / teamAPlayers.length).toFixed(1)
    : '0.0';
  const avgSpeedTeamB = teamBPlayers.length
    ? (teamBPlayers.reduce((sum, p) => sum + p.speed, 0) / teamBPlayers.length).toFixed(1)
    : '0.0';

  const totalDistanceTeamA = teamAPlayers.reduce((sum, p) => sum + p.distance, 0);
  const totalDistanceTeamB = teamBPlayers.reduce((sum, p) => sum + p.distance, 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-3xl text-gray-800 mb-2">Tactical Analysis Tool</h1>
          <p className="text-gray-600">Deep dive into team tactics, formations, and patterns</p>
        </div>

        <div className="flex items-center gap-3">
          <label className="text-sm text-gray-600">Match Selector</label>
          <select
            value={selectedMatch}
            onChange={(e) => setSelectedMatch(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white"
          >
            <option value="latest">Latest</option>
            <option value="sample_match">sample_match</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg p-6 shadow-md">
          <div className="flex items-center justify-between mb-2">
            <div className="p-2 bg-white/20 rounded-lg">
              <Target className="w-6 h-6" />
            </div>
            <span className="text-2xl">{possessionSummary[0]?.possession ?? 0}%</span>
          </div>
          <p className="text-sm opacity-90">Team A Possession</p>
        </div>

        <div className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-lg p-6 shadow-md">
          <div className="flex items-center justify-between mb-2">
            <div className="p-2 bg-white/20 rounded-lg">
              <Target className="w-6 h-6" />
            </div>
            <span className="text-2xl">{possessionSummary[1]?.possession ?? 0}%</span>
          </div>
          <p className="text-sm opacity-90">Team B Possession</p>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg p-6 shadow-md">
          <div className="flex items-center justify-between mb-2">
            <div className="p-2 bg-white/20 rounded-lg">
              <Activity className="w-6 h-6" />
            </div>
            <span className="text-2xl">{events.length}</span>
          </div>
          <p className="text-sm opacity-90">Total Events</p>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-lg p-6 shadow-md">
          <div className="flex items-center justify-between mb-2">
            <div className="p-2 bg-white/20 rounded-lg">
              <Users className="w-6 h-6" />
            </div>
            <span className="text-2xl">{players.length}</span>
          </div>
          <p className="text-sm opacity-90">Players Tracked</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Possession Summary">
          <PossessionChart data={possessionSummary} />
        </Card>

        <Card title="Team Statistics Comparison">
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h4 className="font-semibold text-blue-800 mb-3">Team A</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-700">Avg Speed:</span>
                  <span className="font-semibold text-blue-600">{avgSpeedTeamA} km/h</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-700">Total Distance:</span>
                  <span className="font-semibold text-blue-600">{(totalDistanceTeamA / 1000).toFixed(1)} km</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-700">Players:</span>
                  <span className="font-semibold text-blue-600">{teamAPlayers.length}</span>
                </div>
              </div>
            </div>

            <div className="p-4 bg-red-50 rounded-lg border border-red-200">
              <h4 className="font-semibold text-red-800 mb-3">Team B</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-700">Avg Speed:</span>
                  <span className="font-semibold text-red-600">{avgSpeedTeamB} km/h</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-700">Total Distance:</span>
                  <span className="font-semibold text-red-600">{(totalDistanceTeamB / 1000).toFixed(1)} km</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-700">Players:</span>
                  <span className="font-semibold text-red-600">{teamBPlayers.length}</span>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>

      <Card title="Match Possession Timeline">
        <PossessionTimeline segments={possessionSegments} />
      </Card>

      <Card title="Player Position Heatmap">
        <PlayerHeatmap players={players} />
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-700">
            <strong>Interactive Heatmap:</strong> Hover over player positions to see detailed metrics
            including speed, distance covered, and activity levels.
          </p>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Event Timeline">
          <EventTimelinePanel events={events.slice(0, 8)} />
        </Card>

        <Card title="Advanced Metrics (Coming Soon)">
          <div className="space-y-3">
            <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg border border-purple-200">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-purple-200 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-purple-700" />
                </div>
                <h4 className="font-semibold text-purple-800">Passing Networks</h4>
              </div>
              <p className="text-sm text-purple-700">
                Visualize player connections and passing patterns with weighted network graphs.
              </p>
            </div>

            <div className="p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg border border-green-200">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-green-200 rounded-lg flex items-center justify-center">
                  <Target className="w-5 h-5 text-green-700" />
                </div>
                <h4 className="font-semibold text-green-800">xT Maps</h4>
              </div>
              <p className="text-sm text-green-700">
                Expected Threat analysis showing high-value zones and dangerous areas on the pitch.
              </p>
            </div>

            <div className="p-4 bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg border border-orange-200">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-orange-200 rounded-lg flex items-center justify-center">
                  <Activity className="w-5 h-5 text-orange-700" />
                </div>
                <h4 className="font-semibold text-orange-800">Formation Detection</h4>
              </div>
              <p className="text-sm text-orange-700">
                Automatic identification and visualization of team formations throughout the match.
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
