import axios from 'axios';
import { AnalysisRequest, AnalysisJob, Report, HealthStatus } from '@/types';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('Response Error:', error);
    if (error.response) {
      console.error('Error Data:', error.response.data);
      console.error('Error Status:', error.response.status);
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  // Health check
  health: async (): Promise<HealthStatus> => {
    const response = await api.get('/health');
    return response.data;
  },

  // Analysis operations
  startAnalysis: async (request: AnalysisRequest): Promise<{ job_id: string; status: string }> => {
    const response = await api.post('/analysis/start', request);
    return response.data;
  },

  getJobStatus: async (jobId: string): Promise<AnalysisJob> => {
    const response = await api.get(`/analysis/${jobId}/status`);
    return response.data;
  },

  listJobs: async (): Promise<{ jobs: AnalysisJob[] }> => {
    const response = await api.get('/analysis/jobs');
    return response.data;
  },

  cancelJob: async (jobId: string): Promise<{ success: boolean }> => {
    const response = await api.delete(`/analysis/${jobId}/cancel`);
    return response.data;
  },

  // Reports
  listReports: async (): Promise<{ reports: Report[] }> => {
    const response = await api.get('/reports');
    return response.data;
  },

  downloadReport: async (filename: string): Promise<Blob> => {
    const response = await api.get(`/reports/${filename}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // File upload
  uploadFile: async (file: File): Promise<{ filename: string; size: number; saved_path: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/data/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // System info
  getSystemInfo: async (): Promise<any> => {
    const response = await api.get('/');
    return response.data;
  },
};

export default api;