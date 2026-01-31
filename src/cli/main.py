"""
Command-line interface for the AI Prompt Debugger.
"""
import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.debugger import PromptDebugger
from src.core.models.schemas import AnalyzerConfig, IssueSeverity

app = typer.Typer(
    name="prompt-debugger",
    help="AI Prompt Debugger - Analyze and optimize your LLM prompts",
    add_completion=False
)
console = Console()


def load_prompt_from_file(filepath: str) -> str:
    """Load prompt text from a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        console.print(f"[red]Error: File not found: {filepath}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")
        raise typer.Exit(1)


def display_analysis_result(result, verbose: bool = False):
    """Display analysis result in a formatted way"""
    
    # Header
    console.print("\n")
    console.print(Panel(
        f"[bold cyan]Overall Quality: {result.overall_quality_score:.1f}/100[/bold cyan]\n"
        f"[bold]Grade: {result.overall_grade}[/bold]",
        title="[Analysis Results]",
        border_style="cyan"
    ))
    
    # Metrics Summary
    metrics_table = Table(title="Core Metrics", box=box.ROUNDED)
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Score", style="green")
    metrics_table.add_column("Status", style="yellow")
    
    # Add rows
    metrics_table.add_row(
        "Clarity",
        f"{result.ambiguity.clarity_score:.1f}/100",
        "OK Good" if result.ambiguity.clarity_score >= 70 else "NEEDS WORK"
    )
    metrics_table.add_row(
        "Token Efficiency",
        f"{result.metrics.token_efficiency:.1f}%",
        "OK Efficient" if result.metrics.token_efficiency >= 85 else "NEEDS WORK"
    )
    metrics_table.add_row(
        "Success Probability",
        f"{result.predictions.success_probability:.1f}%",
        "OK High" if result.predictions.success_probability >= 70 else "NEEDS WORK"
    )
    metrics_table.add_row(
        "Security Score",
        f"{result.security.security_score:.1f}/100",
        "OK Safe" if result.security.security_score >= 80 else "NEEDS REVIEW"
    )
    
    console.print(metrics_table)
    
    # Token Usage
    console.print("\n")
    token_panel = Panel(
        f"[bold]Total Tokens:[/bold] {result.metrics.total_tokens:,}\n"
        f"[bold]Estimated Cost:[/bold] ${result.metrics.estimated_cost:.4f}\n"
        f"[bold]Unnecessary Tokens:[/bold] {result.metrics.unnecessary_tokens} "
        f"(${(result.metrics.unnecessary_tokens / 1000) * 0.003:.4f} wasted)",
        title="[Token Analysis]",
        border_style="yellow"
    )
    console.print(token_panel)
    
    # Issues
    if result.issues:
        console.print("\n")
        issues_by_severity = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for issue in result.issues:
            issues_by_severity[issue.severity.value].append(issue)
        
        # Display by severity
        for severity in ['critical', 'high', 'medium', 'low']:
            issues = issues_by_severity[severity]
            if not issues:
                continue
            
            color = {
                'critical': 'red',
                'high': 'orange1',
                'medium': 'yellow',
                'low': 'blue'
            }[severity]
            
            console.print(f"\n[bold {color}]{severity.upper()} ISSUES ({len(issues)}):[/bold {color}]")
            
            for i, issue in enumerate(issues, 1):
                console.print(f"\n[{color}]{i}. {issue.title}[/{color}]")
                console.print(f"   {issue.description}")
                if issue.suggestion:
                    console.print(f"   [italic][i] {issue.suggestion}[/italic]")
                
                if verbose and issue.examples:
                    console.print("   [dim]Examples:[/dim]")
                    for example in issue.examples:
                        console.print(f"   [dim]  - {example}[/dim]")
    
    # Recommendations
    if result.predictions.recommended_improvements:
        console.print("\n")
        rec_panel = Panel(
            "\n".join([f"- {rec}" for rec in result.predictions.recommended_improvements]),
            title="[Recommended Improvements]",
            border_style="green"
        )
        console.print(rec_panel)
    
    # Strengths
    if result.predictions.strengths:
        console.print("\n")
        console.print("[bold green]OK Strengths:[/bold green]")
        for strength in result.predictions.strengths:
            console.print(f"  - {strength}")


@app.command()
def analyze(
    prompt: Optional[str] = typer.Argument(None, help="Prompt text or path to file"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="Path to prompt file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed analysis"),
    strict: bool = typer.Option(False, "--strict", help="Use strict analysis mode"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Save results to file")
):
    """
    Analyze a prompt for issues and optimization opportunities.
    
    Examples:
        prompt-debugger analyze "Create a blog post about AI"
        prompt-debugger analyze --file prompt.txt
        prompt-debugger analyze --file prompt.txt --verbose
    """
    # Load prompt
    if file:
        prompt_text = load_prompt_from_file(file)
    elif prompt:
        prompt_text = prompt
    else:
        console.print("[red]Error: Provide either a prompt text or --file option[/red]")
        raise typer.Exit(1)
    
    # Show prompt preview
    console.print("\n[bold]Analyzing prompt:[/bold]")
    console.print(Panel(
        Syntax(prompt_text[:500] + ("..." if len(prompt_text) > 500 else ""), 
               "text", theme="monokai", line_numbers=False),
        title="Prompt Preview",
        border_style="blue"
    ))
    
    # Analyze with progress indicator
    with Progress(console=console) as progress:
        task = progress.add_task("Running analysis...", total=None)
        
        config = AnalyzerConfig(strict_mode=strict)
        debugger = PromptDebugger(config)
        result = debugger.analyze(prompt_text)
        
        progress.update(task, completed=True)
    
    # Display results
    display_analysis_result(result, verbose)
    
    # Save to file if requested
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(f"Prompt Analysis Report\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(f"Overall Quality: {result.overall_quality_score:.1f}/100 (Grade: {result.overall_grade})\n")
            f.write(f"Total Tokens: {result.metrics.total_tokens:,}\n")
            f.write(f"Estimated Cost: ${result.metrics.estimated_cost:.4f}\n\n")
            f.write(f"Issues Found: {len(result.issues)}\n")
            # ... (rest of report)
        
        console.print(f"\n[green]OK Results saved to {output}[/green]")


@app.command()
def compare(
    file1: str = typer.Argument(..., help="First prompt file"),
    file2: str = typer.Argument(..., help="Second prompt file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed comparison")
):
    """
    Compare two prompts and identify which is better.
    
    Example:
        prompt-debugger compare prompt1.txt prompt2.txt
    """
    prompt1 = load_prompt_from_file(file1)
    prompt2 = load_prompt_from_file(file2)
    
    with Progress(console=console) as progress:
        task = progress.add_task("Comparing prompts...", total=None)
        
        debugger = PromptDebugger()
        comparison = debugger.compare(prompt1, prompt2)
        
        progress.update(task, completed=True)
    
    # Display comparison
    console.print("\n")
    console.print(Panel(
        f"[bold cyan]Winner: Prompt {comparison.better_prompt}[/bold cyan]\n\n"
        f"{comparison.comparison_summary}",
        title="[Comparison Results]",
        border_style="cyan"
    ))
    
    # Quality comparison
    console.print("\n")
    comp_table = Table(title="Quality Comparison", box=box.ROUNDED)
    comp_table.add_column("Metric", style="cyan")
    comp_table.add_column("Prompt A", style="blue")
    comp_table.add_column("Prompt B", style="green")
    comp_table.add_column("Difference", style="yellow")
    
    comp_table.add_row(
        "Overall Quality",
        f"{comparison.prompt_a.overall_quality_score:.1f}",
        f"{comparison.prompt_b.overall_quality_score:.1f}",
        f"{comparison.quality_difference:+.1f}"
    )
    comp_table.add_row(
        "Tokens",
        f"{comparison.prompt_a.metrics.total_tokens:,}",
        f"{comparison.prompt_b.metrics.total_tokens:,}",
        f"{comparison.token_difference:+,}"
    )
    comp_table.add_row(
        "Cost",
        f"${comparison.prompt_a.metrics.estimated_cost:.4f}",
        f"${comparison.prompt_b.metrics.estimated_cost:.4f}",
        f"${comparison.cost_difference:+.4f}"
    )
    
    console.print(comp_table)
    
    # Key differences
    if comparison.key_differences:
        console.print("\n[bold]Key Differences:[/bold]")
        for diff in comparison.key_differences:
            console.print(f"  - {diff}")


@app.command()
def interactive():
    """
    Start interactive mode for prompt analysis.
    """
    console.print("\n[bold cyan][Interactive Mode] AI Prompt Debugger - Interactive Mode[/bold cyan]")
    console.print("[dim]Type your prompt (press Ctrl+D or Ctrl+Z when done, 'quit' to exit)[/dim]\n")
    
    debugger = PromptDebugger()
    
    while True:
        try:
            console.print("[bold]Enter your prompt:[/bold]")
            lines = []
            while True:
                try:
                    line = input()
                    if line.lower() == 'quit':
                        console.print("[yellow]Goodbye![/yellow]")
                        return
                    lines.append(line)
                except EOFError:
                    break
            
            prompt = "\n".join(lines)
            
            if not prompt.strip():
                console.print("[yellow]Empty prompt, try again.[/yellow]\n")
                continue
            
            result = debugger.analyze(prompt)
            display_analysis_result(result, verbose=False)
            
            console.print("\n" + "="*60 + "\n")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break


@app.command()
def version():
    """Show version information"""
    console.print("\n[bold cyan]AI Prompt Debugger[/bold cyan]")
    console.print("Version: 1.0.0")
    console.print("Created by: Senior Development Team")
    console.print("License: MIT\n")


if __name__ == "__main__":
    app()
