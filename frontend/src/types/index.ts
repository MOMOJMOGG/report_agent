export interface AnalysisJob {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  message: string;
  started_at: string;
  completed_at?: string;
  error_message?: string;
}

export interface AnalysisRequest {
  date_range_start: string;
  date_range_end: string;
  tables?: string[];
  filters?: Record<string, any>;
}

export interface Report {
  file_path: string;
  report_type: string;
  created_at: string;
  size_bytes: number;
  worksheets?: string[];
}

export interface HealthStatus {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  active_jobs: number;
  completed_jobs: number;
  system_info?: Record<string, any>;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

export interface DashboardStats {
  total_jobs: number;
  successful_jobs: number;
  failed_jobs: number;
  success_rate: number;
  avg_execution_time: number;
  active_agents: number;
}

export interface AgentStatus {
  agent_type: string;
  status: 'online' | 'offline' | 'busy';
  last_seen: string;
  processed_jobs: number;
  error_count: number;
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}