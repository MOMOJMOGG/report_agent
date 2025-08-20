import React from 'react';
import { Download, FileText, Calendar, HardDrive } from 'lucide-react';
import { useReports } from '@/hooks/useApi';
import { formatTimestamp, formatBytes } from '@/utils/formatters';

const Reports: React.FC = () => {
  const { reports, loading } = useReports();

  const handleDownload = (filename: string) => {
    // Create download link
    const link = document.createElement('a');
    link.href = `/api/v1/reports/${filename}/download`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-dark-800">Reports</h2>
        <p className="text-dark-500 mt-1">Download and manage your analysis reports</p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card-tech text-center">
          <div className="w-12 h-12 bg-primary-500/20 rounded-xl flex items-center justify-center mx-auto mb-3">
            <FileText className="w-6 h-6 text-primary-400" />
          </div>
          <p className="text-2xl font-bold text-dark-800">{reports.length}</p>
          <p className="text-sm text-dark-500">Total Reports</p>
        </div>

        <div className="card-tech text-center">
          <div className="w-12 h-12 bg-success-500/20 rounded-xl flex items-center justify-center mx-auto mb-3">
            <Calendar className="w-6 h-6 text-success-400" />
          </div>
          <p className="text-2xl font-bold text-dark-800">
            {reports.filter(r => {
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
            {formatBytes(reports.reduce((total, report) => total + report.size_bytes, 0))}
          </p>
          <p className="text-sm text-dark-500">Total Size</p>
        </div>
      </div>

      {/* Reports List */}
      <div className="card-tech">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-dark-800">Available Reports</h3>
          <span className="text-sm text-dark-500">{reports.length} reports</span>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
          </div>
        ) : reports.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {reports.map((report, index) => (
              <div key={index} className="bg-dark-200/30 border border-dark-300/30 rounded-lg p-4 hover:border-primary-500/30 transition-all duration-300 group">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-primary-500/20 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                      <FileText className="w-5 h-5 text-primary-400" />
                    </div>
                    <div>
                      <h4 className="font-medium text-dark-700 text-sm">
                        {report.file_path.split('/').pop()?.replace(/\.[^/.]+$/, "")}
                      </h4>
                      <p className="text-xs text-dark-500">{report.report_type}</p>
                    </div>
                  </div>
                  <button 
                    onClick={() => handleDownload(report.file_path.split('/').pop() || '')}
                    className="p-2 text-primary-400 hover:bg-primary-500/20 rounded-lg transition-colors"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </div>

                <div className="space-y-2 text-xs text-dark-500">
                  <div className="flex justify-between">
                    <span>Created</span>
                    <span className="font-tech">{formatTimestamp(report.created_at)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Size</span>
                    <span className="font-tech">{formatBytes(report.size_bytes)}</span>
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

export default Reports;