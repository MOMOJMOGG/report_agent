import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  BarChart3, 
  Brain, 
  FileText, 
  Briefcase, 
  Settings, 
  Activity,
  Database,
  Zap,
  X
} from 'lucide-react';

interface SidebarProps {
  onClose: () => void;
}

const navigation = [
  { name: 'Dashboard', href: '/', icon: BarChart3 },
  { name: 'Analytics', href: '/analytics', icon: Activity },
  { name: 'Jobs', href: '/jobs', icon: Briefcase },
  { name: 'Reports', href: '/reports', icon: FileText },
  { name: 'Settings', href: '/settings', icon: Settings },
];

const Sidebar: React.FC<SidebarProps> = ({ onClose }) => {
  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-dark-200/30">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className="w-8 h-8 bg-gradient-tech from-primary-500 to-primary-600 rounded-lg flex items-center justify-center shadow-lg shadow-primary-500/25">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-success-500 rounded-full animate-pulse-tech"></div>
          </div>
          <div>
            <h2 className="text-sm font-semibold text-dark-800 font-tech">Multi-Agent</h2>
            <p className="text-xs text-dark-500">RAG Dashboard</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="lg:hidden p-1 rounded-md text-dark-400 hover:text-dark-600 hover:bg-dark-200/30 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* System Status */}
      <div className="p-4 border-b border-dark-200/30">
        <div className="bg-dark-200/30 rounded-lg p-3 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-dark-500">System Status</span>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
              <span className="text-success-400 font-medium">Online</span>
            </div>
          </div>
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2">
                <Database className="w-3 h-3 text-primary-400" />
                <span className="text-dark-600">Database</span>
              </div>
              <span className="text-success-400">Connected</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2">
                <Zap className="w-3 h-3 text-warning-400" />
                <span className="text-dark-600">Agents</span>
              </div>
              <span className="text-success-400">5 Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `nav-item group ${isActive ? 'active' : ''}`
            }
            onClick={onClose}
          >
            <item.icon className="w-5 h-5 group-hover:scale-110 transition-transform duration-200" />
            <span className="font-medium">{item.name}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-dark-200/30">
        <div className="text-xs text-dark-400 space-y-1">
          <div className="flex justify-between">
            <span>Version</span>
            <span className="font-tech">1.0.0</span>
          </div>
          <div className="flex justify-between">
            <span>Uptime</span>
            <span className="font-tech text-success-400">2h 15m</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;