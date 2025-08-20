import React, { useState } from 'react';
import { 
  Bot, Database, Sparkles, Brain, FileText, Monitor,
  Activity, CheckCircle, XCircle, Clock, AlertCircle,
  ChevronDown, ChevronUp, Info, Zap
} from 'lucide-react';

export interface AgentStatus {
  agentType: string;
  name: string;
  status: 'idle' | 'active' | 'busy' | 'error' | 'offline';
  currentTask?: string;
  progress?: number;
  lastActivity?: Date;
  stats?: {
    totalTasks: number;
    completedTasks: number;
    failedTasks: number;
    averageExecutionTime: number;
  };
  metadata?: Record<string, any>;
}

interface AgentStatusPanelProps {
  agents: AgentStatus[];
  className?: string;
  compact?: boolean;
  showStats?: boolean;
}

const AgentStatusPanel: React.FC<AgentStatusPanelProps> = ({
  agents,
  className = '',
  compact = false,
  showStats = true
}) => {
  const [expandedAgents, setExpandedAgents] = useState<Set<string>>(new Set());

  const getAgentIcon = (agentType: string) => {
    switch (agentType.toLowerCase()) {
      case 'coordinator':
        return Bot;
      case 'data_fetch':
        return Database;
      case 'normalization':
        return Sparkles;
      case 'rag':
        return Brain;
      case 'report':
        return FileText;
      case 'dashboard':
        return Monitor;
      default:
        return Bot;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
      case 'busy':
        return Activity;
      case 'idle':
        return CheckCircle;
      case 'error':
        return XCircle;
      case 'offline':
        return AlertCircle;
      default:
        return Clock;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-primary-400 bg-primary-500/10 border-primary-500/20';
      case 'busy':
        return 'text-warning-400 bg-warning-500/10 border-warning-500/20';
      case 'idle':
        return 'text-success-400 bg-success-500/10 border-success-500/20';
      case 'error':
        return 'text-red-400 bg-red-500/10 border-red-500/20';
      case 'offline':
        return 'text-dark-400 bg-dark-500/10 border-dark-500/20';
      default:
        return 'text-dark-400 bg-dark-500/10 border-dark-500/20';
    }
  };

  const getAgentDescription = (agentType: string) => {
    switch (agentType.toLowerCase()) {
      case 'coordinator':
        return 'Orchestrates the complete multi-agent pipeline workflow';
      case 'data_fetch':
        return 'Retrieves retail data from database systems';
      case 'normalization':
        return 'Cleans and standardizes data for analysis';
      case 'rag':
        return 'Generates AI-powered insights using vector search';
      case 'report':
        return 'Creates professional Excel reports and summaries';
      case 'dashboard':
        return 'Serves web interface and manages user interactions';
      default:
        return 'Multi-agent system component';
    }
  };

  const formatLastActivity = (date?: Date) => {
    if (!date) return 'Never';
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (seconds < 60) return `${seconds}s ago`;
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return date.toLocaleDateString();
  };

  const formatExecutionTime = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  const toggleAgentExpansion = (agentType: string) => {
    const newExpanded = new Set(expandedAgents);
    if (newExpanded.has(agentType)) {
      newExpanded.delete(agentType);
    } else {
      newExpanded.add(agentType);
    }
    setExpandedAgents(newExpanded);
  };

  const getOverallSystemHealth = () => {
    const totalAgents = agents.length;
    const activeAgents = agents.filter(a => ['active', 'busy', 'idle'].includes(a.status)).length;
    const errorAgents = agents.filter(a => a.status === 'error').length;
    
    if (errorAgents > 0) return { status: 'warning', message: `${errorAgents} agents with errors` };
    if (activeAgents === totalAgents) return { status: 'healthy', message: 'All agents operational' };
    if (activeAgents > totalAgents * 0.7) return { status: 'good', message: 'Most agents operational' };
    return { status: 'degraded', message: 'Some agents offline' };
  };

  if (compact) {
    return (
      <div className={`card-tech ${className}`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-dark-800">System Status</h3>
          <div className="flex items-center space-x-1">
            {agents.map((agent) => {
              const Icon = getAgentIcon(agent.agentType);
              return (
                <div
                  key={agent.agentType}
                  className={`w-6 h-6 rounded border flex items-center justify-center ${getStatusColor(agent.status)}`}
                  title={`${agent.name}: ${agent.status}`}
                >
                  <Icon className="w-3 h-3" />
                </div>
              );
            })}
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-3 text-center text-xs">
          <div>
            <p className="text-dark-500">Active</p>
            <p className="font-medium text-primary-400">
              {agents.filter(a => ['active', 'busy'].includes(a.status)).length}
            </p>
          </div>
          <div>
            <p className="text-dark-500">Total</p>
            <p className="font-medium text-dark-700">{agents.length}</p>
          </div>
        </div>
      </div>
    );
  }

  const systemHealth = getOverallSystemHealth();

  return (
    <div className={`card-tech ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <Activity className="w-5 h-5 text-primary-400" />
          <h3 className="text-lg font-semibold text-dark-800">Agent Status</h3>
        </div>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${
            systemHealth.status === 'healthy' ? 'bg-success-400' :
            systemHealth.status === 'good' ? 'bg-primary-400' :
            systemHealth.status === 'warning' ? 'bg-warning-400' : 'bg-red-400'
          }`} />
          <span className="text-xs text-dark-500">{systemHealth.message}</span>
        </div>
      </div>

      <div className="space-y-3">
        {agents.map((agent) => {
          const Icon = getAgentIcon(agent.agentType);
          const StatusIcon = getStatusIcon(agent.status);
          const isExpanded = expandedAgents.has(agent.agentType);

          return (
            <div key={agent.agentType} className={`rounded-lg border transition-all duration-200 ${getStatusColor(agent.status)}`}>
              <div className="p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="relative">
                      <div className={`w-8 h-8 rounded-lg border flex items-center justify-center ${getStatusColor(agent.status)}`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border border-dark-100 flex items-center justify-center ${getStatusColor(agent.status)}`}>
                        <StatusIcon className="w-2 h-2" />
                      </div>
                      {agent.status === 'active' && (
                        <div className="absolute inset-0 rounded-lg border animate-pulse border-primary-400" />
                      )}
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h4 className="font-medium text-dark-700">{agent.name}</h4>
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(agent.status)}`}>
                          {agent.status}
                        </span>
                      </div>
                      {agent.currentTask && (
                        <p className="text-sm text-dark-600 mt-1">{agent.currentTask}</p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-dark-500 font-tech">
                      {formatLastActivity(agent.lastActivity)}
                    </span>
                    {(agent.stats || agent.metadata) && (
                      <button
                        onClick={() => toggleAgentExpansion(agent.agentType)}
                        className="p-1 text-dark-400 hover:text-primary-400 transition-colors"
                      >
                        {isExpanded ? 
                          <ChevronUp className="w-4 h-4" /> : 
                          <ChevronDown className="w-4 h-4" />
                        }
                      </button>
                    )}
                  </div>
                </div>

                {agent.progress !== undefined && agent.status !== 'idle' && (
                  <div className="mt-3">
                    <div className="flex items-center justify-between text-xs text-dark-500 mb-1">
                      <span>Progress</span>
                      <span>{Math.round(agent.progress * 100)}%</span>
                    </div>
                    <div className="w-full bg-dark-300/30 rounded-full h-1.5">
                      <div 
                        className="bg-gradient-to-r from-primary-500 to-primary-400 h-1.5 rounded-full transition-all duration-500"
                        style={{ width: `${agent.progress * 100}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>

              {isExpanded && (
                <div className="border-t border-current border-opacity-20 p-3">
                  <div className="space-y-3">
                    <div>
                      <h5 className="text-sm font-medium text-dark-700 mb-2 flex items-center">
                        <Info className="w-3 h-3 mr-1" />
                        Description
                      </h5>
                      <p className="text-xs text-dark-600">{getAgentDescription(agent.agentType)}</p>
                    </div>

                    {showStats && agent.stats && (
                      <div>
                        <h5 className="text-sm font-medium text-dark-700 mb-2 flex items-center">
                          <Zap className="w-3 h-3 mr-1" />
                          Performance
                        </h5>
                        <div className="grid grid-cols-2 gap-3">
                          <div className="text-center">
                            <p className="text-xs text-dark-500">Completed</p>
                            <p className="font-medium text-success-400">{agent.stats.completedTasks}</p>
                          </div>
                          <div className="text-center">
                            <p className="text-xs text-dark-500">Failed</p>
                            <p className="font-medium text-red-400">{agent.stats.failedTasks}</p>
                          </div>
                          <div className="text-center">
                            <p className="text-xs text-dark-500">Success Rate</p>
                            <p className="font-medium text-primary-400">
                              {Math.round((agent.stats.completedTasks / Math.max(1, agent.stats.totalTasks)) * 100)}%
                            </p>
                          </div>
                          <div className="text-center">
                            <p className="text-xs text-dark-500">Avg Time</p>
                            <p className="font-medium text-warning-400 font-tech">
                              {formatExecutionTime(agent.stats.averageExecutionTime)}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    {agent.metadata && Object.keys(agent.metadata).length > 0 && (
                      <div>
                        <h5 className="text-sm font-medium text-dark-700 mb-2">Technical Details</h5>
                        <div className="bg-dark-300/20 rounded p-2 text-xs font-tech">
                          <pre className="text-dark-600 whitespace-pre-wrap">
                            {JSON.stringify(agent.metadata, null, 2)}
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {agents.length === 0 && (
        <div className="text-center py-8">
          <Bot className="w-12 h-12 text-dark-400 mx-auto mb-3 opacity-50" />
          <p className="text-dark-500">No agents detected</p>
          <p className="text-sm text-dark-400 mt-1">Agents will appear here when the system starts</p>
        </div>
      )}
    </div>
  );
};

export default AgentStatusPanel;