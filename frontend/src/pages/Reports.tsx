import React, { useState, useEffect, ErrorBoundary } from 'react';
import { Download, FileText, Calendar, HardDrive, RefreshCw, Trash2, Eye, Filter, AlertTriangle } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useReports } from '@/hooks/useApi';
import { formatTimestamp, formatBytes } from '@/utils/formatters';

// Error Boundary Component
class ReportsErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Reports component error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="space-y-6">
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-red-500/20 rounded-xl flex items-center justify-center mx-auto mb-4">
              <AlertTriangle className="w-8 h-8 text-red-400" />
            </div>
            <h2 className="text-xl font-bold text-dark-800 mb-2">Reports Page Error</h2>
            <p className="text-dark-500 mb-4">Something went wrong loading the reports page</p>
            <div className="bg-dark-200/30 p-4 rounded-lg mb-4 text-left max-w-md mx-auto">
              <pre className="text-xs text-red-400 overflow-auto">
                {this.state.error?.toString()}
              </pre>
            </div>
            <button 
              onClick={() => window.location.reload()} 
              className="btn-primary"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

interface SampleReport {
  id: string;
  file_path: string;
  report_type: string;
  created_at: string;
  size_bytes: number;
  worksheets: string[];
  job_id: string;
  status: string;
}

