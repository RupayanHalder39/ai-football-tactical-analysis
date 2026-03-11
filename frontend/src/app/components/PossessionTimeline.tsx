import { UIPossessionSegment } from '../data/types';

interface PossessionTimelineProps {
  segments: UIPossessionSegment[];
  totalDuration?: number;
}

export function PossessionTimeline({ segments, totalDuration = 2700 }: PossessionTimelineProps) {
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-blue-500" />
          <span className="text-gray-600">Team A Possession</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-red-500" />
          <span className="text-gray-600">Team B Possession</span>
        </div>
      </div>

      <div className="relative">
        <div className="flex h-12 rounded-lg overflow-hidden border border-gray-200">
          {segments.map((segment, index) => {
            const width = ((segment.endTime - segment.startTime) / totalDuration) * 100;
            return (
              <div
                key={index}
                className={`
                  h-full flex items-center justify-center text-xs text-white
                  transition-all duration-200 hover:opacity-80
                  ${segment.team === 'Team_A' ? 'bg-blue-500' : 'bg-red-500'}
                `}
                style={{ width: `${width}%` }}
                title={`${segment.team}: ${formatTime(segment.startTime)} - ${formatTime(segment.endTime)}`}
              >
                {width > 5 && <span className="truncate px-1">{segment.team}</span>}
              </div>
            );
          })}
        </div>

        <div className="flex justify-between mt-2 text-xs text-gray-500">
          <span>0:00</span>
          <span>{formatTime(Math.floor(totalDuration / 2))}</span>
          <span>{formatTime(totalDuration)}</span>
        </div>
      </div>
    </div>
  );
}
