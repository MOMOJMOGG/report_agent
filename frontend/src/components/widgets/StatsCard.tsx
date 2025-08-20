import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: string | number;
  change?: string;
  changeType?: 'increase' | 'decrease' | 'neutral';
  icon: LucideIcon;
  color?: 'primary' | 'success' | 'warning' | 'accent';
}

const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  change,
  changeType = 'neutral',
  icon: Icon,
  color = 'primary'
}) => {
  const getColorClasses = () => {
    switch (color) {
      case 'success':
        return 'from-success-500 to-success-600 shadow-success-500/25';
      case 'warning':
        return 'from-warning-500 to-warning-600 shadow-warning-500/25';
      case 'accent':
        return 'from-accent-500 to-accent-600 shadow-accent-500/25';
      default:
        return 'from-primary-500 to-primary-600 shadow-primary-500/25';
    }
  };

  const getChangeColor = () => {
    switch (changeType) {
      case 'increase':
        return 'text-success-400';
      case 'decrease':
        return 'text-accent-400';
      default:
        return 'text-dark-500';
    }
  };

  return (
    <div className="card-tech group hover:scale-105 transition-all duration-300">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-dark-500 mb-1">{title}</p>
          <p className="text-2xl font-bold text-dark-800 mb-2">{value}</p>
          {change && (
            <p className={`text-xs ${getChangeColor()}`}>
              {change}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-xl bg-gradient-to-br ${getColorClasses()} group-hover:scale-110 transition-transform duration-300`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );
};

export default StatsCard;