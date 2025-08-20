# Multi-Agent RAG System 🤖

**Advanced Retail Analytics with Multi-Agent Architecture & Technology Dashboard**

A sophisticated AI system that orchestrates multiple specialized agents to analyze retail returns and warranty data, generating comprehensive Excel reports and interactive web dashboards with real-time analytics and grounded insights.

![Technology Stack](https://img.shields.io/badge/Backend-Python%20%7C%20FastAPI-blue)
![Frontend](https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript-cyan)
![Database](https://img.shields.io/badge/Database-SQLite%20%7C%20SQLAlchemy-green)
![AI](https://img.shields.io/badge/AI-OpenAI%20%7C%20RAG-orange)

## 🚀 Quick Start

### One-Command Setup (Recommended)
```bash
# 1. Create virtual environment
python -m venv agent
source agent/bin/activate  # Linux/Mac
# OR
agent\Scripts\activate     # Windows

# 2. Generate secure keys
python generate_secrets.py

# 3. Start complete system
python start_system.py
```

**Access Points:**
- 🌐 **Dashboard**: http://localhost:3000 (React UI)
- 🔧 **Backend API**: http://127.0.0.1:8000
- 📋 **API Docs**: http://127.0.0.1:8000/docs

## ✨ Key Features

### 🤖 **Multi-Agent Architecture**
- **6 Specialized Agents**: Data Fetch → Normalization → RAG → Report → Dashboard → Coordinator
- **Async Message Passing**: Efficient inter-agent communication
- **Pipeline Orchestration**: Automated workflow with stage tracking
- **Error Recovery**: Robust retry mechanisms and graceful failure handling

### 🌙 **Dark Technology Dashboard**
- **Modern Dark Theme**: Professional UI with cyan/blue technology accents
- **Real-Time Monitoring**: Live job status updates and progress tracking
- **Interactive Charts**: Analytics with bar, line, and pie visualizations
- **Responsive Design**: Optimized for desktop, tablet, and mobile

### 📊 **Advanced Analytics**
- **Job Execution Trends**: Weekly performance visualization
- **Agent Performance**: Individual success rates and load monitoring
- **System Health**: Real-time resource and status monitoring
- **24/7 Operations**: Continuous monitoring and alerting

### 📈 **Report Generation**
- **Excel Reports**: Multi-worksheet analysis with professional formatting
- **Executive Summaries**: High-level insights for stakeholders
- **Data Quality Reports**: Validation metrics and cleanliness scores
- **Download Management**: Organized report library with metadata

## 🏗️ Project Structure

```
multi_agent/
├── README.md                    # This file
├── CLAUDE.md                   # Development guidelines
├── start_system.py             # One-command startup script
├── generate_secrets.py         # Security key generator
├── run_dashboard.py            # Backend server runner
├── requirements.txt            # Python dependencies
│
├── multi_agent/                # Main Python package
│   ├── agents/                 # Specialized AI agents
│   │   ├── coordinator_agent.py    # Pipeline orchestrator
│   │   ├── data_fetch_agent.py     # Database connector
│   │   ├── normalization_agent.py  # Data cleaner
│   │   ├── rag_agent.py            # RAG processor
│   │   ├── report_agent.py         # Excel generator
│   │   └── dashboard_agent.py      # API server
│   ├── core/                   # Core framework
│   │   ├── base_agent.py           # Agent base class
│   │   └── message_broker.py       # Message passing
│   ├── models/                 # Data models
│   │   ├── database_models.py      # SQLAlchemy models
│   │   └── message_types.py        # Agent messages
│   ├── config/                 # Configuration
│   │   ├── settings.py             # App settings
│   │   └── database.py             # DB config
│   ├── utils/                  # Utilities
│   │   └── seed_data_generator.py  # Sample data
│   └── tests/                  # Comprehensive tests
│       ├── unit/                   # Unit tests
│       ├── integration/            # Integration tests
│       └── conftest.py             # Test configuration
│
├── frontend/                   # React dashboard
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── pages/              # Dashboard pages
│   │   ├── hooks/              # React hooks
│   │   ├── utils/              # Utilities
│   │   └── types/              # TypeScript types
│   ├── package.json            # Node dependencies
│   └── README.md               # Frontend docs
│
├── data/                       # Data storage
│   └── retail_data.db          # SQLite database
├── output/                     # Generated files
│   └── reports/                # Excel reports
├── logs/                       # Application logs
└── docs/                       # Documentation
    ├── SECRET_KEYS_GUIDE.md    # Security setup
    └── development-plan.md     # Development history
```

## 🔧 Technology Stack

**Backend (Python):**
- **FastAPI**: Modern, fast web framework with automatic API docs
- **SQLAlchemy**: Powerful ORM with SQLite database
- **OpenAI API**: GPT integration for RAG processing
- **Pytest**: Comprehensive testing framework

**Frontend (React):**
- **React 18**: Modern React with hooks and TypeScript
- **Vite**: Lightning-fast development and building
- **Tailwind CSS**: Utility-first styling with dark theme
- **Recharts**: Interactive data visualizations

**Infrastructure:**
- **Async Architecture**: Full async/await for performance
- **RESTful API**: Clean API design with proper HTTP methods
- **Message Passing**: Event-driven agent communication
- **Environment Config**: Secure configuration management

## 📋 System Requirements

**Development:**
- Python 3.10+
- Node.js 16+ and npm
- 4GB RAM minimum
- Modern web browser

**Production:**
- 8GB RAM recommended
- PostgreSQL (optional upgrade from SQLite)
- Reverse proxy (Nginx recommended)
- SSL certificate for HTTPS

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Security (Generated by generate_secrets.py)
SECRET_KEY=your_generated_secret_key
JWT_SECRET_KEY=your_generated_jwt_secret_key

# OpenAI (Optional - can use mock mode)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=150

# Database
DATABASE_URL=sqlite:///data/retail_data.db
DATABASE_ECHO=false

# RAG Configuration
RAG_ENABLE_MOCK_MODE=false
RAG_MAX_API_CALLS_PER_SESSION=10
RAG_SIMILARITY_THRESHOLD=0.2

# Dashboard
DASHBOARD_HOST=127.0.0.1
DASHBOARD_PORT=8000
DASHBOARD_DEBUG=false
```

## 🧪 Testing

```bash
# Run all tests
pytest multi_agent/tests/ -v

# Run specific test categories
pytest multi_agent/tests/unit/ -v
pytest multi_agent/tests/integration/ -v

# Run with coverage
pytest multi_agent/tests/ --cov=multi_agent --cov-report=html
```

## 📊 Usage Examples

### Start Analysis via Dashboard
1. Open http://localhost:3000
2. Click "Quick Analysis" button
3. Monitor real-time progress
4. Download Excel reports when complete

### API Usage (Python)
```python
import requests

# Start analysis job
response = requests.post('http://127.0.0.1:8000/api/v1/analysis/start', json={
    "date_range_start": "2024-01-01",
    "date_range_end": "2024-03-31",
    "tables": ["returns", "warranties"],
    "filters": {"category": "electronics"}
})

job_id = response.json()["job_id"]

# Monitor progress
status_response = requests.get(f'http://127.0.0.1:8000/api/v1/analysis/{job_id}/status')
print(f"Status: {status_response.json()['status']}")
```

## 🚀 Deployment

### Development
```bash
# Frontend development mode
cd frontend && npm run dev

# Backend development mode  
python run_dashboard.py
```

### Production
```bash
# Build frontend
cd frontend && npm run build

# Start with production settings
export DASHBOARD_DEBUG=false
python start_system.py
```

### Docker (Optional)
```dockerfile
FROM python:3.10-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 8000
CMD ["python", "run_dashboard.py"]
```

## 🛠️ Troubleshooting

### Common Issues

**"No virtual environment detected"**
```bash
python -m venv agent
source agent/bin/activate  # Linux/Mac
agent\Scripts\activate     # Windows
```

**"SECRET_KEY not found"**
```bash
python generate_secrets.py
# Choose option 1 to create .env file
```

**"Port 8000 in use"**
```bash
# Change port in .env file
DASHBOARD_PORT=8080
```

**"OpenAI API errors"**
```bash
# Enable mock mode for testing
RAG_ENABLE_MOCK_MODE=true
```

### Debug Mode
```bash
# Enable detailed logging
export LOG_LEVEL=DEBUG
python start_system.py
```

## 🔒 Security

- **Secure Key Generation**: Cryptographically secure random keys
- **Environment Variables**: Sensitive data in .env (never committed)
- **Input Validation**: All API inputs validated and sanitized
- **CORS Protection**: Configured origins for web security
- **Rate Limiting**: API rate limiting for production use

## 📈 Performance

- **Async Architecture**: Non-blocking operations throughout
- **Database Optimization**: Efficient queries with SQLAlchemy
- **Caching Strategy**: Smart caching for RAG operations
- **Resource Monitoring**: Built-in performance metrics
- **Horizontal Scaling**: Agent-based architecture scales well

## 🤝 Contributing

1. **Read CLAUDE.md** - Essential development guidelines
2. **Follow Structure** - Use established patterns and imports
3. **Test Coverage** - Write tests for all new features
4. **Commit Style** - Use descriptive commit messages
5. **Documentation** - Update README and inline docs

## 🆘 Support

- **Documentation**: Check `docs/` directory
- **API Reference**: Visit `/docs` endpoint when running
- **Environment Check**: Run `python check_venv.py`
- **Key Generation**: Run `python generate_secrets.py`

## 📄 License

MIT License - Feel free to use and modify for your projects.

---

**🤖 Multi-Agent RAG System v1.0.0**  
*Professional retail analytics with AI-powered insights and modern dashboard*

Built with ❤️ using Claude Code | Technology Agent Aesthetic 🌙