# AI Prompt Debugger

A professional-grade prompt analysis and debugging tool for LLM applications. Helps developers, researchers, and prompt engineers identify issues, optimize token usage, and improve prompt quality.

## Features

### 🔍 Core Analysis Engines

1. **Ambiguity Detector**
   - Identifies conflicting instructions
   - Detects vague or undefined terms
   - Finds contradictory requirements
   - Analyzes instruction clarity

2. **Token Waste Analyzer**
   - Detects unnecessary verbosity
   - Identifies redundant phrases
   - Suggests compression opportunities
   - Estimates cost savings

3. **Success Predictor**
   - Analyzes prompt structure quality
   - Predicts likelihood of desired output
   - Identifies missing context
   - Suggests improvements

4. **Security & Safety Scanner**
   - Detects potential prompt injections
   - Identifies jailbreak attempts
   - Checks for sensitive data exposure
   - Validates input sanitization

## Architecture

```
ai-prompt-debugger/
├── src/
│   ├── core/               # Core business logic
│   │   ├── analyzers/      # Analysis engines
│   │   ├── models/         # Data models
│   │   └── utils/          # Utilities
│   ├── api/                # API layer
│   └── cli/                # CLI interface
├── tests/                  # Test suite
├── examples/               # Example prompts
└── docs/                   # Documentation
```

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### CLI Usage

```bash
# Analyze a prompt from file
python -m src.cli.main analyze examples/prompts/basic.txt

# Interactive mode
python -m src.cli.main interactive

# Compare two prompts
python -m src.cli.main compare prompt1.txt prompt2.txt
```

### Python API

```python
from src.core.debugger import PromptDebugger

debugger = PromptDebugger()
result = debugger.analyze("Your prompt here")

print(f"Issues found: {len(result.issues)}")
print(f"Token efficiency: {result.metrics.token_efficiency}%")
print(f"Success probability: {result.predictions.success_probability}%")
```

## Configuration

Create a `.env` file:

```env
ANTHROPIC_API_KEY=your_key_here
LOG_LEVEL=INFO
MAX_TOKENS=4096
```

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Run specific test suite
pytest tests/core/analyzers/test_ambiguity.py
```

## Development

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## License

MIT License - See LICENSE file for details
