#!/usr/bin/env python3
"""
Quick script to check virtual environment status
"""

import os
import sys

def is_in_venv():
    """Check if we're currently running in a virtual environment."""
    return (
        hasattr(sys, 'real_prefix') or  # virtualenv
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or  # venv
        'VIRTUAL_ENV' in os.environ  # both
    )

def get_venv_info():
    """Get detailed virtual environment information."""
    if not is_in_venv():
        return None
    
    info = {}
    if 'VIRTUAL_ENV' in os.environ:
        info['path'] = os.environ['VIRTUAL_ENV']
        info['name'] = os.path.basename(os.environ['VIRTUAL_ENV'])
    else:
        info['path'] = sys.prefix
        info['name'] = 'active'
    
    info['python'] = sys.executable
    info['prefix'] = sys.prefix
    
    return info

def main():
    print("🔍 Virtual Environment Status Check")
    print("=" * 40)
    
    if is_in_venv():
        print("✅ Virtual environment is ACTIVE")
        
        info = get_venv_info()
        print(f"📁 Environment name: {info['name']}")
        print(f"📍 Environment path: {info['path']}")
        print(f"🐍 Python executable: {info['python']}")
        
        if info['name'] == 'agent':
            print("🎯 Perfect! You're in the correct 'agent' environment")
        else:
            print(f"⚠️  Note: You're in '{info['name']}' but 'agent' is recommended for this project")
    else:
        print("❌ No virtual environment detected")
        print("\n💡 To activate the virtual environment:")
        if os.name == 'nt':  # Windows
            print("   agent\\Scripts\\activate")
        else:  # Unix/Linux/Mac
            print("   source agent/bin/activate")
    
    print(f"\n📊 System Info:")
    print(f"   Python version: {sys.version.split()[0]}")
    print(f"   Platform: {sys.platform}")
    print(f"   Current directory: {os.getcwd()}")

if __name__ == "__main__":
    main()