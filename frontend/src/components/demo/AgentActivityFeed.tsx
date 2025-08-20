import React, { useState, useEffect, useRef } from 'react';
import { Clock, Bot, Database, Sparkles, Brain, FileText, Monitor, ChevronDown, ChevronUp } from 'lucide-react';

export interface AgentMessage {
  id: string;
  timestamp: Date;
  agentType: string;
  message: string;
  level: 'info' | 'success' | 'warning' | 'error';
  metadata?: Record<string, any>;
  isExpanded?: boolean;
}

interface AgentActivityFeedProps {
  messages: AgentMessage[];
  className?: string;
  maxHeight?: string;
  showTimestamps?: boolean;
  groupByAgent?: boolean;
}

const AgentActivityFeed: React.FC<AgentActivityFeedProps> = ({
  messages,
  className = '',
  maxHeight = '400px',
  showTimestamps = true,
  groupByAgent = true
}) => {
  const [expandedMessages, setExpandedMessages] = useState<Set<string>>(new Set());
  const [autoScroll, setAutoScroll] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (autoScroll && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, autoScroll]);

  // Detect manual scroll to disable auto-scroll
  const handleScroll = () => {
    if (containerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
      const isAtBottom = Math.abs(scrollHeight - clientHeight - scrollTop) < 10;
      setAutoScroll(isAtBottom);
    }
  };

  const getAgentIcon = (agentType: string) => {
    switch (agentType.toLowerCase()) {
      case 'coordinator':
        return <Bot className="w-4 h-4" />;
      case 'data_fetch':
        return <Database className="w-4 h-4" />;
      case 'normalization':
        return <Sparkles className="w-4 h-4" />;
      case 'rag':
        return <Brain className="w-4 h-4" />;
      case 'report':
        return <FileText className="w-4 h-4" />;
      case 'dashboard':
        return <Monitor className="w-4 h-4" />;
      default:
        return <Bot className="w-4 h-4" />;
    }
  };

  const getAgentColor = (agentType: string) => {
    switch (agentType.toLowerCase()) {
      case 'coordinator':
        return 'text-primary-400 bg-primary-500/10 border-primary-500/20';
      case 'data_fetch':
        return 'text-success-400 bg-success-500/10 border-success-500/20';
      case 'normalization':
        return 'text-warning-400 bg-warning-500/10 border-warning-500/20';
      case 'rag':
        return 'text-accent-400 bg-accent-500/10 border-accent-500/20';
      case 'report':
        return 'text-primary-400 bg-primary-500/10 border-primary-500/20';
      case 'dashboard':
        return 'text-dark-400 bg-dark-500/10 border-dark-500/20';
      default:
        return 'text-dark-400 bg-dark-500/10 border-dark-500/20';
    }
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'success':
        return 'text-success-400';
      case 'warning':
        return 'text-warning-400';
      case 'error':
        return 'text-red-400';
      default:
        return 'text-dark-600';
    }
  };

  const formatAgentName = (agentType: string) => {
    return agentType
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ') + ' Agent';
  };

  const toggleMessageExpansion = (messageId: string) => {
    const newExpanded = new Set(expandedMessages);
    if (newExpanded.has(messageId)) {
      newExpanded.delete(messageId);
    } else {
      newExpanded.add(messageId);
    }
    setExpandedMessages(newExpanded);
  };

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  // Group messages by agent if enabled
  const groupedMessages = groupByAgent
    ? messages.reduce((groups, message) => {
        const agent = message.agentType;
        if (!groups[agent]) groups[agent] = [];
        groups[agent].push(message);
        return groups;
      }, {} as Record<string, AgentMessage[]>)
    : null;

  return (
    <div className={`card-tech ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Bot className="w-5 h-5 text-primary-400" />
          <h3 className="text-lg font-semibold text-dark-800">Agent Activity Feed</h3>
        </div>
        <div className="flex items-center space-x-2 text-xs text-dark-500">
          <div className={`w-2 h-2 rounded-full ${autoScroll ? 'bg-success-400' : 'bg-warning-400'}`} />
          <span>{autoScroll ? 'Auto-scroll' : 'Manual scroll'}</span>
        </div>
      </div>

      <div
        ref={containerRef}
        className="space-y-1 overflow-y-auto scrollbar-thin scrollbar-track-dark-200/20 scrollbar-thumb-dark-400/40"
        style={{ maxHeight }}
        onScroll={handleScroll}
      >
        {messages.length === 0 ? (
          <div className="text-center py-8">
            <Bot className="w-12 h-12 text-dark-400 mx-auto mb-3 opacity-50" />
            <p className="text-dark-500">No agent activity yet</p>
            <p className="text-sm text-dark-400 mt-1">Messages will appear here when analysis starts</p>
          </div>
        ) : groupByAgent && groupedMessages ? (
          // Grouped by agent display
          Object.entries(groupedMessages).map(([agentType, agentMessages]) => (
            <div key={agentType} className="mb-4">
              <div className={`flex items-center space-x-2 p-2 rounded-lg border ${getAgentColor(agentType)} mb-2`}>
                {getAgentIcon(agentType)}
                <span className="font-medium text-sm">{formatAgentName(agentType)}</span>
                <span className="text-xs opacity-75">({agentMessages.length} messages)</span>
              </div>
              <div className="ml-4 space-y-1">
                {agentMessages.map((message) => (
                  <MessageEntry
                    key={message.id}
                    message={message}
                    showTimestamps={showTimestamps}
                    isExpanded={expandedMessages.has(message.id)}
                    onToggleExpansion={() => toggleMessageExpansion(message.id)}
                  />
                ))}
              </div>
            </div>
          ))
        ) : (
          // Chronological display
          messages.map((message) => (
            <div key={message.id} className="flex items-start space-x-3 p-2 rounded-lg hover:bg-dark-200/20 transition-colors">
              <div className={`flex items-center space-x-2 px-2 py-1 rounded-md border text-xs ${getAgentColor(message.agentType)}`}>
                {getAgentIcon(message.agentType)}
                <span className="font-medium">{formatAgentName(message.agentType)}</span>
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  {showTimestamps && (
                    <span className="text-xs text-dark-500 font-tech">
                      [{formatTimestamp(message.timestamp)}]
                    </span>
                  )}
                  <span className={`text-sm ${getLevelColor(message.level)}`}>
                    {message.message}
                  </span>
                  {message.metadata && Object.keys(message.metadata).length > 0 && (
                    <button
                      onClick={() => toggleMessageExpansion(message.id)}
                      className="text-dark-400 hover:text-primary-400 transition-colors"
                    >
                      {expandedMessages.has(message.id) ? 
                        <ChevronUp className="w-4 h-4" /> : 
                        <ChevronDown className="w-4 h-4" />
                      }
                    </button>
                  )}
                </div>
                
                {expandedMessages.has(message.id) && message.metadata && (
                  <div className="mt-2 p-2 bg-dark-300/20 rounded text-xs font-tech">
                    <pre className="text-dark-600 whitespace-pre-wrap">
                      {JSON.stringify(message.metadata, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {messages.length > 0 && (
        <div className="mt-4 pt-3 border-t border-dark-200/30 flex items-center justify-between text-xs text-dark-500">
          <span>{messages.length} total messages</span>
          <button
            onClick={() => {
              setAutoScroll(true);
              messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
            }}
            className="text-primary-400 hover:text-primary-300 transition-colors"
          >
            Scroll to latest
          </button>
        </div>
      )}
    </div>
  );
};

// Individual message entry component for better organization
const MessageEntry: React.FC<{
  message: AgentMessage;
  showTimestamps: boolean;
  isExpanded: boolean;
  onToggleExpansion: () => void;
}> = ({ message, showTimestamps, isExpanded, onToggleExpansion }) => {
  const getLevelColor = (level: string) => {
    switch (level) {
      case 'success':
        return 'text-success-400';
      case 'warning':
        return 'text-warning-400';
      case 'error':
        return 'text-red-400';
      default:
        return 'text-dark-600';
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <div className="p-2 rounded hover:bg-dark-200/10 transition-colors">
      <div className="flex items-center space-x-2">
        {showTimestamps && (
          <span className="text-xs text-dark-500 font-tech">
            [{formatTimestamp(message.timestamp)}]
          </span>
        )}
        <span className={`text-sm ${getLevelColor(message.level)}`}>
          {message.message}
        </span>
        {message.metadata && Object.keys(message.metadata).length > 0 && (
          <button
            onClick={onToggleExpansion}
            className="text-dark-400 hover:text-primary-400 transition-colors"
          >
            {isExpanded ? 
              <ChevronUp className="w-4 h-4" /> : 
              <ChevronDown className="w-4 h-4" />
            }
          </button>
        )}
      </div>
      
      {isExpanded && message.metadata && (
        <div className="mt-2 p-2 bg-dark-300/20 rounded text-xs font-tech">
          <pre className="text-dark-600 whitespace-pre-wrap">
            {JSON.stringify(message.metadata, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default AgentActivityFeed;