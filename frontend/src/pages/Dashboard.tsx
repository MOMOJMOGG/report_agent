import React, { useState, useEffect } from 'react';
import { Plus, TrendingUp, Clock, CheckCircle, AlertTriangle, Brain, Zap, Settings, BarChart } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import StatsCard from '@/components/widgets/StatsCard';
import JobStatusCard from '@/components/widgets/JobStatusCard';
import SystemMonitor from '@/components/widgets/SystemMonitor';
import AgentActivityFeed, { AgentMessage } from '@/components/demo/AgentActivityFeed';
import PipelineVisualizer, { PipelineStage } from '@/components/demo/PipelineVisualizer';
import AgentStatusPanel, { AgentStatus } from '@/components/demo/AgentStatusPanel';
import AnalysisWizard from '@/components/demo/AnalysisWizard';
import SystemSettingsModal from '@/components/demo/SystemSettingsModal';
import { useJobs, useReports } from '@/hooks/useApi';
import { apiService } from '@/utils/api';
import { AnalysisRequest } from '@/types';

const Dashboard: React.FC = () => {
  const { jobs, loading: jobsLoading } = useJobs();
  const { reports } = useReports();
  const navigate = useNavigate();
  const [isStartingJob, setIsStartingJob] = useState(false);
  const [showAnalysisWizard, setShowAnalysisWizard] = useState(false);
  const [showSystemSettings, setShowSystemSettings] = useState(false);
  
  // Demo data states
  const [agentMessages, setAgentMessages] = useState<AgentMessage[]>([]);
  const [pipelineStages, setPipelineStages] = useState<PipelineStage[]>([
    {
      id: 'coordinator',
      name: 'Initialize Pipeline',
      agentType: 'coordinator',
      status: 'pending'
    },
    {
      id: 'data_fetch',
      name: 'Fetch Data',
      agentType: 'data_fetch',
      status: 'pending'
    },
    {
      id: 'normalization',
      name: 'Clean & Normalize',
      agentType: 'normalization',
      status: 'pending'
    },
    {
      id: 'rag',
      name: 'Generate Insights',
      agentType: 'rag',
      status: 'pending'
    },
    {
      id: 'report',
      name: 'Create Reports',
      agentType: 'report',
      status: 'pending'
    },
    {
      id: 'dashboard',
      name: 'Display Results',
      agentType: 'dashboard',
      status: 'pending'
    }
  ]);
  const [currentStage, setCurrentStage] = useState<string>('');
  const [agentStatuses, setAgentStatuses] = useState<AgentStatus[]>([
    {
      agentType: 'coordinator',
      name: 'Coordinator Agent',
      status: 'idle',
      lastActivity: new Date(),
      stats: { totalTasks: 12, completedTasks: 11, failedTasks: 1, averageExecutionTime: 45000 }
    },
    {
      agentType: 'data_fetch',
      name: 'Data Fetch Agent',
      status: 'idle',
      lastActivity: new Date(Date.now() - 300000),
      stats: { totalTasks: 8, completedTasks: 8, failedTasks: 0, averageExecutionTime: 12000 }
    },
    {
      agentType: 'normalization',
      name: 'Normalization Agent',
      status: 'idle',
      lastActivity: new Date(Date.now() - 180000),
      stats: { totalTasks: 8, completedTasks: 7, failedTasks: 1, averageExecutionTime: 8500 }
    },
    {
      agentType: 'rag',
      name: 'RAG Agent',
      status: 'idle',
      lastActivity: new Date(Date.now() - 120000),
      stats: { totalTasks: 6, completedTasks: 5, failedTasks: 1, averageExecutionTime: 32000 }
    },
    {
      agentType: 'report',
      name: 'Report Agent',
      status: 'idle',
      lastActivity: new Date(Date.now() - 90000),
      stats: { totalTasks: 6, completedTasks: 6, failedTasks: 0, averageExecutionTime: 15000 }
    },
    {
      agentType: 'dashboard',
      name: 'Dashboard Agent',
      status: 'active',
      currentTask: 'Serving web interface',
      lastActivity: new Date(),
      stats: { totalTasks: 50, completedTasks: 50, failedTasks: 0, averageExecutionTime: 250 }
    }
  ]);

  const recentJobs = jobs.slice(0, 6);
  const runningJobs = jobs.filter(job => job.status === 'running').length;
  const completedJobs = jobs.filter(job => job.status === 'completed').length;
  const failedJobs = jobs.filter(job => job.status === 'failed').length;
  const successRate = jobs.length > 0 ? completedJobs / jobs.length : 0;

  // Simulate demo pipeline execution
  const simulatePipelineDemo = async () => {
    const stages = ['coordinator', 'data_fetch', 'normalization', 'rag', 'report', 'dashboard'];
    const messages: AgentMessage[] = [];
    let messageId = 1;

    for (let i = 0; i < stages.length; i++) {
      const stage = stages[i];
      setCurrentStage(stage);

      // Update pipeline stage to running
      setPipelineStages(prev => 
        prev.map(s => 
          s.id === stage 
            ? { ...s, status: 'running', startTime: new Date(), progress: 0 }
            : s.status === 'completed' 
            ? s 
            : { ...s, status: s.id === stage ? 'running' : 'pending' }
        )
      );

      // Update agent status
      setAgentStatuses(prev => 
        prev.map(a => 
          a.agentType === stage 
            ? { ...a, status: 'busy', currentTask: getTaskForStage(stage) }
            : a
        )
      );

      // Add start message
      const startMessage: AgentMessage = {
        id: `msg-${messageId++}`,
        timestamp: new Date(),
        agentType: stage,
        message: getStartMessage(stage),
        level: 'info'
      };
      messages.push(startMessage);
      setAgentMessages(prev => [...prev, startMessage]);

      // Simulate progress
      for (let progress = 0; progress <= 1; progress += 0.25) {
        await new Promise(resolve => setTimeout(resolve, 300));
        setPipelineStages(prev => 
          prev.map(s => s.id === stage ? { ...s, progress } : s)
        );
      }

      // Add completion message
      const completeMessage: AgentMessage = {
        id: `msg-${messageId++}`,
        timestamp: new Date(),
        agentType: stage,
        message: getCompleteMessage(stage),
        level: 'success',
        metadata: getMetadataForStage(stage)
      };
      messages.push(completeMessage);
      setAgentMessages(prev => [...prev, completeMessage]);

      // Update to completed
      setPipelineStages(prev => 
        prev.map(s => 
          s.id === stage 
            ? { ...s, status: 'completed', endTime: new Date(), progress: 1 }
            : s
        )
      );

      setAgentStatuses(prev => 
        prev.map(a => 
          a.agentType === stage 
            ? { ...a, status: 'idle', currentTask: undefined }
            : a
        )
      );

      await new Promise(resolve => setTimeout(resolve, 500));
    }

    setCurrentStage('');
    toast.success('Demo pipeline completed successfully!');
  };

  const getTaskForStage = (stage: string) => {
    switch (stage) {
      case 'coordinator': return 'Initializing pipeline workflow...';
      case 'data_fetch': return 'Retrieving retail data from database...';
      case 'normalization': return 'Cleaning and standardizing data...';
      case 'rag': return 'Generating AI insights...';
      case 'report': return 'Creating Excel reports...';
      case 'dashboard': return 'Updating dashboard display...';
      default: return 'Processing...';
    }
  };

  const getStartMessage = (stage: string) => {
    switch (stage) {
      case 'coordinator': return 'Starting new analysis pipeline...';
      case 'data_fetch': return 'Connecting to retail database...';
      case 'normalization': return 'Beginning data cleaning process...';
      case 'rag': return 'Initializing RAG processing engine...';
      case 'report': return 'Preparing Excel report generation...';
      case 'dashboard': return 'Updating real-time dashboard...';
      default: return 'Starting process...';
    }
  };

  const getCompleteMessage = (stage: string) => {
    switch (stage) {
      case 'coordinator': return 'Pipeline orchestration completed';
      case 'data_fetch': return 'Successfully retrieved 1,247 records';
      case 'normalization': return 'Data quality improved to 94.2%';
      case 'rag': return 'Generated 8 high-confidence insights';
      case 'report': return 'Excel report created with 4 worksheets';
      case 'dashboard': return 'Dashboard updated with latest results';
      default: return 'Process completed';
    }
  };

  const getMetadataForStage = (stage: string) => {
    switch (stage) {
      case 'coordinator': return { pipeline_id: 'demo-123', duration_ms: 1200 };
      case 'data_fetch': return { records_found: 1247, tables: ['returns', 'warranties', 'products'] };
      case 'normalization': return { quality_score: 0.942, cleaned_records: 1186, removed_duplicates: 61 };
      case 'rag': return { insights_generated: 8, api_calls: 4, cost_usd: 0.023 };
      case 'report': return { worksheets: 4, file_size_kb: 142, charts_created: 6 };
      case 'dashboard': return { components_updated: 12, response_time_ms: 45 };
      default: return {};
    }
  };

  const handleStartQuickAnalysis = async () => {
    try {
      setIsStartingJob(true);
      
      // Create a real backend job for live demo
      const demoConfig = {
        date_range_start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days ago
        date_range_end: new Date().toISOString().split('T')[0], // today
        tables: ["returns", "warranties", "products"],
        filters: {
          demo_mode: true,
          scenario: "live_demo"
        }
      };
      
      const result = await apiService.startAnalysis(demoConfig);
      toast.success(`Live demo started - Job ID: ${result.job_id.slice(0, 8)}`);
      
      // Start frontend simulation to show the pipeline visualization
      await simulatePipelineDemo();
      
    } catch (error) {
      toast.error('Failed to start live demo analysis');
      console.error('Error starting live demo analysis:', error);
    } finally {
      setIsStartingJob(false);
    }
  };

  const handleAnalysisStart = async (jobId: string) => {
    toast.success(`Analysis started with job ID: ${jobId.slice(0, 8)}`);
    
    // Start the pipeline simulation for wizard-triggered analyses
    try {
      setIsStartingJob(true);
      await simulatePipelineDemo();
    } catch (error) {
      toast.error('Pipeline simulation failed');
      console.error('Error in pipeline simulation:', error);
    } finally {
      setIsStartingJob(false);
    }
  };

  const handleCustomAnalysis = () => {
    setShowAnalysisWizard(true);
  };

  const handleViewReports = () => {
    navigate('/reports');
  };

  const handleSystemSettings = () => {
    setShowSystemSettings(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-dark-800">Multi-Agent RAG Dashboard</h2>
          <p className="text-dark-500 mt-1">Watch AI agents collaborate in real-time</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handleCustomAnalysis}
            className="btn-secondary flex items-center space-x-2"
          >
            <Brain className="w-4 h-4" />
            <span>Analysis Wizard</span>
          </button>
          <button
            onClick={handleStartQuickAnalysis}
            disabled={isStartingJob}
            className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isStartingJob ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                <span>Running Demo...</span>
              </>
            ) : (
              <>
                <Zap className="w-4 h-4" />
                <span>Live Demo</span>
              </>
            )}
          </button>
        </div>
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

      {/* Pipeline Visualizer & Agent Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pipeline Visualizer */}
        <div className="lg:col-span-2">
          <PipelineVisualizer 
            stages={pipelineStages}
            currentStage={currentStage}
            showProgress={true}
            showTimings={true}
          />
        </div>

        {/* Agent Status Panel */}
        <div>
          <AgentStatusPanel 
            agents={agentStatuses}
            compact={false}
            showStats={true}
          />
        </div>
      </div>

      {/* Agent Activity Feed & Recent Jobs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent Activity Feed */}
        <div className="lg:col-span-2">
          <AgentActivityFeed 
            messages={agentMessages}
            maxHeight="500px"
            showTimestamps={true}
            groupByAgent={false}
          />
        </div>

        {/* Recent Jobs & System Monitor */}
        <div className="space-y-6">
          <div className="card-tech">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-dark-800">Recent Jobs</h3>
              <span className="text-sm text-dark-500">{jobs.length} total</span>
            </div>
            
            {jobsLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-500"></div>
              </div>
            ) : recentJobs.length > 0 ? (
              <div className="space-y-2">
                {recentJobs.slice(0, 3).map((job) => (
                  <div key={job.job_id} className="p-2 bg-dark-200/20 rounded text-sm">
                    <div className="flex items-center justify-between">
                      <span className="font-tech text-dark-700">{job.job_id.slice(0, 8)}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        job.status === 'completed' ? 'bg-success-500/20 text-success-400' :
                        job.status === 'running' ? 'bg-warning-500/20 text-warning-400' :
                        job.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                        'bg-dark-500/20 text-dark-400'
                      }`}>
                        {job.status}
                      </span>
                    </div>
                    <p className="text-xs text-dark-500 mt-1 truncate">{job.message}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6">
                <Clock className="w-8 h-8 text-dark-400 mx-auto mb-2" />
                <p className="text-sm text-dark-500">No jobs yet</p>
              </div>
            )}
          </div>

          <SystemMonitor
            activeJobs={runningJobs}
            totalJobs={jobs.length}
            successRate={successRate}
            avgExecutionTime={120}
          />
        </div>
      </div>

      {/* Demo Actions */}
      <div className="card-tech">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-dark-800">Demo Scenarios</h3>
          <span className="text-xs text-dark-500">Click to experience different analysis modes</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button 
            onClick={handleCustomAnalysis}
            className="p-4 bg-primary-500/10 border border-primary-500/20 rounded-lg hover:bg-primary-500/20 transition-colors group"
          >
            <div className="text-center">
              <div className="w-10 h-10 bg-primary-500/20 rounded-lg flex items-center justify-center mx-auto mb-2 group-hover:scale-110 transition-transform">
                <Brain className="w-5 h-5 text-primary-400" />
              </div>
              <h4 className="font-medium text-dark-700">Analysis Wizard</h4>
              <p className="text-sm text-dark-500 mt-1">Guided analysis with demo scenarios</p>
            </div>
          </button>
          
          <button 
            onClick={handleViewReports}
            className="p-4 bg-success-500/10 border border-success-500/20 rounded-lg hover:bg-success-500/20 transition-colors group"
          >
            <div className="text-center">
              <div className="w-10 h-10 bg-success-500/20 rounded-lg flex items-center justify-center mx-auto mb-2 group-hover:scale-110 transition-transform">
                <BarChart className="w-5 h-5 text-success-400" />
              </div>
              <h4 className="font-medium text-dark-700">View Reports</h4>
              <p className="text-sm text-dark-500 mt-1">Browse generated Excel reports</p>
            </div>
          </button>
          
          <button 
            onClick={handleSystemSettings}
            className="p-4 bg-warning-500/10 border border-warning-500/20 rounded-lg hover:bg-warning-500/20 transition-colors group"
          >
            <div className="text-center">
              <div className="w-10 h-10 bg-warning-500/20 rounded-lg flex items-center justify-center mx-auto mb-2 group-hover:scale-110 transition-transform">
                <Settings className="w-5 h-5 text-warning-400" />
              </div>
              <h4 className="font-medium text-dark-700">System Settings</h4>
              <p className="text-sm text-dark-500 mt-1">Configure agent parameters</p>
            </div>
          </button>
        </div>
      </div>

      {/* Analysis Wizard Modal */}
      <AnalysisWizard
        isOpen={showAnalysisWizard}
        onClose={() => setShowAnalysisWizard(false)}
        onAnalysisStart={handleAnalysisStart}
      />

      {/* System Settings Modal */}
      <SystemSettingsModal
        isOpen={showSystemSettings}
        onClose={() => setShowSystemSettings(false)}
      />
    </div>
  );
};

export default Dashboard;