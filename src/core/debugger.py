"""
Main PromptDebugger class - Orchestrates all analysis engines.
"""
from typing import Optional
from .models.schemas import (
    PromptAnalysisResult,
    PromptComparison,
    AnalyzerConfig,
    PromptIssue
)
from .analyzers.ambiguity import AmbiguityDetector
from .analyzers.token_waste import TokenWasteAnalyzer
from .analyzers.success_prediction import SuccessPredictor
from .analyzers.security import SecurityScanner


class PromptDebugger:
    """
    Main orchestrator for prompt analysis.
    Coordinates multiple analysis engines to provide comprehensive feedback.
    """
    
    def __init__(self, config: Optional[AnalyzerConfig] = None):
        """
        Initialize the prompt debugger.
        
        Args:
            config: Configuration for analysis engines
        """
        self.config = config or AnalyzerConfig()
        
        # Initialize analyzers
        self.ambiguity_detector = AmbiguityDetector()
        self.token_analyzer = TokenWasteAnalyzer()
        self.success_predictor = SuccessPredictor()
        self.security_scanner = SecurityScanner()
    
    def analyze(self, prompt: str) -> PromptAnalysisResult:
        """
        Perform comprehensive analysis on a prompt.
        
        Args:
            prompt: The prompt text to analyze
            
        Returns:
            Complete analysis result with all metrics and issues
        """
        # Validate input
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        if len(prompt) > self.config.max_prompt_length:
            raise ValueError(
                f"Prompt exceeds maximum length of {self.config.max_prompt_length} characters"
            )
        
        all_issues = []
        
        # Run ambiguity detection
        if self.config.enable_ambiguity_detection:
            ambiguity_issues, ambiguity_metrics = self.ambiguity_detector.analyze(prompt)
            all_issues.extend(ambiguity_issues)
        else:
            ambiguity_metrics = None
        
        # Run token analysis
        if self.config.enable_token_analysis:
            token_issues, token_metrics = self.token_analyzer.analyze(
                prompt, 
                self.config.token_price_per_1k
            )
            all_issues.extend(token_issues)
        else:
            token_metrics = None
        
        # Run success prediction
        if self.config.enable_success_prediction:
            success_issues, success_prediction = self.success_predictor.analyze(prompt)
            all_issues.extend(success_issues)
        else:
            success_prediction = None
        
        # Run security scan
        if self.config.enable_security_scanning:
            security_issues, security_metrics = self.security_scanner.analyze(prompt)
            all_issues.extend(security_issues)
        else:
            security_metrics = None
        
        # Filter issues by minimum severity
        filtered_issues = self._filter_issues_by_severity(all_issues)
        
        # Calculate overall scores
        overall_quality = self._calculate_overall_quality(
            ambiguity_metrics,
            token_metrics,
            success_prediction,
            security_metrics
        )
        
        grade = self._assign_grade(overall_quality)
        
        return PromptAnalysisResult(
            prompt_text=prompt,
            issues=filtered_issues,
            metrics=token_metrics,
            ambiguity=ambiguity_metrics,
            predictions=success_prediction,
            security=security_metrics,
            overall_quality_score=overall_quality,
            overall_grade=grade
        )
    
    def compare(self, prompt_a: str, prompt_b: str) -> PromptComparison:
        """
        Compare two prompts and identify which is better.
        
        Args:
            prompt_a: First prompt to compare
            prompt_b: Second prompt to compare
            
        Returns:
            Comparison result with analysis of both prompts
        """
        result_a = self.analyze(prompt_a)
        result_b = self.analyze(prompt_b)
        
        # Calculate differences
        quality_diff = result_b.overall_quality_score - result_a.overall_quality_score
        token_diff = result_b.metrics.total_tokens - result_a.metrics.total_tokens
        cost_diff = result_b.metrics.estimated_cost - result_a.metrics.estimated_cost
        
        # Determine better prompt
        if quality_diff > 5:
            better = "B"
        elif quality_diff < -5:
            better = "A"
        else:
            # Quality is similar, prefer fewer tokens
            better = "A" if token_diff > 0 else "B"
        
        # Generate comparison summary
        summary = self._generate_comparison_summary(
            result_a, result_b, quality_diff, token_diff, cost_diff
        )
        
        # Identify key differences
        key_differences = self._identify_key_differences(result_a, result_b)
        
        return PromptComparison(
            prompt_a=result_a,
            prompt_b=result_b,
            quality_difference=quality_diff,
            token_difference=token_diff,
            cost_difference=cost_diff,
            better_prompt=better,
            comparison_summary=summary,
            key_differences=key_differences
        )
    
    def _filter_issues_by_severity(self, issues: list[PromptIssue]) -> list[PromptIssue]:
        """Filter issues based on configured minimum severity"""
        severity_order = {
            'info': 0,
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        
        min_level = severity_order.get(self.config.min_severity_to_report.value, 0)
        
        return [
            issue for issue in issues
            if severity_order.get(issue.severity.value, 0) >= min_level
        ]
    
    def _calculate_overall_quality(
        self,
        ambiguity,
        token_metrics,
        success_prediction,
        security_metrics
    ) -> float:
        """Calculate overall quality score from all metrics"""
        scores = []
        weights = []
        
        if ambiguity:
            scores.append(ambiguity.clarity_score)
            weights.append(0.25)
        
        if token_metrics:
            scores.append(token_metrics.token_efficiency)
            weights.append(0.20)
        
        if success_prediction:
            scores.append(success_prediction.success_probability)
            weights.append(0.35)
        
        if security_metrics:
            scores.append(security_metrics.security_score)
            weights.append(0.20)
        
        if not scores:
            return 0.0
        
        # Weighted average
        total_weight = sum(weights)
        weighted_sum = sum(s * w for s, w in zip(scores, weights))
        
        return round(weighted_sum / total_weight, 2)
    
    def _assign_grade(self, score: float) -> str:
        """Convert quality score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_comparison_summary(
        self,
        result_a: PromptAnalysisResult,
        result_b: PromptAnalysisResult,
        quality_diff: float,
        token_diff: int,
        cost_diff: float
    ) -> str:
        """Generate human-readable comparison summary"""
        summary_parts = []
        
        # Quality comparison
        if abs(quality_diff) < 5:
            summary_parts.append("Both prompts have similar overall quality")
        else:
            better = "Prompt B" if quality_diff > 0 else "Prompt A"
            summary_parts.append(
                f"{better} has significantly better quality "
                f"({abs(quality_diff):.1f} point difference)"
            )
        
        # Token comparison
        if abs(token_diff) > 50:
            more_tokens = "Prompt B" if token_diff > 0 else "Prompt A"
            summary_parts.append(
                f"{more_tokens} uses {abs(token_diff)} more tokens "
                f"(${abs(cost_diff):.4f} cost difference)"
            )
        
        # Critical issues
        critical_a = len(result_a.get_critical_issues())
        critical_b = len(result_b.get_critical_issues())
        
        if critical_a != critical_b:
            fewer = "Prompt B" if critical_b < critical_a else "Prompt A"
            summary_parts.append(
                f"{fewer} has fewer critical issues "
                f"({min(critical_a, critical_b)} vs {max(critical_a, critical_b)})"
            )
        
        return ". ".join(summary_parts) + "."
    
    def _identify_key_differences(
        self,
        result_a: PromptAnalysisResult,
        result_b: PromptAnalysisResult
    ) -> list[str]:
        """Identify key differences between two prompts"""
        differences = []
        
        # Compare clarity
        clarity_diff = result_b.ambiguity.clarity_score - result_a.ambiguity.clarity_score
        if abs(clarity_diff) > 10:
            better = "B" if clarity_diff > 0 else "A"
            differences.append(
                f"Prompt {better} is significantly clearer ({abs(clarity_diff):.1f} points)"
            )
        
        # Compare success probability
        success_diff = result_b.predictions.success_probability - result_a.predictions.success_probability
        if abs(success_diff) > 10:
            better = "B" if success_diff > 0 else "A"
            differences.append(
                f"Prompt {better} has higher success probability ({abs(success_diff):.1f}% better)"
            )
        
        # Compare token efficiency
        efficiency_diff = result_b.metrics.token_efficiency - result_a.metrics.token_efficiency
        if abs(efficiency_diff) > 10:
            better = "B" if efficiency_diff > 0 else "A"
            differences.append(
                f"Prompt {better} is more token-efficient ({abs(efficiency_diff):.1f}% better)"
            )
        
        # Compare security
        security_diff = result_b.security.security_score - result_a.security.security_score
        if abs(security_diff) > 10:
            better = "B" if security_diff > 0 else "A"
            differences.append(
                f"Prompt {better} is more secure ({abs(security_diff):.1f} points better)"
            )
        
        return differences
