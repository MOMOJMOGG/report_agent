import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from '@/components/Layout';
import Dashboard from '@/pages/Dashboard';
import Analytics from '@/pages/Analytics';
import Jobs from '@/pages/Jobs';
import Reports from '@/pages/Reports';
import Settings from '@/pages/Settings';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-dark-50 text-dark-900">
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#27272a',
              color: '#d4d4d8',
              border: '1px solid #3f3f46',
            },
            success: {
              iconTheme: {
                primary: '#22c55e',
                secondary: '#27272a',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#27272a',
              },
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App;