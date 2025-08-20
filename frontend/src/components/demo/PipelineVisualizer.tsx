import React from 'react';
import { 
  Bot, Database, Sparkles, Brain, FileText, Monitor, 
  ArrowRight, CheckCircle, Clock, XCircle, AlertCircle 
} from 'lucide-react';

export interface PipelineStage {
  id: string;
  name: string;
  agentType: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  progress?: number;
  startTime?: Date;
  endTime?: Date;
  message?: string;
}

interface PipelineVisualizerProps {
  stages: PipelineStage[];
  currentStage?: string;
  className?: string;
  compact?: boolean;
  showProgress?: boolean;
  showTimings?: boolean;
}

const PipelineVisualizer: React.FC<PipelineVisualizerProps> = ({
  stages,
  currentStage,
  className = '',
  compact = false,
  showProgress = true,
  showTimings = false
}) => {
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
      case 'completed':
        return CheckCircle;
      case 'running':
        return Clock;
      case 'failed':
        return XCircle;
      case 'skipped':
        return AlertCircle;
      default:
        return Clock;
    }
  };

  const getStatusColor = (status: string, isCurrent: boolean = false) => {
    if (isCurrent) {
      return 'border-primary-500 bg-primary-500/20 text-primary-400';
    }
    
    switch (status) {
      case 'completed':
        return 'border-success-500 bg-success-500/20 text-success-400';
      case 'running':
        return 'border-warning-500 bg-warning-500/20 text-warning-400';
      case 'failed':
        return 'border-red-500 bg-red-500/20 text-red-400';
      case 'skipped':
        return 'border-dark-400 bg-dark-400/20 text-dark-400';
      default:
        return 'border-dark-300/30 bg-dark-200/20 text-dark-500';
    }
  };

  const getConnectorColor = (fromStatus: string, toStatus: string) => {
    if (fromStatus === 'completed' && (toStatus === 'running' || toStatus === 'completed')) {
      return 'border-success-400';
    } else if (fromStatus === 'failed') {
      return 'border-red-400';
    } else if (fromStatus === 'running') {
      return 'border-warning-400';
    }
    return 'border-dark-300/30';
  };

  const formatDuration = (startTime?: Date, endTime?: Date) => {
    if (!startTime) return '';
    const end = endTime || new Date();
    const duration = Math.round((end.getTime() - startTime.getTime()) / 1000);
    
    if (duration < 60) return `${duration}s`;
    const minutes = Math.floor(duration / 60);
    const seconds = duration % 60;
    return `${minutes}m ${seconds}s`;
  };

  const calculateOverallProgress = () => {
    const totalStages = stages.length;
    const completedStages = stages.filter(s => s.status === 'completed').length;
    const currentProgress = stages.find(s => s.id === currentStage)?.progress || 0;
    
    return totalStages > 0 ? (completedStages + currentProgress) / totalStages : 0;
  };

  if (compact) {
    return (
      <div className={`card-tech ${className}`}>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-dark-800">Pipeline Progress</h3>
          <span className="text-sm text-dark-500">
            {Math.round(calculateOverallProgress() * 100)}%
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          {stages.map((stage, index) => {
            const Icon = getAgentIcon(stage.agentType);
            const isCurrent = stage.id === currentStage;
            
            return (
              <React.Fragment key={stage.id}>
                <div 
                  className={`
                    relative flex items-center justify-center w-8 h-8 rounded-lg border-2 transition-all duration-300
                    ${getStatusColor(stage.status, isCurrent)}
                  `}
                  title={`${stage.name} - ${stage.status}`}
                >
                  <Icon className="w-4 h-4" />
                  {stage.status === 'running' && (
                    <div className="absolute inset-0 rounded-lg border-2 border-primary-400 animate-pulse" />
                  )}
                </div>
                
                {index < stages.length - 1 && (
                  <div className={`
                    w-4 h-0.5 transition-colors duration-300
                    ${getConnectorColor(stage.status, stages[index + 1]?.status || 'pending')}
                  `} />
                )}
              </React.Fragment>
            );
          })}
        </div>

        {showProgress && (
          <div className="mt-3">
            <div className="w-full bg-dark-300/30 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-primary-500 to-primary-400 h-2 rounded-full transition-all duration-500"
                style={{ width: `${calculateOverallProgress() * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`card-tech ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <Bot className="w-5 h-5 text-primary-400" />
          <h3 className="text-lg font-semibold text-dark-800">Multi-Agent Pipeline</h3>
        </div>
        <div className="text-sm text-dark-500">
          {Math.round(calculateOverallProgress() * 100)}% Complete
        </div>
      </div>

      <div className="space-y-4">
        {stages.map((stage, index) => {
          const Icon = getAgentIcon(stage.agentType);
          const StatusIcon = getStatusIcon(stage.status);
          const isCurrent = stage.id === currentStage;
          const isCompleted = stage.status === 'completed';
          const isFailed = stage.status === 'failed';

          return (
            <div key={stage.id} className="relative">
              <div className={`
                flex items-center space-x-4 p-3 rounded-lg border transition-all duration-300
                ${getStatusColor(stage.status, isCurrent)}
                ${isCurrent ? 'transform scale-105' : ''}
              `}>
                <div className="flex-shrink-0">
                  <div className="relative">
                    <div className={`
                      w-10 h-10 rounded-lg border-2 flex items-center justify-center
                      ${getStatusColor(stage.status, isCurrent)}
                    `}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div className={`
                      absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-dark-100 flex items-center justify-center
                      ${getStatusColor(stage.status)}
                    `}>
                      <StatusIcon className="w-2.5 h-2.5" />
                    </div>
                    {stage.status === 'running' && (
                      <div className="absolute inset-0 rounded-lg border-2 border-primary-400 animate-pulse" />
                    )}
                  </div>
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-dark-700">{stage.name}</h4>
                    {showTimings && (stage.startTime || stage.endTime) && (
                      <span className="text-xs text-dark-500 font-tech">
                        {formatDuration(stage.startTime, stage.endTime)}
                      </span>
                    )}
                  </div>
                  
                  {stage.message && (
                    <p className="text-sm text-dark-600 mt-1">{stage.message}</p>
                  )}

                  {showProgress && stage.status === 'running' && typeof stage.progress === 'number' && (
                    <div className="mt-2">
                      <div className="w-full bg-dark-300/30 rounded-full h-1.5">
                        <div 
                          className="bg-gradient-to-r from-primary-500 to-primary-400 h-1.5 rounded-full transition-all duration-500"
                          style={{ width: `${stage.progress * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-dark-500 mt-1">
                        {Math.round(stage.progress * 100)}%
                      </span>
                    </div>
                  )}
                </div>

                {isCurrent && (
                  <div className="flex-shrink-0">
                    <div className="w-2 h-2 bg-primary-400 rounded-full animate-pulse" />
                  </div>
                )}
              </div>

              {index < stages.length - 1 && (
                <div className="flex justify-center py-2">
                  <ArrowRight className={`
                    w-4 h-4 transition-colors duration-300
                    ${getConnectorColor(stage.status, stages[index + 1]?.status || 'pending') === 'border-success-400' 
                      ? 'text-success-400' 
                      : getConnectorColor(stage.status, stages[index + 1]?.status || 'pending') === 'border-red-400'
                      ? 'text-red-400'
                      : getConnectorColor(stage.status, stages[index + 1]?.status || 'pending') === 'border-warning-400'
                      ? 'text-warning-400'
                      : 'text-dark-400'
                    }
                  `} />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {showProgress && (
        <div className="mt-6 pt-4 border-t border-dark-200/30">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-dark-700">Overall Progress</span>
            <span className="text-sm text-dark-600">{Math.round(calculateOverallProgress() * 100)}%</span>
          </div>
          <div className="w-full bg-dark-300/30 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-primary-500 to-primary-400 h-2 rounded-full transition-all duration-500"
              style={{ width: `${calculateOverallProgress() * 100}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default PipelineVisualizer;