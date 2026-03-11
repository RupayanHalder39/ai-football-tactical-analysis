import { useRef, useState, useEffect } from 'react';
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, Maximize } from 'lucide-react';
import { UIEvent } from '../data/types';

interface VideoPlayerProps {
  videoUrl: string;
  events: UIEvent[];
  showOverlays: boolean;
  onTimeUpdate?: (currentTime: number) => void;
  currentTime?: number;
}

export function VideoPlayer({ videoUrl, events, showOverlays, onTimeUpdate, currentTime }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [duration, setDuration] = useState(0);
  const [localCurrentTime, setLocalCurrentTime] = useState(0);

  useEffect(() => {
    if (currentTime !== undefined && videoRef.current) {
      videoRef.current.currentTime = currentTime;
    }
  }, [currentTime]);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      const time = videoRef.current.currentTime;
      setLocalCurrentTime(time);
      onTimeUpdate?.(time);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    if (videoRef.current) {
      videoRef.current.currentTime = time;
      setLocalCurrentTime(time);
    }
  };

  const skip = (seconds: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = Math.max(0, Math.min(duration, videoRef.current.currentTime + seconds));
    }
  };

  const toggleFullscreen = () => {
    if (videoRef.current) {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        videoRef.current.requestFullscreen();
      }
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const activeEvents = showOverlays
    ? events.filter((event) => Math.abs(event.timestamp - localCurrentTime) < 2)
    : [];

  return (
    <div className="bg-black rounded-lg overflow-hidden shadow-lg">
      <div className="relative aspect-video bg-gray-900">
        <video
          ref={videoRef}
          src={videoUrl}
          className="w-full h-full"
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
        />

        {showOverlays && activeEvents.length > 0 && (
          <div className="absolute top-4 right-4 space-y-2 max-w-xs">
            {activeEvents.map((event) => (
              <div
                key={event.id}
                className={`
                  px-4 py-2 rounded-lg shadow-lg backdrop-blur-sm
                  ${event.team === 'Team_A' ? 'bg-blue-500/90' : 'bg-red-500/90'}
                  text-white text-sm animate-in fade-in slide-in-from-right
                `}
              >
                <div className="font-semibold capitalize">{event.type}</div>
                <div className="text-xs opacity-90">{event.player}</div>
              </div>
            ))}
          </div>
        )}

        {!isPlaying && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/20">
            <button
              onClick={togglePlay}
              className="w-16 h-16 bg-white/90 hover:bg-white rounded-full flex items-center justify-center transition-all hover:scale-110"
            >
              <Play className="w-8 h-8 text-gray-900 ml-1" />
            </button>
          </div>
        )}
      </div>

      <div className="bg-gray-800 px-4 py-3 space-y-2">
        <div className="flex items-center gap-3">
          <span className="text-white text-sm font-mono">{formatTime(localCurrentTime)}</span>
          <input
            type="range"
            min="0"
            max={duration || 0}
            value={localCurrentTime}
            onChange={handleSeek}
            className="flex-1 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:bg-green-500 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:cursor-pointer"
          />
          <span className="text-white text-sm font-mono">{formatTime(duration)}</span>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button onClick={() => skip(-10)} className="p-2 text-white hover:text-green-400 transition-colors" title="Skip back 10s">
              <SkipBack className="w-5 h-5" />
            </button>
            <button onClick={togglePlay} className="p-2 text-white hover:text-green-400 transition-colors">
              {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
            </button>
            <button onClick={() => skip(10)} className="p-2 text-white hover:text-green-400 transition-colors" title="Skip forward 10s">
              <SkipForward className="w-5 h-5" />
            </button>
            <button onClick={toggleMute} className="p-2 text-white hover:text-green-400 transition-colors">
              {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
            </button>
          </div>

          <button onClick={toggleFullscreen} className="p-2 text-white hover:text-green-400 transition-colors">
            <Maximize className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
