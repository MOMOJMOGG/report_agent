#!/usr/bin/env python3
"""
Dashboard Server Runner
Starts the Dashboard Agent REST API server.
"""

import asyncio
import sys
import signal
from pathlib import Path

# Add src to path
sys.path.append('src/main/python')

from agents.dashboard_agent import DashboardAgent, DashboardConfig
from config.settings import settings


async def main():
    """Main function to run the dashboard server."""
    
    # Create dashboard configuration
    dashboard_config = DashboardConfig(
        host=settings.dashboard.host,
        port=settings.dashboard.port,
        debug=settings.dashboard.debug,
        cors_origins=settings.dashboard.cors_origins,
        max_file_size_mb=settings.dashboard.max_file_size_mb
    )
    
    # Create and start dashboard agent
    agent = DashboardAgent(dashboard_config=dashboard_config)
    
    print(f"🚀 Starting Retail Analysis Dashboard API...")
    print(f"📊 Server will be available at: http://{dashboard_config.host}:{dashboard_config.port}")
    print(f"📋 API documentation at: http://{dashboard_config.host}:{dashboard_config.port}/docs")
    print(f"🔧 Health check at: http://{dashboard_config.host}:{dashboard_config.port}/health")
    
    try:
        # Start the agent
        await agent._on_start()
        
        # Run the server
        await agent.start_server_async()
        
    except KeyboardInterrupt:
        print("\n⏹️  Shutting down dashboard server...")
    except Exception as e:
        print(f"❌ Error running dashboard server: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await agent._on_stop()
        print("✅ Dashboard server stopped")


def run_sync():
    """Synchronous entry point for running the dashboard."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Dashboard stopped by user")


if __name__ == "__main__":
    run_sync()