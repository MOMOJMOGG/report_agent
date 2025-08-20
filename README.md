# Multi-Agent RAG System 🤖

**Advanced Retail Analytics with Multi-Agent Architecture & Dark Technology Dashboard**

A sophisticated AI system that orchestrates multiple specialized agents to process retail returns & warranty data, generating comprehensive Excel reports and interactive web dashboards with real-time analytics and grounded insights.

## 🚀 Quick Start

### Option 1: Complete System (Recommended)
```bash
# Clone and setup
git clone [repository-url]
cd multi_agent

# Create virtual environment
python -m venv agent
source agent/bin/activate  # Linux/Mac
# OR
agent\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Start complete system (Backend + Frontend)
python start_system.py
```

### Option 2: Backend Only
```bash
# Start FastAPI backend server
python run_dashboard.py

# Access API at http://127.0.0.1:8000
# API docs at http://127.0.0.1:8000/docs
```

### Option 3: Development Mode
```bash
# Backend in one terminal
python run_dashboard.py

# Frontend in another terminal  
cd frontend
npm install
npm run dev

# Dashboard at http://localhost:3000
```

## Multi-Agent Architecture Overview

This system implements a multi-agent RAG (Retrieval-Augmented Generation) pipeline:

- **Data Fetch Agent**: Connects to retail database, extracts returns & warranty data
- **Normalization Agent**: Cleans and structures raw data for analysis
- **RAG Agent**: Generates grounded insights with citations from processed data
- **Report Agent**: Creates Excel reports with formatted data and insights
- **Dashboard Agent**: Builds web dashboards with interactive visualizations
- **Coordinator Agent**: Orchestrates the entire pipeline and manages agent communication

## AI/ML Project Structure

**Complete MLOps-ready structure with data, models, experiments support**

```
report_multi_agent/
├── src/main/python/        # Core application code
│   ├── core/               # Multi-agent coordination logic
│   ├── services/           # RAG pipeline services
│   ├── models/             # Agent definitions & data models
│   ├── api/                # Dashboard API endpoints
│   ├── inference/          # Report generation
│   └── utils/              # Data processing utilities
├── data/                   # Dataset management
│   ├── raw/                # Original retail data
│   ├── processed/          # Cleaned returns/warranty data
│   └── external/           # External data sources
├── notebooks/              # Analysis & experimentation
├── models/                 # ML models & artifacts
├── experiments/            # RAG experiment tracking
├── output/                 # Generated reports & dashboards
└── docs/                   # Documentation
```

## Development Guidelines

- **Always search first** before creating new files
- **Extend existing** functionality rather than duplicating  
- **Use Task agents** for operations >30 seconds
- **Single source of truth** for all functionality
- **Language-agnostic structure** - works with Python, JS, Java, etc.
- **Scalable** - start simple, grow as needed
- **MLOps-ready** - supports experiment tracking and model versioning

## ✨ Features

### 🤖 Multi-Agent RAG System
- **6 Specialized Agents**: Data Fetch, Normalization, RAG, Report, Dashboard, Coordinator
- **Pipeline Orchestration**: Automated workflow with stage tracking
- **Message-Based Communication**: Async agent coordination
- **Error Handling & Retry**: Robust failure recovery mechanisms
- **Cost-Efficient**: Local embeddings + OpenAI integration (<$1 budget)

### 🌙 Dark Technology Dashboard
- **Modern UI**: Professional dark theme with cyan/blue technology accents
- **Real-Time Monitoring**: Live job status and system health updates
- **Interactive Analytics**: Charts with Recharts (bar, line, pie)
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Glass Morphism**: Beautiful backdrop blur effects

### 📊 Advanced Analytics
- **Job Execution Trends**: Weekly performance visualization
- **Agent Performance**: Individual agent success rates
- **System Metrics**: Real-time resource monitoring
- **24h Time Analysis**: Execution time patterns

### 📈 Report Generation
- **Excel Reports**: Multi-worksheet analysis with formatting
- **Executive Summaries**: High-level insights for stakeholders
- **Data Quality Reports**: Validation and cleanliness metrics
- **Download Management**: Organized report library

