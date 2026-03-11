import { useState } from 'react';
import { UIEvent, UIPossessionSummary } from '../data/types';
import { ChevronRight, ChevronDown } from 'lucide-react';

interface VideoAnalysisSidebarProps {
  events: UIEvent[];
  currentTime: number;
  onEventClick: (timestamp: number) => void;
  possessionData: UIPossessionSummary[];
  showStats: boolean;
}

export function VideoAnalysisSidebar({
  events,
  currentTime,
  onEventClick,
  possessionData,
  showStats,
}: VideoAnalysisSidebarProps) {
  const [expandedSection, setExpandedSection] = useState<'events' | 'possession' | 'metrics'>('events');

  if (!showStats) {
    return null;
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const toggleSection = (section: 'events' | 'possession' | 'metrics') => {
    setExpandedSection(expandedSection === section ? 'events' : section);
  };

  return (
    <div className="space-y-3 h-full overflow-y-auto">
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <button
          onClick={() => toggleSection('events')}
          className="w-full px-4 py-3 flex items-center justify-between bg-gradient-to-r from-gray-50 to-white hover:from-gray-100 hover:to-gray-50 transition-colors"
        >
          <span className="font-semibold text-gray-800">Event Timeline</span>
          {expandedSection === 'events' ? (
            <ChevronDown className="w-5 h-5 text-gray-600" />
          ) : (
            <ChevronRight className="w-5 h-5 text-gray-600" />
          )}
        </button>

        {expandedSection === 'events' && (
          <div className="p-4 max-h-96 overflow-y-auto">
            <div className="space-y-2">
              {events.map((event) => {
                const isNearCurrent = Math.abs(event.timestamp - currentTime) < 5;

                return (
                  <button
                    key={event.id}
                    onClick={() => onEventClick(event.timestamp)}
                    className={`
                      w-full text-left p-3 rounded-lg border-l-4 transition-all
                      ${event.team === 'Team_A' ? 'border-blue-500' : 'border-red-500'}
                      ${isNearCurrent ? 'bg-green-50 ring-2 ring-green-400' : 'bg-gray-50 hover:bg-gray-100'}
                    `}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-mono text-gray-500">
                        {formatTime(event.timestamp)}
                      </span>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-green-200 text-green-800">
                        success
                      </span>
                    </div>
                    <p className="font-semibold text-gray-800 text-sm capitalize">{event.type}</p>
                    <p className="text-xs text-gray-600">{event.player}</p>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <button
          onClick={() => toggleSection('possession')}
          className="w-full px-4 py-3 flex items-center justify-between bg-gradient-to-r from-gray-50 to-white hover:from-gray-100 hover:to-gray-50 transition-colors"
        >
          <span className="font-semibold text-gray-800">Possession Summary</span>
          {expandedSection === 'possession' ? (
            <ChevronDown className="w-5 h-5 text-gray-600" />
          ) : (
            <ChevronRight className="w-5 h-5 text-gray-600" />
          )}
        </button>

        {expandedSection === 'possession' && (
          <div className="p-4">
            <div className="space-y-3">
              {possessionData.map((team) => (
                <div key={team.team}>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="font-semibold text-gray-700">{team.team}</span>
                    <span className="font-semibold text-gray-900">{team.possession}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${team.team === 'Team_A' ? 'bg-blue-500' : 'bg-red-500'}`}
                      style={{ width: `${team.possession}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <button
          onClick={() => toggleSection('metrics')}
          className="w-full px-4 py-3 flex items-center justify-between bg-gradient-to-r from-gray-50 to-white hover:from-gray-100 hover:to-gray-50 transition-colors"
        >
          <span className="font-semibold text-gray-800">Tactical Metrics</span>
          {expandedSection === 'metrics' ? (
            <ChevronDown className="w-5 h-5 text-gray-600" />
          ) : (
            <ChevronRight className="w-5 h-5 text-gray-600" />
          )}
        </button>

        {expandedSection === 'metrics' && (
          <div className="p-4">
            <div className="space-y-3 text-sm">
              <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                <h4 className="font-semibold text-purple-800 mb-1">Passing Networks</h4>
                <p className="text-xs text-purple-700">Coming soon: Visualize player connections</p>
              </div>
              <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                <h4 className="font-semibold text-green-800 mb-1">xT Maps</h4>
                <p className="text-xs text-green-700">Coming soon: Expected Threat zones</p>
              </div>
              <div className="p-3 bg-orange-50 rounded-lg border border-orange-200">
                <h4 className="font-semibold text-orange-800 mb-1">Team Centroid</h4>
                <p className="text-xs text-orange-700">Coming soon: Team shape analysis</p>
              </div>
              <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                <h4 className="font-semibold text-blue-800 mb-1">Heatmaps</h4>
                <p className="text-xs text-blue-700">Coming soon: Player position density</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
