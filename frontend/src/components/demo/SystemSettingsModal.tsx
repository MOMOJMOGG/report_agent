import React, { useState } from 'react';
import { 
  X, Settings, Bot, Database, Sparkles, Brain, FileText, Monitor,
  Save, RotateCcw, AlertTriangle, CheckCircle, Info
} from 'lucide-react';
import { toast } from 'react-hot-toast';

interface SystemSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface AgentSettings {
  enabled: boolean;
  timeout: number;
  retries: number;
  [key: string]: any;
}

interface SystemSettings {
  coordinator: AgentSettings;
  data_fetch: AgentSettings;
  normalization: AgentSettings;
  rag: AgentSettings;
  report: AgentSettings;
  dashboard: AgentSettings;
}

const SystemSettingsModal: React.FC<SystemSettingsModalProps> = ({ isOpen, onClose }) => {
  const [settings, setSettings] = useState<SystemSettings>({
    coordinator: {
      enabled: true,
      timeout: 300,
      retries: 3,
      maxConcurrentPipelines: 5,
      heartbeatInterval: 30
    },
    data_fetch: {
      enabled: true,
      timeout: 180,
      retries: 2,
      batchSize: 1000,
      connectionPoolSize: 5
    },
    normalization: {
      enabled: true,
      timeout: 120,
      retries: 2,
      qualityThreshold: 0.8,
      removeDuplicates: true
    },
    rag: {
      enabled: true,
      timeout: 600,
      retries: 1,
      maxTokens: 150,
      similarityThreshold: 0.2,
      topK: 5,
      enableMockMode: false
    },
    report: {
      enabled: true,
      timeout: 240,
      retries: 2,
      includeCharts: true,
      fileFormat: 'xlsx',
      compressionLevel: 6
    },
    dashboard: {
      enabled: true,
      timeout: 60,
      retries: 3,
      maxFileSize: 10,
      corsEnabled: true
    }
  });

  const [activeTab, setActiveTab] = useState<keyof SystemSettings>('coordinator');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const getAgentIcon = (agentType: string) => {
    switch (agentType) {
      case 'coordinator': return Bot;
      case 'data_fetch': return Database;
      case 'normalization': return Sparkles;
      case 'rag': return Brain;
      case 'report': return FileText;
      case 'dashboard': return Monitor;
      default: return Settings;
    }
  };

  const getAgentColor = (agentType: string) => {
    switch (agentType) {
      case 'coordinator': return 'primary';
      case 'data_fetch': return 'success';
      case 'normalization': return 'warning';
      case 'rag': return 'accent';
      case 'report': return 'primary';
      case 'dashboard': return 'dark';
      default: return 'dark';
    }
  };

  const getColorClasses = (color: string) => {
    switch (color) {
      case 'primary': return 'text-primary-400 bg-primary-500/10 border-primary-500/20';
      case 'success': return 'text-success-400 bg-success-500/10 border-success-500/20';
      case 'warning': return 'text-warning-400 bg-warning-500/10 border-warning-500/20';
      case 'accent': return 'text-accent-400 bg-accent-500/10 border-accent-500/20';
      default: return 'text-dark-400 bg-dark-500/10 border-dark-500/20';
    }
  };

  const formatAgentName = (agentType: string) => {
    return agentType.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ') + ' Agent';
  };

  const updateSetting = <T extends keyof SystemSettings>(
    agent: T, 
    key: keyof AgentSettings, 
    value: any
  ) => {
    setSettings(prev => ({
      ...prev,
      [agent]: {
        ...prev[agent],
        [key]: value
      }
    }));
    setHasUnsavedChanges(true);
  };

  const handleSave = async () => {
    try {
      // In a real implementation, this would call an API
      console.log('Saving settings:', settings);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast.success('Settings saved successfully!');
      setHasUnsavedChanges(false);
    } catch (error) {
      toast.error('Failed to save settings');
    }
  };

  const handleReset = () => {
    // Reset to defaults
    setSettings({
      coordinator: {
        enabled: true,
        timeout: 300,
        retries: 3,
        maxConcurrentPipelines: 5,
        heartbeatInterval: 30
      },
      data_fetch: {
        enabled: true,
        timeout: 180,
        retries: 2,
        batchSize: 1000,
        connectionPoolSize: 5
      },
      normalization: {
        enabled: true,
        timeout: 120,
        retries: 2,
        qualityThreshold: 0.8,
        removeDuplicates: true
      },
      rag: {
        enabled: true,
        timeout: 600,
        retries: 1,
        maxTokens: 150,
        similarityThreshold: 0.2,
        topK: 5,
        enableMockMode: false
      },
      report: {
        enabled: true,
        timeout: 240,
        retries: 2,
        includeCharts: true,
        fileFormat: 'xlsx',
        compressionLevel: 6
      },
      dashboard: {
        enabled: true,
        timeout: 60,
        retries: 3,
        maxFileSize: 10,
        corsEnabled: true
      }
    });
    setHasUnsavedChanges(true);
    toast.info('Settings reset to defaults');
  };

  const renderAgentSettings = (agentType: keyof SystemSettings) => {
    const agentSettings = settings[agentType];
    const Icon = getAgentIcon(agentType);
    const color = getAgentColor(agentType);

    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className={`w-10 h-10 rounded-lg border flex items-center justify-center ${getColorClasses(color)}`}>
            <Icon className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-dark-800">{formatAgentName(agentType)}</h3>
            <p className="text-sm text-dark-500">Configure agent parameters and behavior</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="flex items-center space-x-2 mb-2">
                <input
                  type="checkbox"
                  checked={agentSettings.enabled}
                  onChange={(e) => updateSetting(agentType, 'enabled', e.target.checked)}
                  className="rounded border-dark-300"
                />
                <span className="text-sm font-medium text-dark-700">Enable Agent</span>
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-dark-700 mb-2">
                Timeout (seconds)
              </label>
              <input
                type="number"
                value={agentSettings.timeout}
                onChange={(e) => updateSetting(agentType, 'timeout', parseInt(e.target.value))}
                className="input-field"
                min="1"
                max="3600"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-dark-700 mb-2">
                Max Retries
              </label>
              <input
                type="number"
                value={agentSettings.retries}
                onChange={(e) => updateSetting(agentType, 'retries', parseInt(e.target.value))}
                className="input-field"
                min="0"
                max="10"
              />
            </div>
          </div>

          <div className="space-y-4">
            {/* Agent-specific settings */}
            {agentType === 'coordinator' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-dark-700 mb-2">
                    Max Concurrent Pipelines
                  </label>
                  <input
                    type="number"
                    value={agentSettings.maxConcurrentPipelines}
                    onChange={(e) => updateSetting(agentType, 'maxConcurrentPipelines', parseInt(e.target.value))}
                    className="input-field"
                    min="1"
                    max="20"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-dark-700 mb-2">
                    Heartbeat Interval (seconds)
                  </label>
                  <input
                    type="number"
                    value={agentSettings.heartbeatInterval}
                    onChange={(e) => updateSetting(agentType, 'heartbeatInterval', parseInt(e.target.value))}
                    className="input-field"
                    min="5"
                    max="300"
                  />
                </div>
              </>
            )}

            {agentType === 'rag' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-dark-700 mb-2">
                    Max Tokens
                  </label>
                  <input
                    type="number"
                    value={agentSettings.maxTokens}
                    onChange={(e) => updateSetting(agentType, 'maxTokens', parseInt(e.target.value))}
                    className="input-field"
                    min="50"
                    max="1000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-dark-700 mb-2">
                    Similarity Threshold
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={agentSettings.similarityThreshold}
                    onChange={(e) => updateSetting(agentType, 'similarityThreshold', parseFloat(e.target.value))}
                    className="input-field"
                    min="0"
                    max="1"
                  />
                </div>
                <div>
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={agentSettings.enableMockMode}
                      onChange={(e) => updateSetting(agentType, 'enableMockMode', e.target.checked)}
                      className="rounded border-dark-300"
                    />
                    <span className="text-sm font-medium text-dark-700">Enable Mock Mode</span>
                  </label>
                </div>
              </>
            )}

            {agentType === 'report' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-dark-700 mb-2">
                    File Format
                  </label>
                  <select
                    value={agentSettings.fileFormat}
                    onChange={(e) => updateSetting(agentType, 'fileFormat', e.target.value)}
                    className="input-field"
                  >
                    <option value="xlsx">Excel (.xlsx)</option>
                    <option value="csv">CSV (.csv)</option>
                    <option value="both">Both formats</option>
                  </select>
                </div>
                <div>
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={agentSettings.includeCharts}
                      onChange={(e) => updateSetting(agentType, 'includeCharts', e.target.checked)}
                      className="rounded border-dark-300"
                    />
                    <span className="text-sm font-medium text-dark-700">Include Charts</span>
                  </label>
                </div>
              </>
            )}
          </div>
        </div>

        <div className="bg-dark-200/30 p-4 rounded-lg">
          <div className="flex items-start space-x-2">
            <Info className="w-4 h-4 text-primary-400 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-dark-600">
              <p className="font-medium mb-1">Configuration Notes:</p>
              <ul className="list-disc list-inside space-y-1 text-xs">
                <li>Changes take effect after saving and restarting the agent</li>
                <li>Timeout values should account for processing complexity</li>
                <li>Higher retry counts improve reliability but increase latency</li>
                <li>Monitor performance after changes to ensure optimal settings</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-dark-100 rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-dark-100 p-6 border-b border-dark-200/30 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Settings className="w-6 h-6 text-primary-400" />
            <h1 className="text-xl font-bold text-dark-800">System Settings</h1>
            {hasUnsavedChanges && (
              <div className="flex items-center space-x-1 text-warning-400">
                <AlertTriangle className="w-4 h-4" />
                <span className="text-xs">Unsaved changes</span>
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 text-dark-400 hover:text-dark-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex">
          {/* Sidebar */}
          <div className="w-64 bg-dark-200/30 p-4">
            <nav className="space-y-2">
              {Object.keys(settings).map((agentType) => {
                const Icon = getAgentIcon(agentType);
                const color = getAgentColor(agentType);
                const isActive = activeTab === agentType;
                
                return (
                  <button
                    key={agentType}
                    onClick={() => setActiveTab(agentType as keyof SystemSettings)}
                    className={`
                      w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors
                      ${isActive 
                        ? `${getColorClasses(color)} border` 
                        : 'text-dark-600 hover:text-dark-800 hover:bg-dark-200/20'
                      }
                    `}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-sm font-medium">{formatAgentName(agentType)}</span>
                    {settings[agentType as keyof SystemSettings].enabled ? (
                      <CheckCircle className="w-3 h-3 text-success-400 ml-auto" />
                    ) : (
                      <AlertTriangle className="w-3 h-3 text-warning-400 ml-auto" />
                    )}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Content */}
          <div className="flex-1 p-6">
            {renderAgentSettings(activeTab)}
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-dark-100 p-6 border-t border-dark-200/30 flex justify-between">
          <button
            onClick={handleReset}
            className="btn-secondary flex items-center space-x-2"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Reset to Defaults</span>
          </button>
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="btn-primary flex items-center space-x-2"
              disabled={!hasUnsavedChanges}
            >
              <Save className="w-4 h-4" />
              <span>Save Settings</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemSettingsModal;