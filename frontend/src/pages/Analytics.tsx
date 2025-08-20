import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, TrendingDown, Activity, Clock } from 'lucide-react';

const Analytics: React.FC = () => {
  // Mock data for charts
  const jobTrendData = [
    { name: 'Mon', jobs: 12, success: 10, failed: 2 },
    { name: 'Tue', jobs: 19, success: 17, failed: 2 },
    { name: 'Wed', jobs: 8, success: 8, failed: 0 },
    { name: 'Thu', jobs: 15, success: 13, failed: 2 },
    { name: 'Fri', jobs: 23, success: 21, failed: 2 },
    { name: 'Sat', jobs: 6, success: 6, failed: 0 },
    { name: 'Sun', jobs: 4, success: 4, failed: 0 },
  ];

  const agentPerformanceData = [
    { name: 'Data Fetch', value: 95, color: '#0ea5e9' },
    { name: 'Normalization', value: 92, color: '#22c55e' },
    { name: 'RAG', value: 88, color: '#f59e0b' },
    { name: 'Report', value: 96, color: '#ef4444' },
    { name: 'Dashboard', value: 99, color: '#8b5cf6' },
  ];

  const executionTimeData = [
    { time: '00:00', avg: 45 },
    { time: '04:00', avg: 32 },
    { time: '08:00', avg: 67 },
    { time: '12:00', avg: 89 },
    { time: '16:00', avg: 95 },
    { time: '20:00', avg: 56 },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-dark-800">Analytics Dashboard</h2>
        <p className="text-dark-500 mt-1">Deep insights into your multi-agent system performance</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card-tech text-center">
          <div className="w-12 h-12 bg-primary-500/20 rounded-xl flex items-center justify-center mx-auto mb-3">
            <Activity className="w-6 h-6 text-primary-400" />
          </div>
          <p className="text-2xl font-bold text-dark-800">87</p>
          <p className="text-sm text-dark-500">Total Jobs This Week</p>
          <div className="flex items-center justify-center mt-2 text-success-400 text-sm">
            <TrendingUp className="w-4 h-4 mr-1" />
            +12% from last week
          </div>
        </div>

        <div className="card-tech text-center">
          <div className="w-12 h-12 bg-success-500/20 rounded-xl flex items-center justify-center mx-auto mb-3">
            <TrendingUp className="w-6 h-6 text-success-400" />
          </div>
          <p className="text-2xl font-bold text-dark-800">94.2%</p>
          <p className="text-sm text-dark-500">Success Rate</p>
          <div className="flex items-center justify-center mt-2 text-success-400 text-sm">
            <TrendingUp className="w-4 h-4 mr-1" />
            +2.1% improvement
          </div>
        </div>

        <div className="card-tech text-center">
          <div className="w-12 h-12 bg-warning-500/20 rounded-xl flex items-center justify-center mx-auto mb-3">
            <Clock className="w-6 h-6 text-warning-400" />
          </div>
          <p className="text-2xl font-bold text-dark-800">67s</p>
          <p className="text-sm text-dark-500">Avg Execution Time</p>
          <div className="flex items-center justify-center mt-2 text-accent-400 text-sm">
            <TrendingDown className="w-4 h-4 mr-1" />
            +8s slower
          </div>
        </div>

        <div className="card-tech text-center">
          <div className="w-12 h-12 bg-accent-500/20 rounded-xl flex items-center justify-center mx-auto mb-3">
            <Activity className="w-6 h-6 text-accent-400" />
          </div>
          <p className="text-2xl font-bold text-dark-800">5</p>
          <p className="text-sm text-dark-500">Failed Jobs</p>
          <div className="flex items-center justify-center mt-2 text-success-400 text-sm">
            <TrendingDown className="w-4 h-4 mr-1" />
            -3 from last week
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Job Trends */}
        <div className="card-tech">
          <h3 className="text-lg font-semibold text-dark-800 mb-4">Weekly Job Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={jobTrendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
              <XAxis dataKey="name" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#27272a', 
                  border: '1px solid #3f3f46',
                  borderRadius: '8px',
                  color: '#d4d4d8'
                }} 
              />
              <Bar dataKey="success" fill="#22c55e" radius={[4, 4, 0, 0]} />
              <Bar dataKey="failed" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Agent Performance */}
        <div className="card-tech">
          <h3 className="text-lg font-semibold text-dark-800 mb-4">Agent Performance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={agentPerformanceData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
              >
                {agentPerformanceData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#27272a', 
                  border: '1px solid #3f3f46',
                  borderRadius: '8px',
                  color: '#d4d4d8'
                }} 
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="grid grid-cols-2 gap-2 mt-4">
            {agentPerformanceData.map((agent, index) => (
              <div key={index} className="flex items-center space-x-2">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: agent.color }}
                />
                <span className="text-sm text-dark-600">{agent.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Execution Time Trends */}
      <div className="card-tech">
        <h3 className="text-lg font-semibold text-dark-800 mb-4">Execution Time Trends (24h)</h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={executionTimeData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
            <XAxis dataKey="time" stroke="#6b7280" />
            <YAxis stroke="#6b7280" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#27272a', 
                border: '1px solid #3f3f46',
                borderRadius: '8px',
                color: '#d4d4d8'
              }} 
            />
            <Line 
              type="monotone" 
              dataKey="avg" 
              stroke="#0ea5e9" 
              strokeWidth={3}
              dot={{ fill: '#0ea5e9', strokeWidth: 2, r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default Analytics;