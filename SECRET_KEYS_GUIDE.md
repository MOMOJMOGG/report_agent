# 🔐 Secret Keys Setup Guide

## What are SECRET_KEY and JWT_SECRET_KEY?

### 🔒 **SECRET_KEY**
- **Purpose**: General application security (session encryption, CSRF protection, etc.)
- **Used for**: Encrypting cookies, securing forms, general cryptographic operations
- **Length**: 50+ characters recommended
- **Characters**: Mixed alphanumeric + symbols for maximum security

### 🔑 **JWT_SECRET_KEY** 
- **Purpose**: JSON Web Token (JWT) signing and verification
- **Used for**: User authentication tokens, API security
- **Length**: 64+ characters recommended  
- **Characters**: Alphanumeric (tokens need to be URL-safe)

## 🚀 Quick Setup (Automated)

### Option 1: Use Our Generator (Recommended)
```bash
# Run the secret generator
python generate_secrets.py

# Choose option 1 to create/update .env file
# This will generate secure keys and set up your complete configuration
```

### Option 2: Manual Setup

1. **Generate keys online** (if you prefer):
   - Go to: https://randomkeygen.com/
   - Use "CodeIgniter Encryption Keys" for SECRET_KEY
   - Use "Fort Knox Passwords" for JWT_SECRET_KEY

2. **Create .env file**:
   ```bash
   cp .env.example .env  # If .env.example exists
   # OR create new .env file
   ```

3. **Add your keys to .env**:
   ```bash
   SECRET_KEY=your_generated_secret_key_here_50_chars_minimum
   JWT_SECRET_KEY=your_generated_jwt_secret_key_here_64_chars_minimum
   ```

## 📋 Complete .env File Template

```bash
# Security Configuration (CRITICAL - KEEP SECRET!)
SECRET_KEY=AbCdEf1234567890!@#$%^&*(-_=+)MixedCharsHere123
JWT_SECRET_KEY=AlphaNumer1cOnlyF0rJWT1234567890123456789012345678901234567890
JWT_EXPIRATION_HOURS=24

# OpenAI Configuration (Optional - can use mock mode)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=150
OPENAI_TEMPERATURE=0.3

# Database Configuration
DATABASE_URL=sqlite:///data/retail_data.db
DATABASE_ECHO=false

# RAG Agent Configuration
RAG_ENABLE_MOCK_MODE=false
RAG_MAX_API_CALLS_PER_SESSION=10
RAG_SIMILARITY_THRESHOLD=0.2
RAG_TOP_K_RETRIEVAL=5
RAG_CACHE_TTL_HOURS=24
RAG_ENABLE_CACHING=true

# Report Agent Configuration
REPORT_OUTPUT_DIRECTORY=output/reports
REPORT_FILE_PREFIX=retail_analysis
REPORT_INCLUDE_TIMESTAMP=true
REPORT_CREATE_CHARTS=true
REPORT_AUTO_ADJUST_COLUMNS=true

# Dashboard Agent Configuration
DASHBOARD_HOST=127.0.0.1
DASHBOARD_PORT=8000
DASHBOARD_DEBUG=false
DASHBOARD_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DASHBOARD_MAX_FILE_SIZE_MB=10

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## 🔒 Security Best Practices

### ✅ **DO:**
- ✅ Use cryptographically secure random generation
- ✅ Make keys long enough (50+ chars for SECRET_KEY, 64+ for JWT)
- ✅ Use mixed characters for SECRET_KEY (letters, numbers, symbols)
- ✅ Keep keys secret and never share them
- ✅ Use different keys for different environments (dev, staging, prod)
- ✅ Regenerate keys if compromised

### ❌ **DON'T:**
- ❌ Use simple passwords or dictionary words
- ❌ Commit .env file to git
- ❌ Share keys in chat, email, or documentation
- ❌ Use the same keys across multiple projects
- ❌ Use default or example keys in production

## 🛡️ Key Security Features

Our generated keys include:

- **Cryptographic Security**: Uses Python's `secrets` module (CSPRNG)
- **Sufficient Length**: 50+ chars for SECRET_KEY, 64+ for JWT_SECRET_KEY
- **Character Variety**: Mixed case, numbers, and symbols for maximum entropy
- **Unique Generation**: Each run produces completely different keys
- **No Patterns**: No predictable sequences or common words

## 🚨 What if I lose my keys?

### If you lose SECRET_KEY:
- Generate a new one
- Users will need to log in again
- Sessions will be invalidated

### If you lose JWT_SECRET_KEY:
- Generate a new one  
- All JWT tokens become invalid
- API authentication will reset

### Emergency Recovery:
```bash
# Generate new keys quickly
python generate_secrets.py
# Choose option 2 for just the keys
# Copy to your .env file
```

## 🔍 Verification

Check if your keys are working:

```bash
# Check your environment variables
python check_venv.py  # Shows if .env is loaded

# Test the application
python start_system.py  # Should start without key errors
```

## 🆘 Troubleshooting

### Common Issues:

1. **"No SECRET_KEY found"**:
   - Make sure .env file exists in project root
   - Check .env file has `SECRET_KEY=your_key_here`
   - Ensure no spaces around the `=` sign

2. **"JWT_SECRET_KEY missing"**:
   - Add `JWT_SECRET_KEY=your_jwt_key_here` to .env
   - Make sure it's long enough (64+ characters)

3. **Keys not loading**:
   - Restart your application after adding keys
   - Check .env file is in the correct location (project root)
   - Ensure python-dotenv is installed: `pip install python-dotenv`

4. **"Weak key" warnings**:
   - Use our generator for cryptographically secure keys
   - Avoid short keys or simple passwords

## 💡 Pro Tips

1. **Development vs Production**:
   ```bash
   # Development - can be simpler
   SECRET_KEY=dev-secret-key-not-for-production-123456789012345
   
   # Production - must be secure
   SECRET_KEY=Pr0d-S3cur3-K3y!@#$%^&*123456789MixedChars!@#$%^&*
   ```

2. **Key Rotation**:
   - Consider rotating keys periodically
   - Keep old keys for a transition period
   - Update all environments simultaneously

3. **Backup Strategy**:
   - Store keys securely (password manager, encrypted vault)
   - Don't rely on just the .env file
   - Have a key recovery plan

## 🎯 Quick Commands

```bash
# Generate secure keys automatically
python generate_secrets.py

# Check if keys are set correctly
grep "SECRET_KEY" .env
grep "JWT_SECRET_KEY" .env

# Start system (will validate keys)
python start_system.py
```

---

**Remember**: These keys are the foundation of your application's security. Take time to set them up properly! 🔐