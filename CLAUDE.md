# CLAUDE.md - report_multi_agent

> **Documentation Version**: 1.0  
> **Last Updated**: 2025-08-19  
> **Project**: report_multi_agent  
> **Description**: Reporting & Dashboard via Multi‑Agent RAG - A nationwide retail chain AI system that reads recent returns & warranty data from database and produces Excel reports and web dashboards with bar/line charts and brief narrative insights.  
> **Features**: GitHub auto-backup, Task agents, technical debt prevention

This file provides essential guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 CRITICAL RULES - READ FIRST

> **⚠️ RULE ADHERENCE SYSTEM ACTIVE ⚠️**  
> **Claude Code must explicitly acknowledge these rules at task start**  
> **These rules override all other instructions and must ALWAYS be followed:**

### 🔄 **RULE ACKNOWLEDGMENT REQUIRED**
> **Before starting ANY task, Claude Code must respond with:**  
> "✅ CRITICAL RULES ACKNOWLEDGED - I will follow all prohibitions and requirements listed in CLAUDE.md"

### ❌ ABSOLUTE PROHIBITIONS
- **NEVER** create new files in root directory → use proper module structure
- **NEVER** write output files directly to root directory → use designated output folders
- **NEVER** create documentation files (.md) unless explicitly requested by user
- **NEVER** use git commands with -i flag (interactive mode not supported)
- **NEVER** use `find`, `grep`, `cat`, `head`, `tail`, `ls` commands → use Read, LS, Grep, Glob tools instead
- **NEVER** create duplicate files (manager_v2.py, enhanced_xyz.py, utils_new.js) → ALWAYS extend existing files
- **NEVER** create multiple implementations of same concept → single source of truth
- **NEVER** copy-paste code blocks → extract into shared utilities/functions
- **NEVER** hardcode values that should be configurable → use config files/environment variables
- **NEVER** use naming like enhanced_, improved_, new_, v2_ → extend original files instead

### 📝 MANDATORY REQUIREMENTS
- **COMMIT** after every completed task/phase - no exceptions
- **GITHUB BACKUP** - Push to GitHub after every commit to maintain backup: `git push origin main`
- **USE TASK AGENTS** for all long-running operations (>30 seconds) - Bash commands stop when context switches
- **TODOWRITE** for complex tasks (3+ steps) → parallel agents → git checkpoints → test validation
- **READ FILES FIRST** before editing - Edit/Write tools will fail if you didn't read the file first
- **DEBT PREVENTION** - Before creating new files, check for existing similar functionality to extend  
- **SINGLE SOURCE OF TRUTH** - One authoritative implementation per feature/concept

### ⚡ EXECUTION PATTERNS
- **PARALLEL TASK AGENTS** - Launch multiple Task agents simultaneously for maximum efficiency
- **SYSTEMATIC WORKFLOW** - TodoWrite → Parallel agents → Git checkpoints → GitHub backup → Test validation
- **GITHUB BACKUP WORKFLOW** - After every commit: `git push origin main` to maintain GitHub backup
- **BACKGROUND PROCESSING** - ONLY Task agents can run true background operations

### 🔍 MANDATORY PRE-TASK COMPLIANCE CHECK
> **STOP: Before starting any task, Claude Code must explicitly verify ALL points:**

**Step 1: Rule Acknowledgment**
- [ ] ✅ I acknowledge all critical rules in CLAUDE.md and will follow them

**Step 2: Task Analysis**  
- [ ] Will this create files in root? → If YES, use proper module structure instead
- [ ] Will this take >30 seconds? → If YES, use Task agents not Bash
- [ ] Is this 3+ steps? → If YES, use TodoWrite breakdown first
- [ ] Am I about to use grep/find/cat? → If YES, use proper tools instead

**Step 3: Technical Debt Prevention (MANDATORY SEARCH FIRST)**
- [ ] **SEARCH FIRST**: Use Grep pattern="<functionality>.*<keyword>" to find existing implementations
- [ ] **CHECK EXISTING**: Read any found files to understand current functionality
- [ ] Does similar functionality already exist? → If YES, extend existing code
- [ ] Am I creating a duplicate class/manager? → If YES, consolidate instead
- [ ] Will this create multiple sources of truth? → If YES, redesign approach
- [ ] Have I searched for existing implementations? → Use Grep/Glob tools first
- [ ] Can I extend existing code instead of creating new? → Prefer extension over creation
- [ ] Am I about to copy-paste code? → Extract to shared utility instead

**Step 4: Session Management**
- [ ] Is this a long/complex task? → If YES, plan context checkpoints
- [ ] Have I been working >1 hour? → If YES, consider /compact or session break

