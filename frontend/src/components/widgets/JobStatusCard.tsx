import React from 'react';
import { Clock, CheckCircle, XCircle, AlertCircle, Play } from 'lucide-react';
import { AnalysisJob } from '@/types';
import { formatRelativeTime, getStatusColor, getStatusBgColor } from '@/utils/formatters';

interface JobStatusCardProps {
  job: AnalysisJob;
  onClick?: () => void;
}

const JobStatusCard: React.FC<JobStatusCardProps> = ({ job, onClick }) => {
  const getStatusIcon = () => {
    switch (job.status) {
      case 'running':
        return <Play className="w-4 h-4" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4" />;
      case 'failed':
        return <XCircle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const getStatusText = () => {
    switch (job.status) {
      case 'running':
        return 'Running';
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      case 'pending':
        return 'Pending';
      default:
        return 'Unknown';
    }
  };

  return (
    <div 
      className="card-tech cursor-pointer hover:border-primary-500/50"
      onClick={onClick}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className={`p-1.5 rounded-lg ${getStatusBgColor(job.status)}`}>
            <div className={getStatusColor(job.status)}>
              {getStatusIcon()}
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-dark-700">Job {job.job_id.slice(0, 8)}</p>
            <p className="text-xs text-dark-500">{formatRelativeTime(job.started_at)}</p>
          </div>
        </div>
        <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBgColor(job.status)} ${getStatusColor(job.status)}`}>
          {getStatusText()}
        </div>
      </div>

      {/* Progress bar for running jobs */}
      {job.status === 'running' && (
        <div className="mb-3">
          <div className="flex justify-between text-xs text-dark-500 mb-1">
            <span>Progress</span>
            <span>{Math.round(job.progress * 100)}%</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${job.progress * 100}%` }}
            />
          </div>
        </div>
      )}

      <p className="text-sm text-dark-600 line-clamp-2">{job.message}</p>

      {job.error_message && (
        <div className="mt-2 p-2 bg-accent-500/10 border border-accent-500/20 rounded-lg">
          <p className="text-xs text-accent-400">{job.error_message}</p>
        </div>
      )}
    </div>
  );
};

export default JobStatusCard;