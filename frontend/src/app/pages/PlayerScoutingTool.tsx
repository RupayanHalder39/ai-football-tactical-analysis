import { useEffect, useMemo, useState } from 'react';
import { Card } from '../components/Card';
import { VideoUpload } from '../components/VideoUpload';
import { VideoPlayer } from '../components/VideoPlayer';
import { VideoAnalysisSidebar } from '../components/VideoAnalysisSidebar';
import { JobStatusPanel } from '../components/JobStatusPanel';
import { PlayerHeatmap } from '../components/PlayerHeatmap';
import { Eye, EyeOff, BarChart2 } from 'lucide-react';
import { createJob, getJobResult, getJobStatus } from '../data/api';
import { adaptEvents, adaptPossessionSegments, adaptPossessionSummary, buildPlayerAnalytics } from '../data/adapters';
import { UIEvent, UIPossessionSegment, UIPossessionSummary, UIPlayerAnalytics, UIJob } from '../data/types';

export function PlayerScoutingTool() {
  const [jobs, setJobs] = useState<UIJob[]>([]);
  const [selectedJob, setSelectedJob] = useState<UIJob | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [showOverlays, setShowOverlays] = useState(true);
  const [showStats, setShowStats] = useState(true);

  const [events, setEvents] = useState<UIEvent[]>([]);
  const [possessionSummary, setPossessionSummary] = useState<UIPossessionSummary[]>([]);
  const [possessionSegments, setPossessionSegments] = useState<UIPossessionSegment[]>([]);
  const [playerAnalytics, setPlayerAnalytics] = useState<UIPlayerAnalytics[]>([]);

  const [videoUrl, setVideoUrl] = useState<string>('');

  const handleUpload = async (file: File) => {
    const objectUrl = URL.createObjectURL(file);
    setVideoUrl(objectUrl);

    const jobResponse = await createJob(file);
    const newJob: UIJob = {
      job_id: jobResponse.job_id,
      status: 'processing',
      fileName: file.name,
      createdAt: new Date().toISOString(),
      progress: 0,
    };

    setJobs((prev) => [newJob, ...prev]);
    setSelectedJob(newJob);
  };

  useEffect(() => {
    if (!selectedJob) return;

    const interval = setInterval(async () => {
      const status = await getJobStatus(selectedJob.job_id);
      setJobs((current) =>
        current.map((job) =>
          job.job_id === status.job_id
            ? { ...job, status: status.status, progress: status.status === 'completed' ? 100 : 50 }
            : job
        )
      );

      if (status.status === 'completed') {
        const result = await getJobResult(selectedJob.job_id, selectedJob.job_id);
        if (result.frames) {
          setPlayerAnalytics(buildPlayerAnalytics(result.frames));
        }
        if (result.events) {
          setEvents(adaptEvents(result.events));
        } else {
          setEvents([]);
        }
        if (result.possession_summary) {
          setPossessionSummary(adaptPossessionSummary(result.possession_summary));
        } else {
          setPossessionSummary([]);
        }
        if (result.possession_segments) {
          setPossessionSegments(adaptPossessionSegments(result.possession_segments));
        } else {
          setPossessionSegments([]);
        }
        localStorage.setItem('lastJobId', selectedJob.job_id);
        clearInterval(interval);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [selectedJob]);


  const handleEventClick = (timestamp: number) => {
    setCurrentTime(timestamp);
  };

  const hasCompletedJob = selectedJob?.status === 'completed';

  const overlayEvents = useMemo(() => events, [events]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl text-gray-800 mb-2">Player Scouting Tool</h1>
        <p className="text-gray-600">Upload match videos and analyze player performance</p>
      </div>

      {!hasCompletedJob && (
        <Card title="Video Upload & Analysis">
          <VideoUpload onUpload={handleUpload} />
        </Card>
      )}

      {jobs.length > 0 && (
        <Card title="Analysis Jobs">
          <JobStatusPanel jobs={jobs} />
        </Card>
      )}

      {hasCompletedJob && (
        <>
          <div className="flex gap-3 justify-end">
            <button
              onClick={() => setShowOverlays(!showOverlays)}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-lg transition-colors
                ${showOverlays ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700'}
              `}
            >
              {showOverlays ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
              <span>Event Overlays</span>
            </button>

            <button
              onClick={() => setShowStats(!showStats)}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-lg transition-colors
                ${showStats ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700'}
              `}
            >
              <BarChart2 className="w-4 h-4" />
              <span>Analytics Panel</span>
            </button>
          </div>

          <div className={`grid gap-6 ${showStats ? 'grid-cols-1 lg:grid-cols-3' : 'grid-cols-1'}`}>
            <div className={showStats ? 'lg:col-span-2' : 'lg:col-span-1 max-w-4xl mx-auto'}>
              <Card title={`Analysis: ${selectedJob?.fileName ?? 'Match'}`}>
                <VideoPlayer
                  videoUrl={videoUrl}
                  events={overlayEvents}
                  showOverlays={showOverlays}
                  onTimeUpdate={setCurrentTime}
                  currentTime={currentTime}
                />

                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <strong>Tip:</strong> Click on events in the timeline to jump to that moment in the video.
                    Event overlays appear automatically when events occur.
                  </p>
                </div>
              </Card>
            </div>

            {showStats && (
              <div className="lg:col-span-1">
                <Card title="Analytics">
                  <VideoAnalysisSidebar
                    events={events}
                    currentTime={currentTime}
                    onEventClick={handleEventClick}
                    possessionData={possessionSummary}
                    showStats={showStats}
                  />
                </Card>
              </div>
            )}
          </div>

          <div className="flex justify-center">
            <button
              onClick={() => {
                setSelectedJob(null);
                setCurrentTime(0);
              }}
              className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Upload New Video
            </button>
          </div>

          {playerAnalytics.length > 0 && (
            <Card title="Player Heatmap (Derived from Job Results)">
              <div className="text-sm text-gray-500 mb-3">
                Player positions are derived from job result frames and mapped to pitch coordinates when available.
              </div>
              <PlayerHeatmap players={playerAnalytics} />
            </Card>
          )}
        </>
      )}
    </div>
  );
}
