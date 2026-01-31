# 📚 AI Prompt Debugger - File Index

## 📖 Documentation Files

### Quick Start
- **GETTING_STARTED.md** - Complete beginner's guide (5 min setup)
- **QUICK_REFERENCE.md** - Cheat sheet for common tasks
- **README.md** - Project overview and features

### Detailed Documentation  
- **PROJECT_SUMMARY.md** - Comprehensive project summary
- **docs/USAGE_GUIDE.md** - In-depth usage examples
- **docs/ARCHITECTURE.md** - System architecture and design patterns

## 🔧 Core Source Code

### Main Components
- **src/core/debugger.py** - Main orchestrator class (PromptDebugger)
- **src/core/models/schemas.py** - Pydantic data models

### Analysis Engines (src/core/analyzers/)
- **ambiguity.py** - Detects vague language and contradictions
- **token_waste.py** - Identifies unnecessary verbosity
- **success_prediction.py** - Predicts output quality
- **security.py** - Scans for security vulnerabilities

### Interface
- **src/cli/main.py** - Command-line interface with Rich formatting

## 🧪 Testing

### Test Suites (tests/core/analyzers/)
- **test_ambiguity.py** - Tests for ambiguity detection
- **test_token_waste.py** - Tests for token analysis
- **test_success_prediction.py** - Tests for success prediction
- **test_security.py** - Tests for security scanning

## 📦 Configuration

- **requirements.txt** - Python dependencies
- **pyproject.toml** - Project configuration (pytest, black, ruff, mypy)
- **.env.example** - Environment variable template
- **.gitignore** - Git ignore patterns

## 🎯 Examples & Demos

- **demo.py** - Interactive demonstration of all features
- **examples/prompts/poor_quality.txt** - Example of poor prompt
- **examples/prompts/high_quality.txt** - Example of good prompt

## 📊 File Organization

```
ai-prompt-debugger/
│
├── 📖 DOCUMENTATION (Start here!)
│   ├── GETTING_STARTED.md          ⭐ Begin here
│   ├── QUICK_REFERENCE.md          📋 Quick lookup
│   ├── README.md                   📘 Overview
│   ├── PROJECT_SUMMARY.md          📊 Full summary
│   └── docs/
│       ├── USAGE_GUIDE.md          📚 Detailed guide
│       └── ARCHITECTURE.md         🏗️ Technical docs
│
├── 🔧 SOURCE CODE
│   └── src/
│       ├── core/
│       │   ├── debugger.py         🎯 Main class
│       │   ├── models/
│       │   │   └── schemas.py      📋 Data models
│       │   └── analyzers/
│       │       ├── ambiguity.py    🔍 Ambiguity detector
│       │       ├── token_waste.py  💰 Token analyzer
│       │       ├── success_prediction.py 📈 Success predictor
│       │       └── security.py     🔒 Security scanner
│       └── cli/
│           └── main.py             💻 CLI interface
│
├── 🧪 TESTS
│   └── tests/core/analyzers/
│       ├── test_ambiguity.py
│       ├── test_token_waste.py
│       ├── test_success_prediction.py
│       └── test_security.py
│
├── 🎯 EXAMPLES
│   ├── demo.py                     🎬 Interactive demo
│   └── examples/prompts/
│       ├── poor_quality.txt        ❌ Bad example
│       └── high_quality.txt        ✅ Good example
│
└── ⚙️ CONFIG
    ├── requirements.txt            📦 Dependencies
    ├── pyproject.toml             🔧 Project config
    ├── .env.example               🔐 Env template
    └── .gitignore                 🚫 Git ignore

```

## 🚀 Recommended Reading Order

### For Users (Want to use the tool)
1. **GETTING_STARTED.md** - Setup and first use
2. **QUICK_REFERENCE.md** - Common commands
3. **docs/USAGE_GUIDE.md** - Detailed examples
4. Run **demo.py** - See it in action

### For Developers (Want to understand/extend)
1. **PROJECT_SUMMARY.md** - Overview
2. **docs/ARCHITECTURE.md** - System design
3. **src/core/debugger.py** - Main orchestrator
4. **src/core/analyzers/** - Individual analyzers
5. **tests/** - Test examples

### For Contributors
1. All documentation files
2. **pyproject.toml** - Code quality setup
3. **tests/** - Testing approach
4. Source code with docstrings

## 📝 Key Files by Purpose

### Want to analyze prompts?
→ **GETTING_STARTED.md** + **demo.py**

### Need quick help?
→ **QUICK_REFERENCE.md**

### Want comprehensive examples?
→ **docs/USAGE_GUIDE.md**

### Understanding the system?
→ **docs/ARCHITECTURE.md**

### Writing code/tests?
→ **src/** + **tests/**

### Configuring the tool?
→ **pyproject.toml** + **.env.example**

## 📊 File Statistics

- Total Documentation: 7 files
- Source Code Files: 9 files  
- Test Files: 4 files
- Configuration Files: 4 files
- Example Files: 3 files

**Total Project Files: 27+**

## 💡 Pro Tips

1. **Start with GETTING_STARTED.md** - 5 minute setup
2. **Run demo.py** - See all features in action
3. **Keep QUICK_REFERENCE.md handy** - Quick lookup
4. **Read ARCHITECTURE.md** - Understand the design
5. **Check tests/** - Real usage examples

---

**Quick Start**: `python demo.py` to see everything in action!
