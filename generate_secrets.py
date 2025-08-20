#!/usr/bin/env python3
"""
Generate secure secret keys for the Multi-Agent RAG System
Creates strong SECRET_KEY and JWT_SECRET_KEY values for production use.
"""

import secrets
import string
from pathlib import Path
import os

def generate_secret_key(length=50):
    """Generate a cryptographically secure secret key."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_jwt_secret(length=64):
    """Generate a secure JWT secret key (longer for JWT)."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_env_file():
    """Create or update .env file with secure keys."""
    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    # Generate secure keys
    secret_key = generate_secret_key()
    jwt_secret = generate_jwt_secret()
    
    print("🔐 Generating Secure Secret Keys")
    print("=" * 50)
    print(f"📊 SECRET_KEY: {len(secret_key)} characters")
    print(f"🔑 JWT_SECRET_KEY: {len(jwt_secret)} characters")
    print()
    
    # Read existing .env or create from .env.example
    env_content = {}
    
    if env_file.exists():
        print("📝 Found existing .env file - updating keys only...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_content[key] = value
    elif env_example.exists():
        print("📝 Creating .env from .env.example template...")
        with open(env_example, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_content[key] = value
    else:
        print("📝 Creating new .env file with default settings...")
        # Default configuration
        env_content = {
            'DATABASE_URL': 'sqlite:///data/retail_data.db',
            'DATABASE_ECHO': 'false',
            'OPENAI_API_KEY': 'your_openai_api_key_here',
            'OPENAI_MODEL': 'gpt-3.5-turbo',
            'OPENAI_MAX_TOKENS': '150',
            'OPENAI_TEMPERATURE': '0.3',
            'RAG_ENABLE_MOCK_MODE': 'false',
            'RAG_MAX_API_CALLS_PER_SESSION': '10',
            'RAG_SIMILARITY_THRESHOLD': '0.2',
            'RAG_TOP_K_RETRIEVAL': '5',
            'RAG_CACHE_TTL_HOURS': '24',
            'RAG_ENABLE_CACHING': 'true',
            'REPORT_OUTPUT_DIRECTORY': 'output/reports',
            'REPORT_FILE_PREFIX': 'retail_analysis',
            'REPORT_INCLUDE_TIMESTAMP': 'true',
            'REPORT_CREATE_CHARTS': 'true',
            'REPORT_AUTO_ADJUST_COLUMNS': 'true',
            'DASHBOARD_HOST': '127.0.0.1',
            'DASHBOARD_PORT': '8000',
            'DASHBOARD_DEBUG': 'false',
            'DASHBOARD_CORS_ORIGINS': 'http://localhost:3000,http://127.0.0.1:3000',
            'DASHBOARD_MAX_FILE_SIZE_MB': '10',
            'JWT_EXPIRATION_HOURS': '24',
            'LOG_LEVEL': 'INFO',
            'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    
    # Update with new secure keys
    env_content['SECRET_KEY'] = secret_key
    env_content['JWT_SECRET_KEY'] = jwt_secret
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write("# Multi-Agent RAG System Configuration\n")
        f.write("# Generated automatically - DO NOT COMMIT TO GIT!\n\n")
        
        f.write("# Security Configuration (CRITICAL - KEEP SECRET!)\n")
        f.write(f"SECRET_KEY={env_content['SECRET_KEY']}\n")
        f.write(f"JWT_SECRET_KEY={env_content['JWT_SECRET_KEY']}\n")
        f.write(f"JWT_EXPIRATION_HOURS={env_content.get('JWT_EXPIRATION_HOURS', '24')}\n\n")
        
        f.write("# OpenAI Configuration\n")
        f.write(f"OPENAI_API_KEY={env_content.get('OPENAI_API_KEY', 'your_openai_api_key_here')}\n")
        f.write(f"OPENAI_MODEL={env_content.get('OPENAI_MODEL', 'gpt-3.5-turbo')}\n")
        f.write(f"OPENAI_MAX_TOKENS={env_content.get('OPENAI_MAX_TOKENS', '150')}\n")
        f.write(f"OPENAI_TEMPERATURE={env_content.get('OPENAI_TEMPERATURE', '0.3')}\n\n")
        
        f.write("# Database Configuration\n")
        f.write(f"DATABASE_URL={env_content.get('DATABASE_URL', 'sqlite:///data/retail_data.db')}\n")
        f.write(f"DATABASE_ECHO={env_content.get('DATABASE_ECHO', 'false')}\n\n")
        
        f.write("# RAG Agent Configuration\n")
        f.write(f"RAG_ENABLE_MOCK_MODE={env_content.get('RAG_ENABLE_MOCK_MODE', 'false')}\n")
        f.write(f"RAG_MAX_API_CALLS_PER_SESSION={env_content.get('RAG_MAX_API_CALLS_PER_SESSION', '10')}\n")
        f.write(f"RAG_SIMILARITY_THRESHOLD={env_content.get('RAG_SIMILARITY_THRESHOLD', '0.2')}\n")
        f.write(f"RAG_TOP_K_RETRIEVAL={env_content.get('RAG_TOP_K_RETRIEVAL', '5')}\n")
        f.write(f"RAG_CACHE_TTL_HOURS={env_content.get('RAG_CACHE_TTL_HOURS', '24')}\n")
        f.write(f"RAG_ENABLE_CACHING={env_content.get('RAG_ENABLE_CACHING', 'true')}\n\n")
        
        f.write("# Report Agent Configuration\n")
        f.write(f"REPORT_OUTPUT_DIRECTORY={env_content.get('REPORT_OUTPUT_DIRECTORY', 'output/reports')}\n")
        f.write(f"REPORT_FILE_PREFIX={env_content.get('REPORT_FILE_PREFIX', 'retail_analysis')}\n")
        f.write(f"REPORT_INCLUDE_TIMESTAMP={env_content.get('REPORT_INCLUDE_TIMESTAMP', 'true')}\n")
        f.write(f"REPORT_CREATE_CHARTS={env_content.get('REPORT_CREATE_CHARTS', 'true')}\n")
        f.write(f"REPORT_AUTO_ADJUST_COLUMNS={env_content.get('REPORT_AUTO_ADJUST_COLUMNS', 'true')}\n\n")
        
        f.write("# Dashboard Agent Configuration\n")
        f.write(f"DASHBOARD_HOST={env_content.get('DASHBOARD_HOST', '127.0.0.1')}\n")
        f.write(f"DASHBOARD_PORT={env_content.get('DASHBOARD_PORT', '8000')}\n")
        f.write(f"DASHBOARD_DEBUG={env_content.get('DASHBOARD_DEBUG', 'false')}\n")
        f.write(f"DASHBOARD_CORS_ORIGINS={env_content.get('DASHBOARD_CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000')}\n")
        f.write(f"DASHBOARD_MAX_FILE_SIZE_MB={env_content.get('DASHBOARD_MAX_FILE_SIZE_MB', '10')}\n\n")
        
        f.write("# Logging Configuration\n")
        f.write(f"LOG_LEVEL={env_content.get('LOG_LEVEL', 'INFO')}\n")
        f.write(f"LOG_FORMAT={env_content.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')}\n")
    
    print(f"✅ Created/Updated: {env_file}")
    print()
    print("🔒 Security Notes:")
    print("   • Keys are cryptographically secure")
    print("   • SECRET_KEY: Used for general application security")
    print("   • JWT_SECRET_KEY: Used for JSON Web Token signing")
    print("   • These keys are unique to your installation")
    print()
    print("⚠️  IMPORTANT:")
    print("   • Never commit .env file to git!")
    print("   • Keep these keys secret and secure")
    print("   • Regenerate keys if compromised")
    print()
    print("📋 Next Steps:")
    print("   1. Add your OpenAI API key if you have one")
    print("   2. Run: python start_system.py")
    print("   3. Your system will use these secure keys automatically")

def show_keys_only():
    """Just generate and display keys without creating files."""
    secret_key = generate_secret_key()
    jwt_secret = generate_jwt_secret()
    
    print("🔐 Generated Secret Keys")
    print("=" * 50)
    print("Copy these values to your .env file:")
    print()
    print(f"SECRET_KEY={secret_key}")
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print()
    print("🔒 Security Features:")
    print(f"   • SECRET_KEY: {len(secret_key)} characters, mixed alphanumeric + symbols")
    print(f"   • JWT_SECRET_KEY: {len(jwt_secret)} characters, alphanumeric")
    print("   • Cryptographically secure random generation")

def main():
    print("🔐 Multi-Agent RAG System - Secret Key Generator")
    print("=" * 60)
    print()
    print("Choose an option:")
    print("1. Create/update .env file with secure keys (Recommended)")
    print("2. Just show me the generated keys")
    print("3. Exit")
    print()
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == '1':
        create_env_file()
    elif choice == '2':
        show_keys_only()
    elif choice == '3':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice. Please run again.")

if __name__ == "__main__":
    main()