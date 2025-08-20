import React, { useState } from 'react';
import { Save, RefreshCw, Database, Brain, FileText, Globe, Shield } from 'lucide-react';
import { toast } from 'react-hot-toast';

const Settings: React.FC = () => {
  const [settings, setSettings] = useState({
    database: {
      url: 'sqlite:///retail_data.db',
      echo: false
    },
    rag: {
      enableMockMode: false,
      maxApiCalls: 10,
      similarityThreshold: 0.2,
      topKRetrieval: 5
    },
    report: {
      outputDirectory: 'output/reports',
      includeTimestamp: true,
      createCharts: true
    },
    dashboard: {
      host: '127.0.0.1',
      port: 8000,
      debug: false
    }
  });

  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success('Settings saved successfully');
    } catch (error) {
      toast.error('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const updateSetting = (section: string, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section as keyof typeof prev],
        [key]: value
      }
    }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-dark-800">Settings</h2>
          <p className="text-dark-500 mt-1">Configure your multi-agent system</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="btn-primary flex items-center space-x-2 disabled:opacity-50"
        >
          {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          <span>{saving ? 'Saving...' : 'Save Changes'}</span>
        </button>
      </div>

      {/* Database Settings */}
      <div className="card-tech">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-8 h-8 bg-primary-500/20 rounded-lg flex items-center justify-center">
            <Database className="w-4 h-4 text-primary-400" />
          </div>
          <h3 className="text-lg font-semibold text-dark-800">Database Configuration</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-dark-700 mb-2">Database URL</label>
            <input
              type="text"
              value={settings.database.url}
              onChange={(e) => updateSetting('database', 'url', e.target.value)}
              className="w-full px-3 py-2 bg-dark-200/30 border border-dark-300/30 rounded-lg text-dark-700 focus:outline-none focus:border-primary-500/50"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-dark-700 mb-2">Enable Query Logging</label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.database.echo}
                onChange={(e) => updateSetting('database', 'echo', e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm text-dark-600">Echo SQL queries to console</span>
            </label>
          </div>
        </div>
      </div>

      {/* RAG Settings */}
      <div className="card-tech">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-8 h-8 bg-success-500/20 rounded-lg flex items-center justify-center">
            <Brain className="w-4 h-4 text-success-400" />
          </div>
          <h3 className="text-lg font-semibold text-dark-800">RAG Agent Configuration</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-dark-700 mb-2">Max API Calls per Session</label>
            <input
              type="number"
              value={settings.rag.maxApiCalls}
              onChange={(e) => updateSetting('rag', 'maxApiCalls', parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-dark-200/30 border border-dark-300/30 rounded-lg text-dark-700 focus:outline-none focus:border-primary-500/50"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-dark-700 mb-2">Similarity Threshold</label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={settings.rag.similarityThreshold}
              onChange={(e) => updateSetting('rag', 'similarityThreshold', parseFloat(e.target.value))}
              className="w-full px-3 py-2 bg-dark-200/30 border border-dark-300/30 rounded-lg text-dark-700 focus:outline-none focus:border-primary-500/50"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-dark-700 mb-2">Top K Retrieval</label>
            <input
              type="number"
              value={settings.rag.topKRetrieval}
              onChange={(e) => updateSetting('rag', 'topKRetrieval', parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-dark-200/30 border border-dark-300/30 rounded-lg text-dark-700 focus:outline-none focus:border-primary-500/50"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-dark-700 mb-2">Mock Mode</label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.rag.enableMockMode}
                onChange={(e) => updateSetting('rag', 'enableMockMode', e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm text-dark-600">Enable mock mode for testing</span>
            </label>
          </div>
        </div>
      </div>

      {/* Report Settings */}
      <div className="card-tech">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-8 h-8 bg-warning-500/20 rounded-lg flex items-center justify-center">
            <FileText className="w-4 h-4 text-warning-400" />
          </div>
          <h3 className="text-lg font-semibold text-dark-800">Report Configuration</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-dark-700 mb-2">Output Directory</label>
            <input
              type="text"
              value={settings.report.outputDirectory}
              onChange={(e) => updateSetting('report', 'outputDirectory', e.target.value)}
              className="w-full px-3 py-2 bg-dark-200/30 border border-dark-300/30 rounded-lg text-dark-700 focus:outline-none focus:border-primary-500/50"
            />
          </div>
          
          <div className="space-y-3">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.report.includeTimestamp}
                onChange={(e) => updateSetting('report', 'includeTimestamp', e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm text-dark-600">Include timestamp in filename</span>
            </label>
            
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.report.createCharts}
                onChange={(e) => updateSetting('report', 'createCharts', e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm text-dark-600">Generate charts and visualizations</span>
            </label>
          </div>
        </div>
      </div>

      {/* Dashboard Settings */}
      <div className="card-tech">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-8 h-8 bg-accent-500/20 rounded-lg flex items-center justify-center">
            <Globe className="w-4 h-4 text-accent-400" />
          </div>
          <h3 className="text-lg font-semibold text-dark-800">Dashboard Configuration</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-dark-700 mb-2">Host</label>
            <input
              type="text"
              value={settings.dashboard.host}
              onChange={(e) => updateSetting('dashboard', 'host', e.target.value)}
              className="w-full px-3 py-2 bg-dark-200/30 border border-dark-300/30 rounded-lg text-dark-700 focus:outline-none focus:border-primary-500/50"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-dark-700 mb-2">Port</label>
            <input
              type="number"
              value={settings.dashboard.port}
              onChange={(e) => updateSetting('dashboard', 'port', parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-dark-200/30 border border-dark-300/30 rounded-lg text-dark-700 focus:outline-none focus:border-primary-500/50"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-dark-700 mb-2">Debug Mode</label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.dashboard.debug}
                onChange={(e) => updateSetting('dashboard', 'debug', e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm text-dark-600">Enable debug mode</span>
            </label>
          </div>
        </div>
      </div>

      {/* System Info */}
      <div className="card-tech">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-8 h-8 bg-secondary-500/20 rounded-lg flex items-center justify-center">
            <Shield className="w-4 h-4 text-secondary-400" />
          </div>
          <h3 className="text-lg font-semibold text-dark-800">System Information</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-dark-500">Version:</span>
              <span className="font-tech text-dark-700">1.0.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-dark-500">Environment:</span>
              <span className="font-tech text-dark-700">Development</span>
            </div>
            <div className="flex justify-between">
              <span className="text-dark-500">Python Version:</span>
              <span className="font-tech text-dark-700">3.10+</span>
            </div>
          </div>
          
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-dark-500">Active Agents:</span>
              <span className="font-tech text-success-400">5</span>
            </div>
            <div className="flex justify-between">
              <span className="text-dark-500">Database Status:</span>
              <span className="font-tech text-success-400">Connected</span>
            </div>
            <div className="flex justify-between">
              <span className="text-dark-500">Last Backup:</span>
              <span className="font-tech text-dark-700">2h ago</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;