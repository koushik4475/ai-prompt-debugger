"""
Core data models for the AI Prompt Debugger.
Provides type-safe data structures for analysis results.
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class IssueSeverity(str, Enum):
    """Severity levels for prompt issues"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueCategory(str, Enum):
    """Categories of prompt issues"""
    AMBIGUITY = "ambiguity"
    CONTRADICTION = "contradiction"
    TOKEN_WASTE = "token_waste"
    CLARITY = "clarity"
    STRUCTURE = "structure"
    SECURITY = "security"
    CONTEXT = "context"
    INSTRUCTION = "instruction"


class PromptIssue(BaseModel):
    """Represents a single issue found in a prompt"""
    category: IssueCategory
    severity: IssueSeverity
    title: str
    description: str
    location: Optional[str] = None  # Line number or section
    suggestion: Optional[str] = None
    examples: Optional[List[str]] = None
    
    class Config:
        frozen = True


class TokenMetrics(BaseModel):
    """Token usage and efficiency metrics"""
    total_tokens: int
    estimated_cost: float
    unnecessary_tokens: int
    token_efficiency: float = Field(ge=0, le=100)  # Percentage
    redundant_phrases: List[str] = Field(default_factory=list)
    compression_opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    
    @validator('token_efficiency')
    def validate_efficiency(cls, v):
        return round(v, 2)


class AmbiguityMetrics(BaseModel):
    """Metrics related to prompt ambiguity"""
    ambiguity_score: float = Field(ge=0, le=100)  # Lower is better
    vague_terms: List[str] = Field(default_factory=list)
    conflicting_instructions: List[tuple[str, str]] = Field(default_factory=list)
    undefined_terms: List[str] = Field(default_factory=list)
    clarity_score: float = Field(ge=0, le=100)  # Higher is better


class SuccessPrediction(BaseModel):
    """Predicted success metrics for the prompt"""
    success_probability: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=100)
    risk_factors: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    recommended_improvements: List[str] = Field(default_factory=list)


class SecurityMetrics(BaseModel):
    """Security and safety metrics"""
    security_score: float = Field(ge=0, le=100)
    potential_injections: List[str] = Field(default_factory=list)
    jailbreak_attempts: List[str] = Field(default_factory=list)
    sensitive_data_detected: bool = False
    sanitization_issues: List[str] = Field(default_factory=list)


class PromptAnalysisResult(BaseModel):
    """Complete analysis result for a prompt"""
    prompt_text: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Analysis results
    issues: List[PromptIssue] = Field(default_factory=list)
    metrics: TokenMetrics
    ambiguity: AmbiguityMetrics
    predictions: SuccessPrediction
    security: SecurityMetrics
    
    # Overall scores
    overall_quality_score: float = Field(ge=0, le=100)
    overall_grade: str  # A, B, C, D, F
    
    @validator('overall_grade')
    def validate_grade(cls, v):
        if v not in ['A', 'B', 'C', 'D', 'F']:
            raise ValueError("Grade must be A, B, C, D, or F")
        return v
    
    def get_critical_issues(self) -> List[PromptIssue]:
        """Get all critical severity issues"""
        return [i for i in self.issues if i.severity == IssueSeverity.CRITICAL]
    
    def get_issues_by_category(self, category: IssueCategory) -> List[PromptIssue]:
        """Get all issues of a specific category"""
        return [i for i in self.issues if i.category == category]


class PromptComparison(BaseModel):
    """Comparison between two prompts"""
    prompt_a: PromptAnalysisResult
    prompt_b: PromptAnalysisResult
    
    quality_difference: float
    token_difference: int
    cost_difference: float
    
    better_prompt: str  # "A" or "B"
    comparison_summary: str
    key_differences: List[str] = Field(default_factory=list)


class AnalyzerConfig(BaseModel):
    """Configuration for the prompt analyzer"""
    enable_ambiguity_detection: bool = True
    enable_token_analysis: bool = True
    enable_success_prediction: bool = True
    enable_security_scanning: bool = True
    
    strict_mode: bool = False  # Stricter analysis
    token_price_per_1k: float = 0.003  # Default pricing
    
    min_severity_to_report: IssueSeverity = IssueSeverity.LOW
    max_prompt_length: int = 200000  # Maximum tokens to analyze