### ⚙️ Configuration Management
- **Environment Settings**: Database, RAG, Report, Dashboard configs
- **Real-Time Updates**: Settings applied without restart
- **Security**: Secure secret key management
- **Monitoring**: System health and performance tracking

## 🏗️ Architecture

### Technology Stack
**Backend:**
- Python 3.10+ with FastAPI
- SQLAlchemy ORM with SQLite
- OpenAI API integration
- Pytest testing framework

**Frontend:**
- React 18 + TypeScript
- Vite for fast development
- Tailwind CSS for styling
- Recharts for visualizations

**Infrastructure:**
- Message-driven architecture
- Async/await throughout
- RESTful API design
- Git-based deployment

## 📋 System Requirements

**Python Backend:**
- Python 3.10 or higher
- 2GB RAM minimum
- SQLite database support
- OpenAI API key (optional for full RAG)

**React Frontend:**
- Node.js 16+ and npm
- Modern web browser
- 1GB disk space for dependencies

## 🔧 Configuration

### Environment Variables (.env)
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=150

# RAG Configuration  
RAG_ENABLE_MOCK_MODE=false
RAG_MAX_API_CALLS_PER_SESSION=10
RAG_SIMILARITY_THRESHOLD=0.2

# Database Configuration
DATABASE_URL=sqlite:///data/retail_data.db
DATABASE_ECHO=false

# Dashboard Configuration
DASHBOARD_HOST=127.0.0.1
DASHBOARD_PORT=8000
DASHBOARD_DEBUG=false
```

## 🧪 Testing

```bash
# Run all tests
pytest src/test/ -v

# Run specific agent tests
pytest src/test/unit/test_coordinator_agent.py -v
pytest src/test/unit/test_dashboard_agent.py -v
pytest src/test/unit/test_rag_agent.py -v

# Integration tests
pytest src/test/integration/ -v
```

## 📊 Usage Examples

### Start Analysis Job via API
```python
import requests

# Start new analysis
response = requests.post('http://127.0.0.1:8000/api/v1/analysis/start', json={
    "date_range_start": "2024-01-01",
    "date_range_end": "2024-03-31",
    "tables": ["returns", "warranties"],
    "filters": {"category": "electronics"}
})

job_id = response.json()["job_id"]
print(f"Started job: {job_id}")
```

### Monitor Job Progress
```python
# Check job status
status_response = requests.get(f'http://127.0.0.1:8000/api/v1/analysis/{job_id}/status')
status = status_response.json()
print(f"Status: {status['status']}, Progress: {status['progress']*100:.1f}%")
```

## 🚀 Deployment

### Production Setup
1. **Environment**: Use production-grade database (PostgreSQL)
2. **Security**: Set strong secret keys and JWT tokens
3. **Scaling**: Deploy with Gunicorn/Uvicorn workers
4. **Frontend**: Build with `npm run build` and serve with Nginx
5. **Monitoring**: Enable logging and health checks

### Docker Deployment (Optional)
```dockerfile
# Create Dockerfile for containerized deployment
FROM python:3.10-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
CMD ["python", "run_dashboard.py"]
```

## 🤝 Contributing

1. **Read CLAUDE.md** - Essential development guidelines
2. **Follow Architecture** - Use existing patterns and structure
3. **Test Everything** - Comprehensive test coverage required
4. **Commit Often** - Atomic commits with descriptive messages
5. **Document Changes** - Update README and code comments

## 📖 Documentation

- **CLAUDE.md** - Development guidelines and critical rules
- **frontend/README.md** - React dashboard documentation
- **API Documentation** - Available at `/docs` when running backend
- **Agent Documentation** - Inline docstrings in agent classes

## 🛠️ Troubleshooting

**Common Issues:**
- **Port 8000 in use**: Change `DASHBOARD_PORT` in settings
- **OpenAI API errors**: Check API key and enable mock mode for testing
- **Database locked**: Ensure no other processes are using SQLite file
- **Frontend won't start**: Run `npm install` in frontend directory
- **Import errors**: Activate virtual environment and install requirements

**Debug Mode:**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python run_dashboard.py
```

## 📄 License

MIT License - Feel free to use and modify for your projects.

---

🎯 **Multi-Agent RAG System v1.0.0**  
🤖 **Generated with Claude Code** | 💻 **Technology Agent Style Dashboard**