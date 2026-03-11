import { useState } from 'react';
import { Clock, Target, Circle, Shield, Award } from 'lucide-react';
import { UIEvent } from '../data/types';

interface EventTimelinePanelProps {
  events: UIEvent[];
  onEventClick?: (event: UIEvent) => void;
}

const eventIcons: Record<string, any> = {
  pass: Circle,
  dribble: Target,
  shot: Target,
  tackle: Shield,
  interception: Shield,
  goal: Award,
};

export function EventTimelinePanel({ events, onEventClick }: EventTimelinePanelProps) {
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);

  const handleEventClick = (event: UIEvent) => {
    setSelectedEventId(event.id);
    onEventClick?.(event);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
      {events.map((event, index) => {
        const Icon = eventIcons[event.type] || Circle;
        const isSelected = event.id === selectedEventId;

        return (
          <div
            key={event.id}
            onClick={() => handleEventClick(event)}
            className={`
              relative pl-8 pb-4 cursor-pointer transition-all duration-200
              ${index !== events.length - 1 ? 'border-l-2 border-gray-200' : ''}
              ${isSelected ? 'transform scale-[1.02]' : ''}
            `}
          >
            <div className={`
              absolute left-0 top-0 -translate-x-1/2
              w-8 h-8 rounded-full flex items-center justify-center
              ${event.team === 'Team_A' ? 'bg-blue-500' : 'bg-red-500'}
              ${isSelected ? 'ring-4 ring-offset-2 ring-gray-300' : ''}
            `}>
              <Icon className="w-4 h-4 text-white" />
            </div>

            <div className={`
              ml-4 bg-white rounded-lg p-4 shadow-sm border-l-4
              ${event.team === 'Team_A' ? 'border-blue-500' : 'border-red-500'}
              ${isSelected ? 'shadow-lg' : 'hover:shadow-md'}
            `}>
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-gray-400" />
                  <span className="font-mono text-sm">{formatTime(event.timestamp)}</span>
                </div>
                <span className={`
                  px-2 py-1 rounded-full text-xs
                  ${event.outcome === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}
                `}>
                  {event.outcome}
                </span>
              </div>

              <div className="space-y-1">
                <p className="font-semibold text-gray-800 capitalize">
                  {event.type}
                </p>
                <p className="text-sm text-gray-600">
                  {event.player} ({event.team})
                </p>
                <p className="text-xs text-gray-400">
                  Position: ({event.x.toFixed(1)}, {event.y.toFixed(1)})
                </p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
