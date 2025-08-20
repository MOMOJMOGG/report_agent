#!/usr/bin/env python3
"""
Test runner script for the multi-agent RAG system.
Provides comprehensive testing capabilities with proper setup.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src" / "main" / "python"))
sys.path.insert(0, str(project_root / "src"))

def setup_environment():
    """Set up the testing environment."""
    # Set environment variables for testing
    os.environ["DATABASE_URL"] = "sqlite:///test_data.db"
    os.environ["TESTING"] = "true"
    
    # Create necessary directories
    test_dirs = [
        project_root / "data",
        project_root / "output",
        project_root / "logs",
        project_root / "tmp"
    ]
    
    for test_dir in test_dirs:
        test_dir.mkdir(exist_ok=True)

def run_unit_tests():
    """Run unit tests."""
    print("Running unit tests...")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "src/test/unit/",
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    return subprocess.run(cmd, cwd=project_root).returncode

def run_integration_tests():
    """Run integration tests."""
    print("Running integration tests...")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "src/test/integration/",
        "-v",
        "--tb=short",
        "--color=yes",
        "-m", "integration"
    ]
    
    return subprocess.run(cmd, cwd=project_root).returncode

def run_all_tests():
    """Run all tests."""
    print("Running all tests...")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "src/test/",
        "-v",
        "--tb=short",
        "--color=yes",
        "--cov=src/main/python",
        "--cov-report=term-missing",
        "--cov-report=html:output/coverage_html"
    ]
    
    return subprocess.run(cmd, cwd=project_root).returncode

def run_specific_test(test_path):
    """Run a specific test file or test function."""
    print(f"Running specific test: {test_path}")
    
    cmd = [
        sys.executable, "-m", "pytest",
        test_path,
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    return subprocess.run(cmd, cwd=project_root).returncode

def check_dependencies():
    """Check if required testing dependencies are installed."""
    required_packages = [
        "pytest",
        "pytest-asyncio",
        "sqlalchemy",
        "faker"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        
        print("\nInstall missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def generate_test_data():
    """Generate test data for testing."""
    print("Generating test data...")
    
    try:
        from src.main.python.utils.seed_data_generator import SeedDataGenerator
        
        generator = SeedDataGenerator()
        generator.generate_all_data(num_returns=100, num_warranties=50)
        
        print("Test data generated successfully!")
        return True
        
    except Exception as e:
        print(f"Failed to generate test data: {e}")
        return False

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Multi-Agent RAG Test Runner")
    parser.add_argument(
        "command",
        choices=["unit", "integration", "all", "specific", "setup", "deps"],
        help="Test command to run"
    )
    parser.add_argument(
        "--test-path",
        help="Specific test path (for 'specific' command)"
    )
    parser.add_argument(
        "--generate-data",
        action="store_true",
        help="Generate test data before running tests"
    )
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    if args.command == "deps":
        if check_dependencies():
            print("All dependencies are installed!")
            return 0
        else:
            return 1
    
    if args.command == "setup":
        if generate_test_data():
            print("Test environment setup complete!")
            return 0
        else:
            return 1
    
    # Check dependencies before running tests
    if not check_dependencies():
        print("Please install missing dependencies before running tests.")
        return 1
    
    # Generate test data if requested
    if args.generate_data:
        if not generate_test_data():
            print("Failed to generate test data. Continuing anyway...")
    
    # Run tests based on command
    exit_code = 0
    
    if args.command == "unit":
        exit_code = run_unit_tests()
    elif args.command == "integration":
        exit_code = run_integration_tests()
    elif args.command == "all":
        exit_code = run_all_tests()
    elif args.command == "specific":
        if not args.test_path:
            print("--test-path required for 'specific' command")
            return 1
        exit_code = run_specific_test(args.test_path)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())