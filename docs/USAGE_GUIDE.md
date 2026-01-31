# AI Prompt Debugger - Usage Guide

## Overview

The AI Prompt Debugger is a professional tool for analyzing, optimizing, and debugging prompts for Large Language Models (LLMs). It helps identify issues, reduce token waste, and improve the likelihood of getting desired outputs.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd ai-prompt-debugger

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Basic Analysis

Analyze a prompt directly from command line:

```bash
python -m src.cli.main analyze "Create a Python function to sort a list"
```

Analyze from a file:

```bash
python -m src.cli.main analyze --file examples/prompts/high_quality.txt
```

### 2. Verbose Analysis

Get detailed analysis with all issues and examples:

```bash
python -m src.cli.main analyze --file prompt.txt --verbose
```

### 3. Compare Two Prompts

Compare two different versions of a prompt:

```bash
python -m src.cli.main compare prompt_v1.txt prompt_v2.txt
```

### 4. Interactive Mode

Start an interactive session:

```bash
python -m src.cli.main interactive
```

## Python API Usage

### Basic Analysis

```python
from src.core.debugger import PromptDebugger

# Initialize debugger
debugger = PromptDebugger()

# Analyze a prompt
prompt = """
Create a REST API endpoint for user authentication.
Include error handling and input validation.
"""

result = debugger.analyze(prompt)

# Access results
print(f"Overall Quality: {result.overall_quality_score}/100")
print(f"Grade: {result.overall_grade}")
print(f"Total Tokens: {result.metrics.total_tokens}")
print(f"Success Probability: {result.predictions.success_probability}%")

# Get issues
for issue in result.issues:
    print(f"[{issue.severity}] {issue.title}")
    print(f"  {issue.description}")
    if issue.suggestion:
        print(f"  💡 {issue.suggestion}")
```

### Advanced Configuration

```python
from src.core.debugger import PromptDebugger
from src.core.models.schemas import AnalyzerConfig, IssueSeverity

# Custom configuration
config = AnalyzerConfig(
    enable_ambiguity_detection=True,
    enable_token_analysis=True,
    enable_success_prediction=True,
    enable_security_scanning=True,
    strict_mode=True,  # Stricter analysis
    min_severity_to_report=IssueSeverity.MEDIUM,  # Only report medium and above
    token_price_per_1k=0.003  # Custom pricing
)

debugger = PromptDebugger(config)
result = debugger.analyze(prompt)
```

### Comparing Prompts

```python
prompt_v1 = "Write code to sort numbers."
prompt_v2 = """
Create a Python function that sorts a list of integers.

Requirements:
- Use built-in sort methods
- Handle empty lists
- Return sorted list in ascending order

Example:
sort_numbers([3, 1, 2]) -> [1, 2, 3]
"""

comparison = debugger.compare(prompt_v1, prompt_v2)

print(f"Better prompt: {comparison.better_prompt}")
print(f"Quality difference: {comparison.quality_difference:.1f} points")
print(f"Token difference: {comparison.token_difference} tokens")
print(f"\nKey differences:")
for diff in comparison.key_differences:
    print(f"  • {diff}")
```

### Accessing Specific Metrics

```python
result = debugger.analyze(prompt)

# Ambiguity metrics
print(f"Clarity Score: {result.ambiguity.clarity_score}/100")
print(f"Vague terms: {result.ambiguity.vague_terms}")
print(f"Conflicts: {result.ambiguity.conflicting_instructions}")

# Token metrics
print(f"Total tokens: {result.metrics.total_tokens}")
print(f"Token efficiency: {result.metrics.token_efficiency}%")
print(f"Wasted tokens: {result.metrics.unnecessary_tokens}")
print(f"Estimated cost: ${result.metrics.estimated_cost:.4f}")

# Success prediction
print(f"Success probability: {result.predictions.success_probability}%")
print(f"Confidence: {result.predictions.confidence_score}%")
print(f"Strengths: {result.predictions.strengths}")
print(f"Risks: {result.predictions.risk_factors}")

# Security metrics
print(f"Security score: {result.security.security_score}/100")
print(f"Potential injections: {result.security.potential_injections}")
print(f"Sensitive data: {result.security.sensitive_data_detected}")
```

### Filtering Issues

```python
result = debugger.analyze(prompt)

# Get only critical issues
critical = result.get_critical_issues()
for issue in critical:
    print(f"CRITICAL: {issue.title}")

# Get issues by category
from src.core.models.schemas import IssueCategory

ambiguity_issues = result.get_issues_by_category(IssueCategory.AMBIGUITY)
token_issues = result.get_issues_by_category(IssueCategory.TOKEN_WASTE)
security_issues = result.get_issues_by_category(IssueCategory.SECURITY)
```

## Understanding Results

### Quality Scores

- **Overall Quality (0-100)**: Weighted average of all metrics
  - 90-100: Excellent (Grade A)
  - 80-89: Good (Grade B)
  - 70-79: Fair (Grade C)
  - 60-69: Poor (Grade D)
  - <60: Failing (Grade F)

