#!/bin/bash
"""
Development environment setup script for the multi-agent RAG system.
Installs dependencies, sets up database, and prepares testing environment.
"""

set -e  # Exit on any error

echo "🚀 Setting up Multi-Agent RAG Development Environment"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check Python version (require 3.8+)
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ required, but found $python_version"
    exit 1
fi

echo "✅ Python $python_version found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p data/{raw,processed,external,temp}
mkdir -p models/{trained,checkpoints,metadata}
mkdir -p experiments/{configs,results,logs}
mkdir -p output
mkdir -p logs
mkdir -p tmp

# Set up database
echo "🗄️ Setting up database..."
python3 -c "
import sys
sys.path.append('src/main/python')
from src.main.resources.config.database import db_manager
from src.main.python.utils.seed_data_generator import SeedDataGenerator

# Create tables
db_manager.create_tables()
print('Database tables created')

# Generate seed data
generator = SeedDataGenerator()
generator.generate_all_data(num_returns=1000, num_warranties=500)
print('Seed data generated')
"

# Run dependency check
echo "🔍 Checking dependencies..."
python3 scripts/run_tests.py deps

# Run basic tests
echo "🧪 Running basic tests..."
python3 scripts/run_tests.py unit

echo "✅ Development environment setup complete!"
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run tests:"
echo "  python3 scripts/run_tests.py all"
echo ""
echo "To start development:"
echo "  python3 -m src.main.python.utils.seed_data_generator  # Generate data"
echo "  python3 scripts/run_tests.py unit                     # Run unit tests"
echo "  python3 scripts/run_tests.py integration              # Run integration tests"