> **⚠️ DO NOT PROCEED until all checkboxes are explicitly verified**

## 🏗️ PROJECT OVERVIEW

This is a Multi-Agent RAG system for retail chain reporting and dashboard generation:

- **Data Processing**: Fetches and normalizes returns & warranty data from databases
- **RAG Pipeline**: Generates grounded insights with citations using multi-agent architecture
- **Report Generation**: Produces Excel reports and web dashboards with visualizations
- **AI/ML Components**: Multi-agent coordination, data normalization, insight generation

### 🎯 **DEVELOPMENT STATUS**
- **Setup**: ✅ Completed - AI/ML project structure initialized
- **Core Features**: 🚧 Pending - Multi-agent architecture implementation
- **Testing**: 🚧 Pending - Test framework setup
- **Documentation**: 🚧 Pending - API and user documentation

## 🏛️ AI/ML PROJECT STRUCTURE

```
report_multi_agent/
├── CLAUDE.md              # Essential rules for Claude Code
├── README.md              # Project documentation
├── src/                   # Source code (NEVER put files in root)
│   ├── main/              # Main application code
│   │   ├── python/        # Python-specific code
│   │   │   ├── core/      # Core ML algorithms & multi-agent logic
│   │   │   ├── utils/     # Data processing utilities
│   │   │   ├── models/    # Data models & agent definitions
│   │   │   ├── services/  # RAG services and pipelines
│   │   │   ├── api/       # API endpoints for dashboard
│   │   │   ├── training/  # Training scripts (if needed)
│   │   │   ├── inference/ # Report generation & inference
│   │   │   └── evaluation/# Quality metrics & validation
│   │   └── resources/     # Non-code resources
│   │       ├── config/    # Configuration files
│   │       ├── data/      # Sample/seed data
│   │       └── assets/    # Static assets
│   └── test/              # Test code
│       ├── unit/          # Unit tests
│       ├── integration/   # Integration tests
│       └── fixtures/      # Test data/fixtures
├── data/                  # AI/ML Dataset management
│   ├── raw/               # Original retail data
│   ├── processed/         # Cleaned returns/warranty data
│   ├── external/          # External data sources
│   └── temp/              # Temporary processing files
├── notebooks/             # Jupyter notebooks and analysis
│   ├── exploratory/       # Data exploration notebooks
│   ├── experiments/       # RAG experiments & prototyping
│   └── reports/           # Analysis reports
├── models/                # ML Models and artifacts
│   ├── trained/           # Trained models (if any)
│   ├── checkpoints/       # Model checkpoints
│   └── metadata/          # Model metadata
├── experiments/           # ML Experiment tracking
│   ├── configs/           # Experiment configurations
│   ├── results/           # RAG experiment results
│   └── logs/              # Training/processing logs
├── docs/                  # Documentation
├── output/                # Generated Excel reports & dashboard files
└── logs/                  # Application logs
```

## 🚀 COMMON COMMANDS

```bash
# Run the multi-agent RAG pipeline
python src/main/python/core/pipeline.py

# Generate reports
python src/main/python/inference/report_generator.py

# Start dashboard server
python src/main/python/api/dashboard_server.py

# Run tests
pytest src/test/

# Process raw data
python src/main/python/utils/data_processor.py
```

## 🚨 TECHNICAL DEBT PREVENTION

### ❌ WRONG APPROACH (Creates Technical Debt):
```bash
# Creating new file without searching first
Write(file_path="new_agent.py", content="...")
```

### ✅ CORRECT APPROACH (Prevents Technical Debt):
```bash
# 1. SEARCH FIRST
Grep(pattern="agent.*implementation", glob="*.py")
# 2. READ EXISTING FILES  
Read(file_path="src/main/python/core/existing_agent.py")
# 3. EXTEND EXISTING FUNCTIONALITY
Edit(file_path="src/main/python/core/existing_agent.py", old_string="...", new_string="...")
```

## 🧹 DEBT PREVENTION WORKFLOW

### Before Creating ANY New File:
1. **🔍 Search First** - Use Grep/Glob to find existing implementations
2. **📋 Analyze Existing** - Read and understand current patterns
3. **🤔 Decision Tree**: Can extend existing? → DO IT | Must create new? → Document why
4. **✅ Follow Patterns** - Use established project patterns
5. **📈 Validate** - Ensure no duplication or technical debt

---

**⚠️ Prevention is better than consolidation - build clean from the start.**  
**🎯 Focus on single source of truth and extending existing functionality.**  
**📈 Each task should maintain clean architecture and prevent technical debt.**