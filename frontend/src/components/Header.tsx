import React from 'react';
import { Bell, Search, User, Menu, RefreshCw } from 'lucide-react';
import { useHealth } from '@/hooks/useApi';
import { formatRelativeTime } from '@/utils/formatters';

interface HeaderProps {
  onMenuClick: () => void;
  pageTitle: string;
}

const Header: React.FC<HeaderProps> = ({ onMenuClick, pageTitle }) => {
  const { health, loading, refresh } = useHealth();

  return (
    <header className="flex items-center justify-between px-6 py-4 bg-dark-100/30 backdrop-blur-xl border-b border-dark-200/30">
      {/* Left side */}
      <div className="flex items-center space-x-4">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-md text-dark-400 hover:text-dark-600 hover:bg-dark-200/30 transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>
        
        <div>
          <h1 className="text-xl font-semibold text-dark-800">{pageTitle}</h1>
          <p className="text-sm text-dark-500">
            Multi-Agent RAG System - {health ? formatRelativeTime(health.timestamp) : 'Loading...'}
          </p>
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center space-x-4">
        {/* Search */}
        <div className="hidden md:flex items-center space-x-2 bg-dark-200/30 rounded-lg px-3 py-2 w-64">
          <Search className="w-4 h-4 text-dark-400" />
          <input
            type="text"
            placeholder="Search jobs, reports..."
            className="bg-transparent border-none outline-none text-sm text-dark-700 placeholder-dark-400 flex-1"
          />
        </div>

        {/* Health status */}
        <div className="flex items-center space-x-2">
          <button
            onClick={refresh}
            disabled={loading}
            className="p-2 rounded-lg text-dark-400 hover:text-primary-400 hover:bg-primary-500/10 transition-all duration-200 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          
          {health && (
            <div className="flex items-center space-x-2 px-3 py-1 rounded-lg bg-success-500/10 border border-success-500/20">
              <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
              <span className="text-xs font-medium text-success-400">
                {health.active_jobs} Active
              </span>
            </div>
          )}
        </div>

        {/* Notifications */}
        <button className="relative p-2 rounded-lg text-dark-400 hover:text-warning-400 hover:bg-warning-500/10 transition-all duration-200">
          <Bell className="w-5 h-5" />
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-warning-500 rounded-full flex items-center justify-center">
            <span className="text-xs font-bold text-white">3</span>
          </div>
        </button>

        {/* User menu */}
        <button className="flex items-center space-x-2 p-2 rounded-lg text-dark-400 hover:text-dark-600 hover:bg-dark-200/30 transition-all duration-200">
          <div className="w-8 h-8 bg-gradient-tech from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
          <span className="hidden md:block text-sm font-medium text-dark-600">Admin</span>
        </button>
      </div>
    </header>
  );
};

export default Header;