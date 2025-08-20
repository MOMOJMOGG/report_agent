import React from 'react';
import { Activity, Cpu, Database, Zap, Users } from 'lucide-react';

interface SystemMonitorProps {
  activeJobs: number;
  totalJobs: number;
  successRate: number;
  avgExecutionTime: number;
}

const SystemMonitor: React.FC<SystemMonitorProps> = ({
  activeJobs,
  totalJobs,
  successRate,
  avgExecutionTime
}) => {
  const agents = [
    { name: 'Data Fetch', status: 'online', load: 65 },
    { name: 'Normalization', status: 'online', load: 42 },
    { name: 'RAG', status: 'online', load: 78 },
    { name: 'Report', status: 'online', load: 23 },
    { name: 'Dashboard', status: 'online', load: 15 }
  ];

  return (
    <div className="card-tech">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-dark-800">System Monitor</h3>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-success-400 font-medium">All Systems Operational</span>
        </div>
      </div>

      {/* System Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="text-center p-3 bg-dark-200/30 rounded-lg">
          <div className="flex items-center justify-center w-8 h-8 bg-primary-500/20 rounded-lg mx-auto mb-2">
            <Activity className="w-4 h-4 text-primary-400" />
          </div>
          <p className="text-xl font-bold text-dark-800">{activeJobs}</p>
          <p className="text-xs text-dark-500">Active Jobs</p>
        </div>

        <div className="text-center p-3 bg-dark-200/30 rounded-lg">
          <div className="flex items-center justify-center w-8 h-8 bg-success-500/20 rounded-lg mx-auto mb-2">
            <Cpu className="w-4 h-4 text-success-400" />
          </div>
          <p className="text-xl font-bold text-dark-800">{Math.round(successRate * 100)}%</p>
          <p className="text-xs text-dark-500">Success Rate</p>
        </div>

        <div className="text-center p-3 bg-dark-200/30 rounded-lg">
          <div className="flex items-center justify-center w-8 h-8 bg-warning-500/20 rounded-lg mx-auto mb-2">
            <Database className="w-4 h-4 text-warning-400" />
          </div>
          <p className="text-xl font-bold text-dark-800">{totalJobs}</p>
          <p className="text-xs text-dark-500">Total Jobs</p>
        </div>

        <div className="text-center p-3 bg-dark-200/30 rounded-lg">
          <div className="flex items-center justify-center w-8 h-8 bg-accent-500/20 rounded-lg mx-auto mb-2">
            <Zap className="w-4 h-4 text-accent-400" />
          </div>
          <p className="text-xl font-bold text-dark-800">{Math.round(avgExecutionTime)}s</p>
          <p className="text-xs text-dark-500">Avg Time</p>
        </div>
      </div>

      {/* Agent Status */}
      <div>
        <h4 className="text-sm font-medium text-dark-700 mb-3 flex items-center">
          <Users className="w-4 h-4 mr-2" />
          Agent Status
        </h4>
        <div className="space-y-2">
          {agents.map((agent) => (
            <div key={agent.name} className="flex items-center justify-between p-2 bg-dark-200/20 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-dark-700">{agent.name}</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-16 bg-dark-300/30 rounded-full h-1.5">
                  <div 
                    className="bg-gradient-to-r from-primary-500 to-primary-400 h-1.5 rounded-full transition-all duration-500"
                    style={{ width: `${agent.load}%` }}
                  />
                </div>
                <span className="text-xs text-dark-500 w-8 text-right">{agent.load}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SystemMonitor;