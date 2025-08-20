import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import { Menu, X } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="flex h-screen bg-dark-50 overflow-hidden">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`
          fixed inset-y-0 left-0 z-50 w-64 transform bg-dark-100/50 backdrop-blur-xl border-r border-dark-200/30
          transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <Sidebar onClose={() => setSidebarOpen(false)} />
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <Header 
          onMenuClick={() => setSidebarOpen(true)}
          pageTitle={getPageTitle(location.pathname)}
        />

        {/* Page content */}
        <main className="flex-1 overflow-auto bg-grid-pattern">
          <div className="h-full p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

const getPageTitle = (pathname: string): string => {
  const titles: Record<string, string> = {
    '/': 'Dashboard',
    '/analytics': 'Analytics',
    '/jobs': 'Jobs',
    '/reports': 'Reports',
    '/settings': 'Settings',
  };
  return titles[pathname] || 'Dashboard';
};

export default Layout;