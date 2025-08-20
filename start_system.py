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
    
    # Check if virtual environment exists
    venv_path = project_root / "agent"
    if not venv_path.exists():
        print("❌ Virtual environment 'agent' not found!")
        print("Please create it first: python -m venv agent")
        sys.exit(1)
    
    # Activate virtual environment command based on OS
    if os.name == 'nt':  # Windows
        activate_cmd = f"{venv_path}/Scripts/activate && "
    else:  # Unix/Linux/Mac
        activate_cmd = f"source {venv_path}/bin/activate && "
    
    print("📦 Installing/updating Python dependencies...")
    run_command(f"{activate_cmd}pip install -r requirements.txt", cwd=project_root)
    
    print("\n🗄️ Setting up database...")
    db_path = project_root / "data" / "retail_data.db"
    if not db_path.exists():
        print("Creating database and seeding with sample data...")
        run_command(f"{activate_cmd}python src/main/python/utils/seed_data_generator.py", cwd=project_root)
    
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