- **Clarity Score (0-100)**: Inverse of ambiguity
  - Higher = clearer, more specific instructions

- **Token Efficiency (0-100%)**: Percentage of non-wasted tokens
  - Higher = more efficient use of tokens

- **Success Probability (0-100%)**: Likelihood of desired output
  - Higher = better structured prompt

- **Security Score (0-100)**: Safety and security level
  - Higher = safer, no injection attempts

### Issue Severities

1. **CRITICAL**: Must fix immediately (security, injections)
2. **HIGH**: Strongly recommended to fix (contradictions, major ambiguity)
3. **MEDIUM**: Should fix for better results (vague terms, token waste)
4. **LOW**: Optional improvements (minor optimizations)
5. **INFO**: Informational (suggestions, tips)

## Best Practices

### 1. Start with Analysis

Always analyze your prompt before using it in production:

```python
result = debugger.analyze(your_prompt)
if result.overall_quality_score < 70:
    print("⚠️  Prompt needs improvement")
    for rec in result.predictions.recommended_improvements:
        print(f"  • {rec}")
```

### 2. Iterate Based on Feedback

Use the suggestions to improve your prompt:

```python
# Version 1
v1 = "Write some code about data processing"
result_v1 = debugger.analyze(v1)

# Improved based on feedback
v2 = """
Create a Python function that processes CSV data.

Requirements:
- Read CSV file
- Clean missing values
- Calculate statistics
- Return pandas DataFrame

Example input: sales_data.csv
Example output: DataFrame with cleaned data + summary stats
"""
result_v2 = debugger.analyze(v2)

# Compare improvement
print(f"Improvement: {result_v2.overall_quality_score - result_v1.overall_quality_score:.1f} points")
```

### 3. Monitor Token Usage

Keep an eye on costs:

```python
result = debugger.analyze(prompt)
print(f"Tokens: {result.metrics.total_tokens}")
print(f"Cost per request: ${result.metrics.estimated_cost:.4f}")
print(f"Potential savings: {result.metrics.unnecessary_tokens} tokens")

if result.metrics.token_efficiency < 85:
    print("Consider optimizing for better efficiency")
```

### 4. Security Checks

Always scan prompts that include user input:

```python
user_prompt = get_user_input()  # From your application
result = debugger.analyze(user_prompt)

if result.security.security_score < 80:
    print("⚠️  Security concern detected")
    for issue in result.get_issues_by_category(IssueCategory.SECURITY):
        log_security_warning(issue)
```

## Integration Examples

### Web Application Integration

```python
from flask import Flask, request, jsonify
from src.core.debugger import PromptDebugger

app = Flask(__name__)
debugger = PromptDebugger()

@app.route('/analyze', methods=['POST'])
def analyze_prompt():
    data = request.json
    prompt = data.get('prompt')
    
    try:
        result = debugger.analyze(prompt)
        
        return jsonify({
            'quality_score': result.overall_quality_score,
            'grade': result.overall_grade,
            'issues': [
                {
                    'severity': issue.severity.value,
                    'title': issue.title,
                    'description': issue.description,
                    'suggestion': issue.suggestion
                }
                for issue in result.issues
            ],
            'metrics': {
                'tokens': result.metrics.total_tokens,
                'cost': result.metrics.estimated_cost,
                'efficiency': result.metrics.token_efficiency
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400
```

### CI/CD Integration

```python
# test_prompts.py
import sys
from pathlib import Path
from src.core.debugger import PromptDebugger

def test_production_prompts():
    debugger = PromptDebugger()
    prompts_dir = Path('prompts/production')
    
    failed = []
    
    for prompt_file in prompts_dir.glob('*.txt'):
        with open(prompt_file) as f:
            prompt = f.read()
        
        result = debugger.analyze(prompt)
        
        # Enforce quality standards
        if result.overall_quality_score < 75:
            failed.append(f"{prompt_file.name}: Quality {result.overall_quality_score}/100")
        
        if result.security.security_score < 90:
            failed.append(f"{prompt_file.name}: Security {result.security.security_score}/100")
    
    if failed:
        print("❌ Prompt quality checks failed:")
        for failure in failed:
            print(f"  • {failure}")
        sys.exit(1)
    else:
        print("✅ All prompts pass quality checks")

if __name__ == '__main__':
    test_production_prompts()
```

## Troubleshooting

### Issue: "Module not found"
```bash
# Ensure you're in the project root
cd ai-prompt-debugger

# Install dependencies
pip install -r requirements.txt
```

### Issue: "Token encoding error"
```bash
# Install tiktoken
pip install tiktoken --break-system-packages
```

### Issue: High memory usage
```python
# For very large prompts, disable some analyzers
config = AnalyzerConfig(
    enable_token_analysis=False  # Skip if memory constrained
)
debugger = PromptDebugger(config)
```

## Support

For issues, feature requests, or questions:
- GitHub Issues: [repository-url]/issues
- Documentation: [repository-url]/docs
- Email: support@example.com
