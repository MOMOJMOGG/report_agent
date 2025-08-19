# report_multi_agent

**Multi-Agent RAG System for Retail Chain Reporting & Dashboard Generation**

A nationwide retail chain AI system that reads recent returns & warranty data from its database and produces Excel reports and web dashboards with bar/line charts and brief narrative insights using a multi-agent RAG architecture.

## Quick Start

1. **Read CLAUDE.md first** - Contains essential rules for Claude Code
2. Follow the pre-task compliance checklist before starting any work
3. Use proper module structure under `src/main/python/`
4. Commit after every completed task

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

## Features

- 🤖 **Multi-Agent RAG Pipeline**: Coordinated agents for data processing and insight generation
- 📊 **Excel Report Generation**: Automated creation of formatted reports
- 🌐 **Web Dashboard**: Interactive visualizations with bar/line charts
- 🔍 **Grounded Insights**: RAG-powered analysis with citations
- 📈 **Real-time Processing**: Direct database connectivity for fresh data
- 🏗️ **Scalable Architecture**: Modular design supporting enterprise deployment

## Core Components

### Multi-Agent System
- **Agent Coordination**: Message-based communication between specialized agents
- **Task Distribution**: Parallel processing for optimal performance
- **Error Handling**: Robust failure recovery and retry mechanisms

### RAG Pipeline
- **Data Retrieval**: Efficient database querying and data extraction
- **Context Generation**: Intelligent context building for LLM processing
- **Insight Generation**: Grounded analysis with source citations
- **Quality Assurance**: Validation and fact-checking mechanisms

### Report & Dashboard Generation
- **Excel Integration**: Automated spreadsheet creation with formatting
- **Web Visualization**: Interactive charts using modern web technologies
- **Template System**: Customizable report and dashboard templates
- **Export Options**: Multiple format support for different stakeholders

## Getting Started

1. **Setup Environment**: Install dependencies and configure database connections
2. **Configure Agents**: Set up agent parameters and communication protocols  
3. **Run Pipeline**: Execute multi-agent RAG workflow
4. **Generate Outputs**: Create Excel reports and web dashboards
5. **Monitor Results**: Review insights and validate output quality

## License

[Add your license information here]

---

🎯 **Template by Chang Ho Chien | HC AI 說人話channel | v1.0.0**  
📺 **Tutorial**: https://youtu.be/8Q1bRZaHH24