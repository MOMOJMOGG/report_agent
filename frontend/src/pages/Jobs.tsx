import React, { useState } from 'react';
import { Plus, Search, Filter, Download, Trash2, Play, Pause, Brain } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { useJobs } from '@/hooks/useApi';
import { formatTimestamp, formatDuration, getStatusColor, getStatusBgColor } from '@/utils/formatters';
import AnalysisWizard from '@/components/demo/AnalysisWizard';

const Jobs: React.FC = () => {
  const { jobs, loading } = useJobs();
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showAnalysisWizard, setShowAnalysisWizard] = useState(false);
  const [processingActions, setProcessingActions] = useState<Set<string>>(new Set());

  const filteredJobs = jobs.filter(job => {
    const matchesSearch = job.job_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.message.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || job.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getExecutionTime = (job: any) => {
    if (job.completed_at) {
      const start = new Date(job.started_at).getTime();
      const end = new Date(job.completed_at).getTime();
      return formatDuration((end - start) / 1000);
    } else if (job.status === 'running') {
      const start = new Date(job.started_at).getTime();
      const now = Date.now();
      return formatDuration((now - start) / 1000);
    }
    return '-';
  };

  const handlePauseJob = async (jobId: string) => {
    if (processingActions.has(jobId)) return;
    
    try {
      setProcessingActions(prev => new Set(prev).add(jobId));
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast.success(`Job ${jobId.slice(0, 8)} paused successfully`);
    } catch (error) {
      toast.error('Failed to pause job');
    } finally {
      setProcessingActions(prev => {
        const newSet = new Set(prev);
        newSet.delete(jobId);
        return newSet;
      });
    }
  };

  const handleDownloadReport = async (jobId: string) => {
    if (processingActions.has(jobId)) return;
    
    try {
      setProcessingActions(prev => new Set(prev).add(jobId));
      
      // Get job results first to find the report filename
      try {
        const response = await fetch(`/api/v1/analysis/${jobId}/results`);
        if (response.ok) {
          const results = await response.json();
          if (results.reports && results.reports.length > 0) {
            const report = results.reports[0];
            const filename = report.file_path.split('/').pop();
            
            // Download the actual report file
            const link = document.createElement('a');
            link.href = `/api/v1/reports/${filename}/download`;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            toast.success(`Report for job ${jobId.slice(0, 8)} downloaded`);
          } else {
            toast.error('No reports found for this job');
          }
        } else {
          // Fallback to generic download if job results not found
          const link = document.createElement('a');
          link.href = `/api/v1/reports/retail_analysis_${jobId.slice(0, 8)}.xlsx/download`;
          link.download = `retail_analysis_${jobId.slice(0, 8)}.xlsx`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          
          toast.success(`Report download initiated for job ${jobId.slice(0, 8)}`);
        }
      } catch (fetchError) {
        // Fallback download attempt
        const link = document.createElement('a');
        link.href = `/api/v1/reports/retail_analysis_${jobId.slice(0, 8)}.xlsx/download`;
        link.download = `retail_analysis_${jobId.slice(0, 8)}.xlsx`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        toast.success(`Report download initiated for job ${jobId.slice(0, 8)}`);
      }
    } catch (error) {
      toast.error('Failed to download report');
    } finally {
      setProcessingActions(prev => {
        const newSet = new Set(prev);
        newSet.delete(jobId);
        return newSet;
      });
    }
  };

  const handleDeleteJob = async (jobId: string) => {
    if (processingActions.has(jobId)) return;
    
    const confirmed = window.confirm(`Are you sure you want to delete job ${jobId.slice(0, 8)}?`);
    if (!confirmed) return;
    
    try {
      setProcessingActions(prev => new Set(prev).add(jobId));
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast.success(`Job ${jobId.slice(0, 8)} deleted successfully`);
    } catch (error) {
      toast.error('Failed to delete job');
    } finally {
      setProcessingActions(prev => {
        const newSet = new Set(prev);
        newSet.delete(jobId);
        return newSet;
      });
    }
  };

  const handleNewAnalysis = () => {
    setShowAnalysisWizard(true);
  };

  const handleAnalysisStart = (jobId: string) => {
    toast.success(`New analysis started: ${jobId.slice(0, 8)}`);
    setShowAnalysisWizard(false);
  };

  const handleViewJobDetails = (jobId: string) => {
    navigate(`/analytics?job=${jobId}`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-dark-800">Job Management</h2>
          <p className="text-dark-500 mt-1">Monitor and manage your analysis jobs</p>
        </div>
        <button 
          onClick={handleNewAnalysis}
          className="btn-primary flex items-center space-x-2"
        >
          <Brain className="w-4 h-4" />
          <span>New Analysis</span>
        </button>
      </div>

      {/* Filters */}
      <div className="card-tech">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-dark-400" />
              <input
                type="text"
                placeholder="Search jobs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-dark-200/30 border border-dark-300/30 rounded-lg text-dark-700 placeholder-dark-400 focus:outline-none focus:border-primary-500/50"
              />
            </div>
          </div>

          {/* Status Filter */}
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-dark-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-dark-200/30 border border-dark-300/30 rounded-lg px-3 py-2 text-dark-700 focus:outline-none focus:border-primary-500/50"
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>
        </div>
      </div>

      {/* Jobs Table */}
      <div className="card-tech overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-dark-200/30">
                  <th className="text-left py-3 px-4 font-medium text-dark-600">Job ID</th>
                  <th className="text-left py-3 px-4 font-medium text-dark-600">Status</th>
                  <th className="text-left py-3 px-4 font-medium text-dark-600">Progress</th>
                  <th className="text-left py-3 px-4 font-medium text-dark-600">Started</th>
                  <th className="text-left py-3 px-4 font-medium text-dark-600">Duration</th>
                  <th className="text-left py-3 px-4 font-medium text-dark-600">Message</th>
                  <th className="text-left py-3 px-4 font-medium text-dark-600">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredJobs.map((job) => (
                  <tr key={job.job_id} className="border-b border-dark-200/20 hover:bg-dark-200/20 transition-colors">
                    <td className="py-3 px-4">
                      <span className="font-tech text-sm text-dark-700">{job.job_id.slice(0, 8)}</span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusBgColor(job.status)} ${getStatusColor(job.status)}`}>
                        {job.status}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-dark-300/30 rounded-full h-2">
                          <div 
                            className="bg-gradient-to-r from-primary-500 to-primary-400 h-2 rounded-full transition-all duration-500"
                            style={{ width: `${job.progress * 100}%` }}
                          />
                        </div>
                        <span className="text-xs text-dark-500">{Math.round(job.progress * 100)}%</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-sm text-dark-600">
                      {formatTimestamp(job.started_at)}
                    </td>
                    <td className="py-3 px-4 text-sm text-dark-600 font-tech">
                      {getExecutionTime(job)}
                    </td>
                    <td className="py-3 px-4 text-sm text-dark-600 max-w-xs truncate">
                      {job.message}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-1">
                        {job.status === 'running' && (
                          <button 
                            onClick={() => handlePauseJob(job.job_id)}
                            disabled={processingActions.has(job.job_id)}
                            className="p-1 text-warning-400 hover:bg-warning-500/20 rounded disabled:opacity-50 transition-colors"
                            title="Pause job"
                          >
                            <Pause className="w-4 h-4" />
                          </button>
                        )}
                        {job.status === 'completed' && (
                          <button 
                            onClick={() => handleDownloadReport(job.job_id)}
                            disabled={processingActions.has(job.job_id)}
                            className="p-1 text-primary-400 hover:bg-primary-500/20 rounded disabled:opacity-50 transition-colors"
                            title="Download report"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                        )}
                        {['failed', 'completed'].includes(job.status) && (
                          <button 
                            onClick={() => handleDeleteJob(job.job_id)}
                            disabled={processingActions.has(job.job_id)}
                            className="p-1 text-accent-400 hover:bg-accent-500/20 rounded disabled:opacity-50 transition-colors"
                            title="Delete job"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                        <button 
                          onClick={() => handleViewJobDetails(job.job_id)}
                          className="p-1 text-dark-400 hover:bg-dark-500/20 rounded transition-colors"
                          title="View details"
                        >
                          <Play className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {filteredJobs.length === 0 && (
              <div className="text-center py-8">
                <p className="text-dark-500">No jobs found</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Analysis Wizard Modal */}
      <AnalysisWizard
        isOpen={showAnalysisWizard}
        onClose={() => setShowAnalysisWizard(false)}
        onAnalysisStart={handleAnalysisStart}
      />
    </div>
  );
};

export default Jobs;