import React, { useState } from 'react';
import { Plus, TrendingUp, Clock, CheckCircle, AlertTriangle } from 'lucide-react';
import { toast } from 'react-hot-toast';
import StatsCard from '@/components/widgets/StatsCard';
import JobStatusCard from '@/components/widgets/JobStatusCard';
import SystemMonitor from '@/components/widgets/SystemMonitor';
import { useJobs, useReports } from '@/hooks/useApi';
import { apiService } from '@/utils/api';
import { AnalysisRequest } from '@/types';

const Dashboard: React.FC = () => {
  const { jobs, loading: jobsLoading } = useJobs();
  const { reports } = useReports();
  const [isStartingJob, setIsStartingJob] = useState(false);

  const recentJobs = jobs.slice(0, 6);
  const runningJobs = jobs.filter(job => job.status === 'running').length;
  const completedJobs = jobs.filter(job => job.status === 'completed').length;
  const failedJobs = jobs.filter(job => job.status === 'failed').length;
  const successRate = jobs.length > 0 ? completedJobs / jobs.length : 0;

  const handleStartQuickAnalysis = async () => {
    try {
      setIsStartingJob(true);
      
      const request: AnalysisRequest = {
        date_range_start: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        date_range_end: new Date().toISOString().split('T')[0],
        tables: ['returns', 'warranties', 'products'],
        filters: { store_locations: ['all'], product_categories: ['all'] }
      };

      const result = await apiService.startAnalysis(request);
      toast.success(`Analysis job started: ${result.job_id.slice(0, 8)}`);
    } catch (error) {
      toast.error('Failed to start analysis');
      console.error('Error starting analysis:', error);
    } finally {
      setIsStartingJob(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-dark-800">Welcome to Multi-Agent Dashboard</h2>
          <p className="text-dark-500 mt-1">Monitor your retail analysis pipeline in real-time</p>
        </div>
        <button
          onClick={handleStartQuickAnalysis}
          disabled={isStartingJob}
          className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Plus className="w-4 h-4" />
          <span>{isStartingJob ? 'Starting...' : 'Quick Analysis'}</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Running Jobs"
          value={runningJobs}
          change={runningJobs > 0 ? `${runningJobs} active` : 'No active jobs'}
          changeType="neutral"
          icon={Clock}
          color="primary"
        />
        <StatsCard
          title="Completed"
          value={completedJobs}
          change={`${Math.round(successRate * 100)}% success rate`}
          changeType="increase"
          icon={CheckCircle}
          color="success"
        />
        <StatsCard
          title="Failed Jobs"
          value={failedJobs}
          change={failedJobs > 0 ? `${failedJobs} need attention` : 'All good'}
          changeType={failedJobs > 0 ? "decrease" : "neutral"}
          icon={AlertTriangle}
          color="accent"
        />
        <StatsCard
          title="Reports"
          value={reports.length}
          change="+2 this week"
          changeType="increase"
          icon={TrendingUp}
          color="warning"
        />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Jobs */}
        <div className="lg:col-span-2">
          <div className="card-tech">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-dark-800">Recent Jobs</h3>
              <span className="text-sm text-dark-500">{jobs.length} total</span>
            </div>
            
            {jobsLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
              </div>
            ) : recentJobs.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {recentJobs.map((job) => (
                  <JobStatusCard
                    key={job.job_id}
                    job={job}
                    onClick={() => console.log('View job details:', job.job_id)}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Clock className="w-12 h-12 text-dark-400 mx-auto mb-3" />
                <p className="text-dark-500">No jobs yet. Start your first analysis!</p>
              </div>
            )}
          </div>
        </div>

        {/* System Monitor */}
        <div>
          <SystemMonitor
            activeJobs={runningJobs}
            totalJobs={jobs.length}
            successRate={successRate}
            avgExecutionTime={120} // This would come from actual metrics
          />
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card-tech">
        <h3 className="text-lg font-semibold text-dark-800 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 bg-primary-500/10 border border-primary-500/20 rounded-lg hover:bg-primary-500/20 transition-colors group">
            <div className="text-center">
              <div className="w-10 h-10 bg-primary-500/20 rounded-lg flex items-center justify-center mx-auto mb-2 group-hover:scale-110 transition-transform">
                <TrendingUp className="w-5 h-5 text-primary-400" />
              </div>
              <h4 className="font-medium text-dark-700">Custom Analysis</h4>
              <p className="text-sm text-dark-500 mt-1">Set custom date ranges and filters</p>
            </div>
          </button>
          
          <button className="p-4 bg-success-500/10 border border-success-500/20 rounded-lg hover:bg-success-500/20 transition-colors group">
            <div className="text-center">
              <div className="w-10 h-10 bg-success-500/20 rounded-lg flex items-center justify-center mx-auto mb-2 group-hover:scale-110 transition-transform">
                <CheckCircle className="w-5 h-5 text-success-400" />
              </div>
              <h4 className="font-medium text-dark-700">View Reports</h4>
              <p className="text-sm text-dark-500 mt-1">Download and view generated reports</p>
            </div>
          </button>
          
          <button className="p-4 bg-warning-500/10 border border-warning-500/20 rounded-lg hover:bg-warning-500/20 transition-colors group">
            <div className="text-center">
              <div className="w-10 h-10 bg-warning-500/20 rounded-lg flex items-center justify-center mx-auto mb-2 group-hover:scale-110 transition-transform">
                <AlertTriangle className="w-5 h-5 text-warning-400" />
              </div>
              <h4 className="font-medium text-dark-700">System Settings</h4>
              <p className="text-sm text-dark-500 mt-1">Configure agents and parameters</p>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;