import { useState } from 'react';
import { UIPlayerAnalytics } from '../data/types';

interface PlayerHeatmapProps {
  players: UIPlayerAnalytics[];
}

export function PlayerHeatmap({ players }: PlayerHeatmapProps) {
  const [hoveredPlayer, setHoveredPlayer] = useState<UIPlayerAnalytics | null>(null);

  const pitchWidth = 100;
  const pitchHeight = 68;

  return (
    <div className="relative">
      <svg
        viewBox={`0 0 ${pitchWidth} ${pitchHeight}`}
        className="w-full h-auto bg-green-600 rounded-lg border-2 border-white"
      >
        <rect x="0" y="0" width={pitchWidth} height={pitchHeight} fill="#15803d" stroke="white" strokeWidth="0.3" />
        <line x1={pitchWidth / 2} y1="0" x2={pitchWidth / 2} y2={pitchHeight} stroke="white" strokeWidth="0.3" />
        <circle cx={pitchWidth / 2} cy={pitchHeight / 2} r="9" fill="none" stroke="white" strokeWidth="0.3" />
        <circle cx={pitchWidth / 2} cy={pitchHeight / 2} r="0.5" fill="white" />
        <rect x="0" y="13.84" width="16.5" height="40.32" fill="none" stroke="white" strokeWidth="0.3" />
        <rect x={pitchWidth - 16.5} y="13.84" width="16.5" height="40.32" fill="none" stroke="white" strokeWidth="0.3" />
        <rect x="0" y="24.84" width="5.5" height="18.32" fill="none" stroke="white" strokeWidth="0.3" />
        <rect x={pitchWidth - 5.5} y="24.84" width="5.5" height="18.32" fill="none" stroke="white" strokeWidth="0.3" />

        {players.map((player) => {
          const opacity = player.heatmapIntensity / 10;
          const isHovered = hoveredPlayer?.playerId === player.playerId;

          return (
            <g key={player.playerId}>
              <circle
                cx={player.x}
                cy={player.y}
                r="4"
                fill={player.team === 'Team_A' ? '#3b82f6' : '#ef4444'}
                opacity={opacity * 0.3}
              />
              <circle
                cx={player.x}
                cy={player.y}
                r={isHovered ? '1.5' : '1'}
                fill={player.team === 'Team_A' ? '#3b82f6' : '#ef4444'}
                stroke="white"
                strokeWidth="0.2"
                className="cursor-pointer transition-all duration-200"
                onMouseEnter={() => setHoveredPlayer(player)}
                onMouseLeave={() => setHoveredPlayer(null)}
              />
            </g>
          );
        })}
      </svg>

      {hoveredPlayer && (
        <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-4 border border-gray-200 min-w-[200px]">
          <h4 className="font-semibold text-gray-800 mb-2">{hoveredPlayer.playerName}</h4>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Team:</span>
              <span className={hoveredPlayer.team === 'Team_A' ? 'text-blue-600' : 'text-red-600'}>
                {hoveredPlayer.team}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Speed:</span>
              <span>{hoveredPlayer.speed.toFixed(1)} km/h</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Distance:</span>
              <span>{hoveredPlayer.distance.toLocaleString()} m</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Activity:</span>
              <span>{hoveredPlayer.heatmapIntensity}/10</span>
            </div>
          </div>
        </div>
      )}

      <div className="mt-4 flex items-center justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-blue-500" />
          <span className="text-gray-600">Team A</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-red-500" />
          <span className="text-gray-600">Team B</span>
        </div>
      </div>
    </div>
  );
}
