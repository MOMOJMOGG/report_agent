export const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
};

export const formatDuration = (seconds: number): string => {
  if (seconds < 60) return `${seconds.toFixed(0)}s`;
  if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
  return `${(seconds / 3600).toFixed(1)}h`;
};

export const formatTimestamp = (timestamp: string): string => {
  return new Date(timestamp).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

export const formatRelativeTime = (timestamp: string): string => {
  const now = new Date().getTime();
  const time = new Date(timestamp).getTime();
  const diff = now - time;
  
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (days > 0) return `${days}d ago`;
  if (hours > 0) return `${hours}h ago`;
  if (minutes > 0) return `${minutes}m ago`;
  return `${seconds}s ago`;
};

export const formatPercentage = (value: number): string => {
  return `${(value * 100).toFixed(1)}%`;
};

export const getStatusColor = (status: string): string => {
  switch (status) {
    case 'running':
      return 'text-primary-400';
    case 'completed':
      return 'text-success-400';
    case 'failed':
      return 'text-accent-400';
    case 'pending':
      return 'text-warning-400';
    default:
      return 'text-dark-400';
  }
};

export const getStatusBgColor = (status: string): string => {
  switch (status) {
    case 'running':
      return 'bg-primary-500/20';
    case 'completed':
      return 'bg-success-500/20';
    case 'failed':
      return 'bg-accent-500/20';
    case 'pending':
      return 'bg-warning-500/20';
    default:
      return 'bg-dark-500/20';
  }
};