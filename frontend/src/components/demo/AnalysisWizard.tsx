import React, { useState } from 'react';
import { 
  Zap, Settings, Brain, Clock, TrendingUp, Package, 
  Calendar, Filter, PlayCircle, HelpCircle, ChevronRight,
  Database, BarChart, FileSpreadsheet, X
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { apiService } from '@/utils/api';
import { AnalysisRequest } from '@/types';

export interface DemoScenario {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  estimatedTime: string;
  features: string[];
  config: Partial<AnalysisRequest>;
  color: string;
}

interface AnalysisWizardProps {
  isOpen: boolean;
  onClose: () => void;
  onAnalysisStart?: (jobId: string) => void;
}

const AnalysisWizard: React.FC<AnalysisWizardProps> = ({
  isOpen,
  onClose,
  onAnalysisStart
}) => {
  const [step, setStep] = useState<'scenarios' | 'config' | 'confirm'>('scenarios');
  const [selectedScenario, setSelectedScenario] = useState<DemoScenario | null>(null);
  const [customConfig, setCustomConfig] = useState<AnalysisRequest>({
    date_range_start: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    date_range_end: new Date().toISOString().split('T')[0],
    tables: ['returns', 'warranties', 'products'],
    filters: { store_locations: ['all'], product_categories: ['all'] }
  });
  const [isStarting, setIsStarting] = useState(false);

  const demoScenarios: DemoScenario[] = [
    {
      id: 'quick-demo',
      name: 'Lightning Demo',
      description: 'Perfect for showcasing the system with fast processing',
      icon: <Zap className="w-6 h-6" />,
      estimatedTime: '30 seconds',
      features: ['All 6 agents active', 'Sample data processing', 'Quick insights'],
      config: {
        date_range_start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        date_range_end: new Date().toISOString().split('T')[0],
        tables: ['returns', 'warranties'],
        filters: { store_locations: ['all'], product_categories: ['electronics'] }
      },
      color: 'primary'
    },
    {
      id: 'return-analysis',
      name: 'Return Patterns',
      description: 'Deep analysis of product return trends and patterns',
      icon: <TrendingUp className="w-6 h-6" />,
      estimatedTime: '2 minutes',
      features: ['Return trend analysis', 'Category breakdowns', 'Seasonal patterns'],
      config: {
        date_range_start: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        date_range_end: new Date().toISOString().split('T')[0],
        tables: ['returns', 'products'],
        filters: { store_locations: ['all'], product_categories: ['all'] }
      },
      color: 'success'
    },
    {
      id: 'warranty-insights',
      name: 'Warranty Deep Dive',
      description: 'Focus on warranty claims and resolution efficiency',
      icon: <Package className="w-6 h-6" />,
      estimatedTime: '90 seconds',
      features: ['Warranty resolution times', 'Cost analysis', 'Issue categorization'],
      config: {
        date_range_start: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        date_range_end: new Date().toISOString().split('T')[0],
        tables: ['warranties', 'products'],
        filters: { store_locations: ['all'], product_categories: ['electronics'] }
      },
      color: 'warning'
    },
    {
      id: 'full-analysis',
      name: 'Comprehensive Analysis',
      description: 'Complete retail analysis across all data dimensions',
      icon: <Brain className="w-6 h-6" />,
      estimatedTime: '5 minutes',
      features: ['All data sources', 'Advanced RAG processing', 'Executive summary'],
      config: {
        date_range_start: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        date_range_end: new Date().toISOString().split('T')[0],
        tables: ['returns', 'warranties', 'products'],
        filters: { store_locations: ['all'], product_categories: ['all'] }
      },
      color: 'accent'
    },
    {
      id: 'custom',
      name: 'Custom Configuration',
      description: 'Configure your own analysis parameters',
      icon: <Settings className="w-6 h-6" />,
      estimatedTime: 'Variable',
      features: ['Custom date ranges', 'Selective data sources', 'Advanced filters'],
      config: customConfig,
      color: 'dark'
    }
  ];

  const getColorClasses = (color: string) => {
    switch (color) {
      case 'primary':
        return 'border-primary-500/30 bg-primary-500/10 hover:bg-primary-500/20 text-primary-400';
      case 'success':
        return 'border-success-500/30 bg-success-500/10 hover:bg-success-500/20 text-success-400';
      case 'warning':
        return 'border-warning-500/30 bg-warning-500/10 hover:bg-warning-500/20 text-warning-400';
      case 'accent':
        return 'border-accent-500/30 bg-accent-500/10 hover:bg-accent-500/20 text-accent-400';
      default:
        return 'border-dark-300/30 bg-dark-200/20 hover:bg-dark-200/30 text-dark-400';
    }
  };

  const handleScenarioSelect = (scenario: DemoScenario) => {
    setSelectedScenario(scenario);
    if (scenario.id === 'custom') {
      setStep('config');
    } else {
      setStep('confirm');
    }
  };

  const handleStartAnalysis = async () => {
    if (!selectedScenario) return;

    try {
      setIsStarting(true);
      const config = selectedScenario.id === 'custom' ? customConfig : selectedScenario.config as AnalysisRequest;
      
      const result = await apiService.startAnalysis(config);
      toast.success(`Analysis started: ${selectedScenario.name}`);
      
      onAnalysisStart?.(result.job_id);
      onClose();
    } catch (error) {
      toast.error('Failed to start analysis');
      console.error('Error starting analysis:', error);
    } finally {
      setIsStarting(false);
    }
  };

  const renderScenarios = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-dark-800 mb-2">Choose Your Analysis</h2>
        <p className="text-dark-600">Select a demo scenario or configure custom analysis</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {demoScenarios.map((scenario) => (
          <button
            key={scenario.id}
            onClick={() => handleScenarioSelect(scenario)}
            className={`
              p-6 rounded-xl border-2 transition-all duration-300 text-left group
              ${getColorClasses(scenario.color)}
            `}
          >
            <div className="flex items-start space-x-4">
              <div className={`
                p-3 rounded-lg transition-transform group-hover:scale-110
                ${getColorClasses(scenario.color)}
              `}>
                {scenario.icon}
              </div>
              
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold text-dark-800">{scenario.name}</h3>
                  <div className="flex items-center space-x-1 text-xs text-dark-500">
                    <Clock className="w-3 h-3" />
                    <span>{scenario.estimatedTime}</span>
                  </div>
                </div>
                
                <p className="text-sm text-dark-600 mb-3">{scenario.description}</p>
                
                <div className="space-y-2">
                  {scenario.features.map((feature, index) => (
                    <div key={index} className="flex items-center space-x-2 text-xs text-dark-600">
                      <div className="w-1.5 h-1.5 rounded-full bg-current opacity-60" />
                      <span>{feature}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>

      <div className="text-center pt-4">
        <button
          onClick={onClose}
          className="text-dark-500 hover:text-dark-700 transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  );

  const renderConfig = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-dark-800">Custom Configuration</h2>
          <p className="text-dark-600">Configure your analysis parameters</p>
        </div>
        <button
          onClick={() => setStep('scenarios')}
          className="text-dark-500 hover:text-primary-400 transition-colors"
        >
          Back to scenarios
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-dark-700 mb-2">
              <Calendar className="w-4 h-4 inline mr-1" />
              Date Range
            </label>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="date"
                value={customConfig.date_range_start}
                onChange={(e) => setCustomConfig({ ...customConfig, date_range_start: e.target.value })}
                className="input-field"
              />
              <input
                type="date"
                value={customConfig.date_range_end}
                onChange={(e) => setCustomConfig({ ...customConfig, date_range_end: e.target.value })}
                className="input-field"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-dark-700 mb-2">
              <Database className="w-4 h-4 inline mr-1" />
              Data Sources
            </label>
            <div className="space-y-2">
              {['returns', 'warranties', 'products'].map((table) => (
                <label key={table} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={customConfig.tables.includes(table)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setCustomConfig({
                          ...customConfig,
                          tables: [...customConfig.tables, table]
                        });
                      } else {
                        setCustomConfig({
                          ...customConfig,
                          tables: customConfig.tables.filter(t => t !== table)
                        });
                      }
                    }}
                    className="rounded border-dark-300"
                  />
                  <span className="text-sm text-dark-700 capitalize">{table}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-dark-700 mb-2">
              <Filter className="w-4 h-4 inline mr-1" />
              Store Locations
            </label>
            <select 
              className="input-field"
              value={customConfig.filters.store_locations?.[0] || 'all'}
              onChange={(e) => setCustomConfig({
                ...customConfig,
                filters: { ...customConfig.filters, store_locations: [e.target.value] }
              })}
            >
              <option value="all">All Locations</option>
              <option value="new-york">New York</option>
              <option value="los-angeles">Los Angeles</option>
              <option value="chicago">Chicago</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-dark-700 mb-2">
              <Package className="w-4 h-4 inline mr-1" />
              Product Categories
            </label>
            <select 
              className="input-field"
              value={customConfig.filters.product_categories?.[0] || 'all'}
              onChange={(e) => setCustomConfig({
                ...customConfig,
                filters: { ...customConfig.filters, product_categories: [e.target.value] }
              })}
            >
              <option value="all">All Categories</option>
              <option value="electronics">Electronics</option>
              <option value="clothing">Clothing</option>
              <option value="home-garden">Home & Garden</option>
              <option value="sports">Sports & Outdoors</option>
            </select>
          </div>
        </div>
      </div>

      <div className="flex justify-between pt-4">
        <button
          onClick={() => setStep('scenarios')}
          className="btn-secondary"
        >
          Back
        </button>
        <button
          onClick={() => setStep('confirm')}
          className="btn-primary"
          disabled={customConfig.tables.length === 0}
        >
          Continue
          <ChevronRight className="w-4 h-4 ml-1" />
        </button>
      </div>
    </div>
  );

  const renderConfirm = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-dark-800">Confirm Analysis</h2>
          <p className="text-dark-600">Review and start your analysis</p>
        </div>
        <button
          onClick={() => setStep(selectedScenario?.id === 'custom' ? 'config' : 'scenarios')}
          className="text-dark-500 hover:text-primary-400 transition-colors"
        >
          Back
        </button>
      </div>

      {selectedScenario && (
        <div className="card-tech">
          <div className="flex items-start space-x-4 mb-6">
            <div className={`p-3 rounded-lg ${getColorClasses(selectedScenario.color)}`}>
              {selectedScenario.icon}
            </div>
            <div>
              <h3 className="text-xl font-semibold text-dark-800 mb-2">{selectedScenario.name}</h3>
              <p className="text-dark-600">{selectedScenario.description}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="text-center">
              <Clock className="w-6 h-6 text-primary-400 mx-auto mb-2" />
              <p className="text-sm font-medium text-dark-700">Estimated Time</p>
              <p className="text-xs text-dark-500">{selectedScenario.estimatedTime}</p>
            </div>
            <div className="text-center">
              <Database className="w-6 h-6 text-success-400 mx-auto mb-2" />
              <p className="text-sm font-medium text-dark-700">Data Sources</p>
              <p className="text-xs text-dark-500">
                {(selectedScenario.config.tables || []).join(', ')}
              </p>
            </div>
            <div className="text-center">
              <BarChart className="w-6 h-6 text-warning-400 mx-auto mb-2" />
              <p className="text-sm font-medium text-dark-700">Output</p>
              <p className="text-xs text-dark-500">Excel report + Dashboard</p>
            </div>
          </div>

          <div className="space-y-3">
            <h4 className="font-medium text-dark-700">What will happen:</h4>
            <div className="space-y-2">
              {[
                'Coordinator Agent will orchestrate the pipeline',
                'Data Fetch Agent will retrieve your retail data',
                'Normalization Agent will clean and standardize data',
                'RAG Agent will generate AI-powered insights',
                'Report Agent will create professional Excel reports',
                'Dashboard Agent will display results in real-time'
              ].map((step, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <div className="w-6 h-6 rounded-full bg-primary-500/20 text-primary-400 flex items-center justify-center text-xs font-medium">
                    {index + 1}
                  </div>
                  <span className="text-sm text-dark-600">{step}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-center space-x-4 pt-4">
        <button
          onClick={() => setStep(selectedScenario?.id === 'custom' ? 'config' : 'scenarios')}
          className="btn-secondary"
        >
          Back to Edit
        </button>
        <button
          onClick={handleStartAnalysis}
          disabled={isStarting}
          className="btn-primary flex items-center space-x-2"
        >
          <PlayCircle className="w-4 h-4" />
          <span>{isStarting ? 'Starting...' : 'Start Analysis'}</span>
        </button>
      </div>
    </div>
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-dark-100 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-dark-100 p-6 border-b border-dark-200/30 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Brain className="w-6 h-6 text-primary-400" />
            <h1 className="text-xl font-bold text-dark-800">Multi-Agent Analysis Wizard</h1>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-dark-400 hover:text-dark-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6">
          {step === 'scenarios' && renderScenarios()}
          {step === 'config' && renderConfig()}
          {step === 'confirm' && renderConfirm()}
        </div>
      </div>
    </div>
  );
};

export default AnalysisWizard;