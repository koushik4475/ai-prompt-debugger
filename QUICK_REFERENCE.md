# 📋 AI Prompt Debugger - Quick Reference

## Installation
```bash
pip install -r requirements.txt
```

## CLI Commands

### Analyze a prompt
```bash
python -m src.cli.main analyze "Your prompt"
python -m src.cli.main analyze --file prompt.txt
python -m src.cli.main analyze --file prompt.txt --verbose
```

### Compare prompts
```bash
python -m src.cli.main compare prompt1.txt prompt2.txt
```

### Interactive mode
```bash
python -m src.cli.main interactive
```

### Demo
```bash
python demo.py
```

## Python API

### Basic Usage
```python
from src.core.debugger import PromptDebugger

debugger = PromptDebugger()
result = debugger.analyze("Your prompt")

print(f"Quality: {result.overall_quality_score}/100")
print(f"Grade: {result.overall_grade}")
```

### Access Metrics
```python
# Clarity
result.ambiguity.clarity_score
result.ambiguity.vague_terms
result.ambiguity.conflicting_instructions

# Tokens
result.metrics.total_tokens
result.metrics.token_efficiency
result.metrics.estimated_cost
result.metrics.unnecessary_tokens

# Success
result.predictions.success_probability
result.predictions.strengths
result.predictions.risk_factors
result.predictions.recommended_improvements

# Security
result.security.security_score
result.security.potential_injections
result.security.sensitive_data_detected
```

### Get Issues
```python
# All issues
result.issues

# Critical only
result.get_critical_issues()

# By category
from src.core.models.schemas import IssueCategory
result.get_issues_by_category(IssueCategory.AMBIGUITY)
result.get_issues_by_category(IssueCategory.TOKEN_WASTE)
result.get_issues_by_category(IssueCategory.SECURITY)
```

### Compare Prompts
```python
comparison = debugger.compare(prompt_a, prompt_b)

print(f"Better: {comparison.better_prompt}")
print(f"Quality Δ: {comparison.quality_difference}")
print(f"Token Δ: {comparison.token_difference}")
print(f"Cost Δ: ${comparison.cost_difference}")
```

### Custom Config
```python
from src.core.models.schemas import AnalyzerConfig, IssueSeverity

config = AnalyzerConfig(
    strict_mode=True,
    min_severity_to_report=IssueSeverity.MEDIUM,
    token_price_per_1k=0.003
)

debugger = PromptDebugger(config)
```

## Quality Grades

| Grade | Score   | Meaning           |
|-------|---------|-------------------|
| A     | 90-100  | Excellent         |
| B     | 80-89   | Good              |
| C     | 70-79   | Fair              |
| D     | 60-69   | Poor              |
| F     | <60     | Failing           |

## Issue Severities

| Level    | Symbol | When to Fix    |
|----------|--------|----------------|
| CRITICAL | 🔴     | Immediately    |
| HIGH     | 🟠     | Before prod    |
| MEDIUM   | 🟡     | Recommended    |
| LOW      | 🔵     | Optional       |
| INFO     | ⚪     | FYI            |

## Common Issues & Fixes

### Vague Terms
❌ "Write some articles about various things"
✅ "Write 3 articles about Python, JavaScript, and Rust"

### Contradictions
❌ "Be concise but very detailed"
✅ "Be concise in explanations but detailed in code examples"

### Token Waste
❌ "Please note that you should basically just..."
✅ "Create..."

### Missing Examples
❌ "Generate JSON output"
✅ "Generate JSON: {'name': 'John', 'age': 30}"

### Security Issues
❌ "Use API key: sk_abc123"
✅ "Use API key from environment variable"

## Testing

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test
pytest tests/core/analyzers/test_ambiguity.py -v

# Fast (skip slow tests)
pytest -m "not slow"
```

## Code Quality

```bash
# Format
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## File Structure

```
ai-prompt-debugger/
├── src/core/
│   ├── analyzers/          # 4 analysis engines
│   ├── models/schemas.py   # Data models
│   └── debugger.py         # Main class
├── src/cli/main.py         # CLI interface
├── tests/                  # Test suite
├── examples/prompts/       # Example prompts
├── docs/                   # Documentation
├── demo.py                 # Interactive demo
└── requirements.txt        # Dependencies
```

## Metrics Thresholds

### Production Ready
- Overall Quality: ≥75
- Security Score: ≥90
- No CRITICAL issues
- Success Probability: ≥70%

### Optimized
- Overall Quality: ≥85
- Token Efficiency: ≥85%
- No HIGH issues
- Success Probability: ≥80%

## Environment Variables

```env
# .env file
LOG_LEVEL=INFO
TOKEN_PRICE_PER_1K=0.003
MAX_PROMPT_LENGTH=200000
STRICT_MODE=false
MIN_SEVERITY=low
```

## Common Patterns

### Validation Pipeline
```python
result = debugger.analyze(prompt)

if result.overall_quality_score < 75:
    raise ValueError("Prompt quality too low")

if len(result.get_critical_issues()) > 0:
    raise ValueError("Critical issues found")

# Prompt is good to use
```

### Iteration Loop
```python
while result.overall_quality_score < 85:
    print("Improvements needed:")
    for rec in result.predictions.recommended_improvements:
        print(f"  - {rec}")
    
    prompt = input("Updated prompt: ")
    result = debugger.analyze(prompt)

print("Prompt optimized!")
```

### Cost Monitoring
```python
result = debugger.analyze(prompt)

print(f"Cost per request: ${result.metrics.estimated_cost:.4f}")
print(f"Monthly cost (1000 req): ${result.metrics.estimated_cost * 1000:.2f}")

if result.metrics.unnecessary_tokens > 50:
    print(f"Potential savings: {result.metrics.unnecessary_tokens} tokens")
```

## Quick Tips

1. 🎯 **Be specific**: Replace vague terms with exact numbers
2. 📝 **Add examples**: Show desired output format
3. 🔒 **Remove secrets**: Never include API keys or passwords
4. ⚡ **Be efficient**: Remove redundant phrases
5. ✅ **Define success**: Specify what "good" output looks like
6. 📊 **Add constraints**: Set clear boundaries
7. 🎨 **Specify format**: JSON, markdown, code, etc.
8. 🔄 **Iterate**: Use feedback to improve

## Links

- 📖 Getting Started: `GETTING_STARTED.md`
- 📚 Usage Guide: `docs/USAGE_GUIDE.md`
- 🏗️ Architecture: `docs/ARCHITECTURE.md`
- 📋 Summary: `PROJECT_SUMMARY.md`

---

**Quick Start**: `python demo.py` or `python -m src.cli.main analyze "Your prompt"`