const ReportsContent: React.FC = () => {
  const { reports, loading, error } = useReports();
  const [sampleReports, setSampleReports] = useState<SampleReport[]>([]);
  const [typeFilter, setTypeFilter] = useState('all');
  const [refreshing, setRefreshing] = useState(false);
  const [debugInfo, setDebugInfo] = useState<string>('');
  const [componentLoaded, setComponentLoaded] = useState(false);

  // Component initialization
  useEffect(() => {
    console.log('Reports component mounting...');
    setComponentLoaded(true);
    return () => {
      console.log('Reports component unmounting...');
    };
  }, []);

  // Create sample reports for demonstration
  useEffect(() => {
    try {
      console.log('Setting up sample reports...');
      const samples: SampleReport[] = [
      {
        id: 'rpt_001',
        file_path: 'output/reports/retail_analysis_2024-01-20_14-30-15.xlsx',
        report_type: 'excel_comprehensive',
        created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        size_bytes: 145420,
        worksheets: ['Executive Summary', 'Returns Analysis', 'Warranty Claims', 'Product Performance'],
        job_id: 'job_abc123',
        status: 'completed'
      },
      {
        id: 'rpt_002',
        file_path: 'output/reports/warranty_deep_dive_2024-01-20_13-15-30.xlsx',
        report_type: 'excel_warranty',
        created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
        size_bytes: 89320,
        worksheets: ['Warranty Overview', 'Resolution Times', 'Cost Analysis'],
        job_id: 'job_def456',
        status: 'completed'
      },
      {
        id: 'rpt_003',
        file_path: 'output/reports/returns_pattern_analysis_2024-01-19_16-45-22.xlsx',
        report_type: 'excel_returns',
        created_at: new Date(Date.now() - 22 * 60 * 60 * 1000).toISOString(),
        size_bytes: 203150,
        worksheets: ['Return Trends', 'Category Analysis', 'Seasonal Patterns', 'Store Comparison'],
        job_id: 'job_ghi789',
        status: 'completed'
      },
      {
        id: 'rpt_004',
        file_path: 'output/reports/quick_demo_analysis_2024-01-20_15-22-18.csv',
        report_type: 'csv_summary',
        created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        size_bytes: 12480,
        worksheets: ['Summary Data'],
        job_id: 'job_jkl012',
        status: 'completed'
      },
      {
        id: 'rpt_005',
        file_path: 'output/reports/electronics_focus_2024-01-20_12-08-45.xlsx',
        report_type: 'excel_category',
        created_at: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
        size_bytes: 167890,
        worksheets: ['Electronics Overview', 'Return Reasons', 'Warranty Issues'],
        job_id: 'job_mno345',
        status: 'completed'
      }
      ];
      setSampleReports(samples);
      console.log('Sample reports set successfully:', samples.length);
    } catch (error) {
      console.error('Error setting up sample reports:', error);
      toast.error('Failed to initialize sample reports');
    }
  }, []);

  // Debug info effect
  useEffect(() => {
    const debugData = {
      apiReports: reports.length,
      sampleReports: sampleReports.length,
      loading,
      error,
      totalFiltered: 0
    };
    setDebugInfo(JSON.stringify(debugData, null, 2));
  }, [reports, sampleReports, loading, error]);

  const allReports = [...reports, ...sampleReports];
  const filteredReports = allReports.filter(report => {
    if (typeFilter === 'all') return true;
    return report.report_type && report.report_type.includes(typeFilter);
  });

  const handleDownload = (report: SampleReport) => {
    try {
      // Create download link
      const filename = report.file_path.split('/').pop() || 'report.xlsx';
      const link = document.createElement('a');
      link.href = `/api/v1/reports/${filename}/download`;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast.success(`Downloading ${filename}`);
    } catch (error) {
      toast.error('Failed to download report');
    }
  };

  const handlePreview = (report: SampleReport) => {
    toast.info(`Preview functionality for ${report.report_type} reports coming soon!`);
  };

  const handleDeleteReport = async (reportId: string) => {
    const confirmed = window.confirm('Are you sure you want to delete this report?');
    if (!confirmed) return;

    try {
      // For sample reports, just remove from state
      setSampleReports(prev => prev.filter(r => r.id !== reportId));
      toast.success('Report deleted successfully');
    } catch (error) {
      toast.error('Failed to delete report');
    }
  };

  const handleRefreshReports = async () => {
    setRefreshing(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success('Reports refreshed');
    } catch (error) {
      toast.error('Failed to refresh reports');
    } finally {
      setRefreshing(false);
    }
  };

  const getReportTypeColor = (type: string) => {
    if (type.includes('excel')) {
      if (type.includes('comprehensive')) return 'bg-primary-500/20 text-primary-400';
      if (type.includes('warranty')) return 'bg-warning-500/20 text-warning-400';
      if (type.includes('returns')) return 'bg-success-500/20 text-success-400';
      if (type.includes('category')) return 'bg-accent-500/20 text-accent-400';
    }
    return 'bg-dark-500/20 text-dark-400';
  };

  const getReportTypeName = (type: string) => {
    const typeMap: Record<string, string> = {
      'excel_comprehensive': 'Comprehensive Analysis',
      'excel_warranty': 'Warranty Focus',
      'excel_returns': 'Returns Analysis',
      'excel_category': 'Category Focus',
      'csv_summary': 'CSV Summary',
      'unknown': 'Unknown Type'
    };
    return typeMap[type] || type || 'Unknown Type';
  };

  // Show loading state until component is properly initialized
  if (!componentLoaded) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-dark-500">Loading Reports...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-dark-800">Analysis Reports</h2>
          <p className="text-dark-500 mt-1">Download and manage your analysis reports</p>
          {error && (
            <div className="mt-2 p-2 bg-red-500/10 border border-red-500/20 rounded text-red-400 text-sm">
              API Error: {error}
            </div>
          )}
          {process.env.NODE_ENV === 'development' && (
            <details className="mt-2">
              <summary className="text-xs text-dark-500 cursor-pointer">Debug Info</summary>
              <pre className="mt-1 p-2 bg-dark-300/20 rounded text-xs font-mono text-dark-600">
                {debugInfo}
              </pre>
            </details>
          )}
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="input-field text-sm"
          >
            <option value="all">All Types</option>
            <option value="excel">Excel Reports</option>
            <option value="csv">CSV Reports</option>
            <option value="comprehensive">Comprehensive</option>
            <option value="warranty">Warranty Focus</option>
            <option value="returns">Returns Analysis</option>
          </select>
          <button
            onClick={handleRefreshReports}
            disabled={refreshing}
            className="btn-secondary flex items-center space-x-2 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card-tech text-center">
          <div className="w-12 h-12 bg-primary-500/20 rounded-xl flex items-center justify-center mx-auto mb-3">
            <FileText className="w-6 h-6 text-primary-400" />
          </div>
          <p className="text-2xl font-bold text-dark-800">{filteredReports.length}</p>
          <p className="text-sm text-dark-500">Available Reports</p>
        </div>

        <div className="card-tech text-center">
          <div className="w-12 h-12 bg-success-500/20 rounded-xl flex items-center justify-center mx-auto mb-3">
            <Calendar className="w-6 h-6 text-success-400" />
          </div>
          <p className="text-2xl font-bold text-dark-800">
            {filteredReports.filter(r => {
              if (!r.created_at) return false;
              const reportDate = new Date(r.created_at);
              const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
              return reportDate > weekAgo;
            }).length}
          </p>
          <p className="text-sm text-dark-500">This Week</p>
        </div>

        <div className="card-tech text-center">
          <div className="w-12 h-12 bg-warning-500/20 rounded-xl flex items-center justify-center mx-auto mb-3">
            <HardDrive className="w-6 h-6 text-warning-400" />
          </div>
          <p className="text-2xl font-bold text-dark-800">
            {formatBytes(filteredReports.reduce((total, report) => total + (report.size_bytes || 0), 0))}
          </p>
          <p className="text-sm text-dark-500">Total Size</p>
        </div>
      </div>

      {/* Reports List */}
      <div className="card-tech">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-dark-800">Available Reports</h3>
          <span className="text-sm text-dark-500">{filteredReports.length} reports</span>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
            <span className="ml-2 text-dark-500">Loading reports...</span>
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <div className="w-12 h-12 bg-red-500/20 rounded-xl flex items-center justify-center mx-auto mb-3">
              <AlertTriangle className="w-6 h-6 text-red-400" />
            </div>
            <p className="text-red-400 mb-2">Failed to load reports</p>
            <p className="text-sm text-dark-500 mb-4">{error}</p>
            <button 
              onClick={() => window.location.reload()} 
              className="btn-secondary"
            >
              Retry
            </button>
          </div>
        ) : filteredReports.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredReports.map((report, index) => (
              <div key={(report as any).id || `report-${index}`} className="bg-dark-200/30 border border-dark-300/30 rounded-lg p-4 hover:border-primary-500/30 transition-all duration-300 group">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-primary-500/20 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                      <FileText className="w-5 h-5 text-primary-400" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-dark-700 text-sm">
                        {report.file_path ? report.file_path.split('/').pop()?.replace(/\.[^/.]+$/, "") : 'Unknown Report'}
                      </h4>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getReportTypeColor(report.report_type || '')}`}>
                          {getReportTypeName(report.report_type || 'unknown')}
                        </span>
                        {(report as any).job_id && (
                          <span className="text-xs text-dark-500 font-tech">
                            {(report as any).job_id.slice(0, 8)}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-1">
                    <button 
                      onClick={() => handlePreview(report as SampleReport)}
                      className="p-1.5 text-dark-400 hover:bg-dark-500/20 rounded-lg transition-colors"
                      title="Preview report"
                    >
                      <Eye className="w-3.5 h-3.5" />
                    </button>
                    <button 
                      onClick={() => handleDownload(report as SampleReport)}
                      className="p-1.5 text-primary-400 hover:bg-primary-500/20 rounded-lg transition-colors"
                      title="Download report"
                    >
                      <Download className="w-3.5 h-3.5" />
                    </button>
                    <button 
                      onClick={() => handleDeleteReport((report as any).id || `report-${index}`)}
                      className="p-1.5 text-accent-400 hover:bg-accent-500/20 rounded-lg transition-colors"
                      title="Delete report"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <div className="space-y-2 text-xs text-dark-500">
                  <div className="flex justify-between">
                    <span>Created</span>
                    <span className="font-tech">{report.created_at ? formatTimestamp(report.created_at) : 'Unknown'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Size</span>
                    <span className="font-tech">{formatBytes(report.size_bytes || 0)}</span>
                  </div>
                  {report.worksheets && (
                    <div className="flex justify-between">
                      <span>Worksheets</span>
                      <span className="font-tech">{report.worksheets.length}</span>
                    </div>
                  )}
                </div>

                {report.worksheets && (
                  <div className="mt-3 pt-3 border-t border-dark-300/30">
                    <p className="text-xs text-dark-500 mb-1">Contents:</p>
                    <div className="flex flex-wrap gap-1">
                      {report.worksheets.map((sheet, idx) => (
                        <span 
                          key={idx}
                          className="px-2 py-1 bg-dark-300/30 rounded text-xs text-dark-600"
                        >
                          {sheet}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <FileText className="w-12 h-12 text-dark-400 mx-auto mb-3" />
            <p className="text-dark-500">No reports available yet</p>
            <p className="text-sm text-dark-400 mt-1">Reports will appear here after completing analysis jobs</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Main Reports component with error boundary
const Reports: React.FC = () => {
  return (
    <ReportsErrorBoundary>
      <ReportsContent />
    </ReportsErrorBoundary>
  );
};

export default Reports;