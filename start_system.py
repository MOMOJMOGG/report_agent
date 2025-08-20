#!/usr/bin/env python3
"""
Complete Multi-Agent RAG System Startup Script
Starts both the FastAPI backend and React frontend dashboard.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def is_in_venv():
    """Check if we're currently running in a virtual environment."""
    return (
        hasattr(sys, 'real_prefix') or  # virtualenv
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or  # venv
        'VIRTUAL_ENV' in os.environ  # both
    )

def get_venv_name():
    """Get the name of the current virtual environment."""
    if 'VIRTUAL_ENV' in os.environ:
        return os.path.basename(os.environ['VIRTUAL_ENV'])
    return None

def run_command(cmd, cwd=None, background=False):
    """Run a command with optional working directory."""
    print(f"Running: {cmd}")
    if background:
        return subprocess.Popen(cmd, shell=True, cwd=cwd)
    else:
        return subprocess.run(cmd, shell=True, cwd=cwd)

def main():
    print("🚀 Starting Multi-Agent RAG System")
    print("=" * 50)
    
    # Get project root
    project_root = Path(__file__).parent
    
    # Check virtual environment status
    if is_in_venv():
        venv_name = get_venv_name()
        print(f"✅ Virtual environment detected: {venv_name or 'active'}")
        
        # Check if we're in the expected 'agent' venv
        if venv_name and venv_name != 'agent':
            print(f"⚠️  Warning: You're in '{venv_name}' venv, but 'agent' is recommended")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                print("Please activate the 'agent' virtual environment and try again")
                sys.exit(1)
        
        # No activation needed - we're already in venv
        activate_cmd = ""
    else:
        print("❌ No virtual environment detected!")
        
        # Check if 'agent' venv exists
        venv_path = project_root / "agent"
        if not venv_path.exists():
            print("Virtual environment 'agent' not found!")
            print("Please create and activate it first:")
            print("  python -m venv agent")
            if os.name == 'nt':
                print("  agent\\Scripts\\activate")
            else:
                print("  source agent/bin/activate")
            print("  python start_system.py")
            sys.exit(1)
        else:
            print("Virtual environment 'agent' exists but not activated!")
            print("Please activate it first:")
            if os.name == 'nt':
                print("  agent\\Scripts\\activate")
            else:
                print("  source agent/bin/activate")
            print("  python start_system.py")
            sys.exit(1)
    
    print("📦 Installing/updating Python dependencies...")
    run_command(f"{activate_cmd}pip install -r requirements.txt", cwd=project_root)
    
    print("\n🗄️ Setting up database...")
    db_path = project_root / "data" / "retail_data.db"
    if not db_path.exists():
        print("Creating database and seeding with sample data...")
        run_command(f"{activate_cmd}python -m multi_agent.utils.seed_data_generator", cwd=project_root)
    
    print("\n🔧 Starting FastAPI Backend Server...")
    backend_process = run_command(
        f"{activate_cmd}python run_dashboard.py", 
        cwd=project_root, 
        background=True
    )
    
    # Wait for backend to start
    print("⏳ Waiting for backend to initialize...")
    time.sleep(5)
    
    # Check if frontend exists
    frontend_path = project_root / "frontend"
    if frontend_path.exists():
        print("\n🎨 Starting React Frontend Dashboard...")
        
        # Check if node_modules exists
        node_modules = frontend_path / "node_modules"
        if not node_modules.exists():
            print("📦 Installing frontend dependencies...")
            run_command("npm install", cwd=frontend_path)
        
        print("🌐 Starting development server...")
        frontend_process = run_command(
            "npm run dev", 
            cwd=frontend_path, 
            background=True
        )
        
        print("\n✅ System Started Successfully!")
        print("=" * 50)
        print("🔗 Backend API: http://127.0.0.1:8000")
        print("🔗 API Docs: http://127.0.0.1:8000/docs")
        print("🔗 Frontend Dashboard: http://localhost:3000")
        print("=" * 50)
        print("\n📋 Available Features:")
        print("• Real-time job monitoring and analytics")
        print("• Multi-agent pipeline orchestration")
        print("• Excel report generation")
        print("• Interactive data visualizations")
        print("• System health monitoring")
        print("\n💡 Quick Start:")
        print("1. Open the dashboard at http://localhost:3000")
        print("2. Click 'Quick Analysis' to start your first job")
        print("3. Monitor progress in real-time")
        print("4. Download reports when complete")
        
        try:
            print("\n⌨️  Press Ctrl+C to stop all services")
            # Keep both processes running
            backend_process.wait()
            frontend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping services...")
            backend_process.terminate()
            if 'frontend_process' in locals():
                frontend_process.terminate()
            print("✅ All services stopped")
    
    else:
        print("\n⚠️  Frontend not found, running backend only")
        print("🔗 Backend API: http://127.0.0.1:8000")
        print("🔗 API Docs: http://127.0.0.1:8000/docs")
        
        try:
            print("\n⌨️  Press Ctrl+C to stop backend service")
            backend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping backend...")
            backend_process.terminate()
            print("✅ Backend stopped")

if __name__ == "__main__":
    main()