import { useState, useEffect, useCallback } from 'react';
import { apiService } from '@/utils/api';
import { AnalysisJob, Report, HealthStatus } from '@/types';

export const useJobs = () => {
  const [jobs, setJobs] = useState<AnalysisJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchJobs = useCallback(async () => {
    try {
      setLoading(true);
      const response = await apiService.listJobs();
      setJobs(response.jobs);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch jobs');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchJobs();
    
    // Auto-refresh every 5 seconds
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, [fetchJobs]);

  return { jobs, loading, error, refresh: fetchJobs };
};

export const useReports = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReports = useCallback(async () => {
    try {
      setLoading(true);
      const response = await apiService.listReports();
      setReports(response.reports);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch reports');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  return { reports, loading, error, refresh: fetchReports };
};

export const useHealth = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = useCallback(async () => {
    try {
      setLoading(true);
      const status = await apiService.health();
      setHealth(status);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Health check failed');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    
    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  return { health, loading, error, refresh: checkHealth };
};

export const useJobStatus = (jobId: string | null) => {
  const [job, setJob] = useState<AnalysisJob | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchJobStatus = useCallback(async () => {
    if (!jobId) return;
    
    try {
      setLoading(true);
      const jobStatus = await apiService.getJobStatus(jobId);
      setJob(jobStatus);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch job status');
    } finally {
      setLoading(false);
    }
  }, [jobId]);

  useEffect(() => {
    if (jobId) {
      fetchJobStatus();
      
      // Auto-refresh while job is running
      const interval = setInterval(() => {
        if (job?.status === 'running' || job?.status === 'pending') {
          fetchJobStatus();
        }
      }, 2000);
      
      return () => clearInterval(interval);
    }
  }, [jobId, fetchJobStatus, job?.status]);

  return { job, loading, error, refresh: fetchJobStatus };
};