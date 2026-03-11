import { Clock, CheckCircle, XCircle, Loader, ExternalLink } from 'lucide-react';
import { UIJob } from '../data/types';

interface JobStatusPanelProps {
  jobs: UIJob[];
}

const statusIcons = {
  pending: Clock,
  processing: Loader,
  completed: CheckCircle,
  failed: XCircle,
};

const statusColors = {
  pending: 'text-gray-500 bg-gray-100',
  processing: 'text-blue-500 bg-blue-100',
  completed: 'text-green-500 bg-green-100',
  failed: 'text-red-500 bg-red-100',
};

export function JobStatusPanel({ jobs }: JobStatusPanelProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-3">
      {jobs.map((job) => {
        const StatusIcon = statusIcons[job.status];

        return (
          <div
            key={job.job_id}
            className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow duration-200"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-semibold text-gray-800">{job.fileName}</h4>
                  <span className={`px-2 py-1 rounded-full text-xs flex items-center gap-1 ${statusColors[job.status]}`}>
                    <StatusIcon className={`w-3 h-3 ${job.status === 'processing' ? 'animate-spin' : ''}`} />
                    {job.status}
                  </span>
                </div>
                <p className="text-xs text-gray-500">
                  Job ID: {job.job_id} • Created: {formatDate(job.createdAt)}
                </p>
              </div>

              {job.resultLink && (
                <a
                  href={job.resultLink}
                  className="ml-4 text-blue-600 hover:text-blue-700 flex items-center gap-1 text-sm"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <span>View Result</span>
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
            </div>

            {(job.status === 'processing' || job.status === 'completed') && (
              <div className="space-y-1">
                <div className="flex justify-between text-xs text-gray-600">
                  <span>Progress</span>
                  <span>{job.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-blue-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${job.progress}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
