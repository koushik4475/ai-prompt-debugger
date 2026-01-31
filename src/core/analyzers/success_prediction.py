"""
Success Predictor - Predicts likelihood of getting desired output based on prompt patterns.
"""
from typing import List, Tuple, Dict, Any
import re
from ..models.schemas import (
    PromptIssue,
    IssueCategory,
    IssueSeverity,
    SuccessPrediction
)


class SuccessPredictor:
    """
    Predicts success probability and identifies strengths/weaknesses in prompts.
    """
    
    # Positive indicators (increase success probability)
    POSITIVE_PATTERNS = {
        'specific_format': r'(format|structure|template|example output)',
        'clear_constraints': r'(must|should|exactly|between \d+ and \d+)',
        'output_examples': r'(example:|for example|such as)',
        'step_by_step': r'(step|first|then|finally|process)',
        'context_provided': r'(context|background|situation|scenario)',
        'role_definition': r'(you are|act as|as a|role)',
        'success_criteria': r'(success|correct|good result|valid)',
    }
    
    # Negative indicators (decrease success probability)
    NEGATIVE_PATTERNS = {
        'overly_complex': r'\b\w{20,}\b',  # Very long words
        'too_many_requirements': r'(?:and|also|additionally|furthermore)',
        'contradictory_language': r'(but|however|although|except)',
        'open_ended': r'(maybe|perhaps|might|could|anything)',
    }
    
    # Quality indicators
    QUALITY_MARKERS = {
        'has_examples': 10,
        'has_constraints': 15,
        'has_format': 15,
        'has_context': 10,
        'has_clear_goal': 20,
        'has_role': 5,
        'step_by_step': 10,
    }
    
    def __init__(self):
        self.issues: List[PromptIssue] = []
    
    def analyze(self, prompt: str) -> Tuple[List[PromptIssue], SuccessPrediction]:
        """
        Predict success probability based on prompt quality.
        
        Args:
            prompt: The prompt text to analyze
            
        Returns:
            Tuple of (issues found, success prediction)
        """
        self.issues = []
        
        # Analyze prompt structure
        structure_score = self._analyze_structure(prompt)
        
        # Identify strengths and weaknesses
        strengths = self._identify_strengths(prompt)
        risk_factors = self._identify_risk_factors(prompt)
        
        # Calculate scores
        success_prob = self._calculate_success_probability(
            prompt, structure_score, len(strengths), len(risk_factors)
        )
        
        confidence = self._calculate_confidence(prompt, success_prob)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            prompt, strengths, risk_factors
        )
        
        prediction = SuccessPrediction(
            success_probability=success_prob,
            confidence_score=confidence,
            risk_factors=risk_factors,
            strengths=strengths,
            recommended_improvements=recommendations
        )
        
        return self.issues, prediction
    
    def _analyze_structure(self, prompt: str) -> float:
        """Analyze overall prompt structure quality"""
        score = 0.0
        
        # Check for positive patterns
        for pattern_name, pattern in self.POSITIVE_PATTERNS.items():
            if re.search(pattern, prompt, re.IGNORECASE):
                score += self.QUALITY_MARKERS.get(pattern_name.replace('_pattern', ''), 5)
        
        # Penalize for negative patterns
        for pattern_name, pattern in self.NEGATIVE_PATTERNS.items():
            matches = len(re.findall(pattern, prompt, re.IGNORECASE))
            if matches > 3:  # Too many instances
                score -= min(matches * 2, 15)
        
        # Check length appropriateness
        words = prompt.split()
        if len(words) < 10:
            score -= 20
            self.issues.append(PromptIssue(
                category=IssueCategory.STRUCTURE,
                severity=IssueSeverity.HIGH,
                title="Prompt too short",
                description="Very short prompts often lack necessary context and constraints.",
                suggestion="Provide more context, examples, and clear success criteria."
            ))
        elif len(words) > 500:
            score -= 10
            self.issues.append(PromptIssue(
                category=IssueCategory.STRUCTURE,
                severity=IssueSeverity.MEDIUM,
                title="Prompt may be too long",
                description="Very long prompts can dilute key instructions.",
                suggestion="Consider breaking into sections or removing less critical details."
            ))
        
        return max(min(score, 100), 0)
    
    def _identify_strengths(self, prompt: str) -> List[str]:
        """Identify what the prompt does well"""
        strengths = []
        prompt_lower = prompt.lower()
        
        # Check for examples
        if re.search(r'(example|for instance|such as)', prompt_lower):
            strengths.append("Provides concrete examples")
        
        # Check for clear output format
        if re.search(r'(format|structure|output.*format|return.*format)', prompt_lower):
            strengths.append("Specifies output format")
        
        # Check for constraints
        if re.search(r'(must|should|required|exactly|between.*and)', prompt_lower):
            strengths.append("Contains clear constraints")
        
        # Check for context
        if re.search(r'(context|background|scenario|situation)', prompt_lower):
            strengths.append("Provides relevant context")
        
        # Check for role assignment
        if re.search(r'(you are|act as|as a|your role)', prompt_lower):
            strengths.append("Defines AI role clearly")
        
        # Check for step-by-step
        if re.search(r'(step|first|then|next|finally)', prompt_lower):
            strengths.append("Uses step-by-step instructions")
        
        # Check for success criteria
        if re.search(r'(success|correct|good|valid|acceptable)', prompt_lower):
            strengths.append("Defines success criteria")
        
        # Check for delimiters (good for structure)
        if re.search(r'(---|###|===|\*\*\*)', prompt):
            strengths.append("Uses clear section delimiters")
        
        return strengths
    
    def _identify_risk_factors(self, prompt: str) -> List[str]:
        """Identify potential issues that might affect success"""
        risks = []
        prompt_lower = prompt.lower()
        
        # Missing clear goal
        if not re.search(r'(create|generate|write|make|produce|provide|give)', prompt_lower):
            risks.append("No clear action verb - ambiguous goal")
            self.issues.append(PromptIssue(
                category=IssueCategory.STRUCTURE,
                severity=IssueSeverity.HIGH,
                title="Unclear goal or objective",
                description="Prompt lacks a clear action verb or goal statement.",
                suggestion="Start with a clear instruction like 'Create...', 'Generate...', or 'Write...'"
            ))
        
        # No examples when needed
        if 'example' not in prompt_lower and len(prompt.split()) > 50:
            risks.append("Complex prompt without examples")
            self.issues.append(PromptIssue(
                category=IssueCategory.STRUCTURE,
                severity=IssueSeverity.MEDIUM,
                title="Missing examples for complex task",
                description="Complex prompts benefit from concrete examples.",
                suggestion="Add 1-2 examples of desired output format or style."
            ))
        
        # Too open-ended
        open_ended_count = len(re.findall(
            r'(any|anything|whatever|however|maybe|perhaps)', 
            prompt_lower
        ))
        if open_ended_count > 3:
            risks.append(f"Too many open-ended terms ({open_ended_count} instances)")
            self.issues.append(PromptIssue(
                category=IssueCategory.STRUCTURE,
                severity=IssueSeverity.MEDIUM,
                title="Overly open-ended instructions",
                description="Too many open-ended terms may lead to inconsistent outputs.",
                suggestion="Add specific constraints or preferred approaches."
            ))
        
        # No output format specified
        if not re.search(r'(format|json|xml|markdown|list|table|code)', prompt_lower):
            if len(prompt.split()) > 30:
                risks.append("No output format specified")
                self.issues.append(PromptIssue(
                    category=IssueCategory.STRUCTURE,
                    severity=IssueSeverity.MEDIUM,
                    title="Output format not specified",
                    description="Specifying format increases consistency.",
                    suggestion="Add format instructions like 'Respond in JSON format' or 'Use markdown formatting'."
                ))
        
        # Contradictory instructions detected
        contradictions = len(re.findall(
            r'(but|however|although|except|unless)', 
            prompt_lower
        ))
        if contradictions > 2:
            risks.append(f"Multiple contradictory statements ({contradictions})")
        
        # Missing context for complex topics
        technical_terms = len(re.findall(r'\b[A-Z]{2,}\b', prompt))
        has_context = bool(re.search(r'(context|background|about|regarding)', prompt_lower))
        if technical_terms > 3 and not has_context:
            risks.append("Technical terms without context")
            self.issues.append(PromptIssue(
                category=IssueCategory.CONTEXT,
                severity=IssueSeverity.MEDIUM,
                title="Technical terms without context",
                description="Found technical terms/acronyms without background context.",
                suggestion="Provide context or definitions for domain-specific terms."
            ))
        
        return risks
    
    def _calculate_success_probability(
        self, 
        prompt: str,
        structure_score: float,
        num_strengths: int,
        num_risks: int
    ) -> float:
        """Calculate overall success probability"""
        
        # Base score from structure
        base_score = structure_score * 0.4
        
        # Add points for strengths (max 40 points)
        strength_score = min(num_strengths * 6, 40)
        
        # Subtract points for risks (max -30 points)
        risk_penalty = min(num_risks * 5, 30)
        
        # Length penalty/bonus
        words = len(prompt.split())
        if 20 <= words <= 200:
            length_bonus = 15
        elif 10 <= words < 20 or 200 < words <= 300:
            length_bonus = 5
        else:
            length_bonus = 0
        
        total = base_score + strength_score + length_bonus - risk_penalty
        return max(min(total, 100), 0)
    
    def _calculate_confidence(self, prompt: str, success_prob: float) -> float:
        """Calculate confidence in the prediction"""
        
        # More data = higher confidence
        words = len(prompt.split())
        
        if words < 10:
            base_confidence = 50
        elif words < 50:
            base_confidence = 70
        else:
            base_confidence = 85
        
        # Extreme probabilities are less confident
        if 20 < success_prob < 80:
            prob_confidence = 100
        else:
            prob_confidence = 70
        
        return (base_confidence + prob_confidence) / 2
    
    def _generate_recommendations(
        self,
        prompt: str,
        strengths: List[str],
        risks: List[str]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Recommend based on missing strengths
        all_strength_types = {
            "Provides concrete examples",
            "Specifies output format",
            "Contains clear constraints",
            "Provides relevant context",
            "Defines AI role clearly",
            "Uses step-by-step instructions",
            "Defines success criteria"
        }
        
        missing_strengths = all_strength_types - set(strengths)
        
        if "Provides concrete examples" in missing_strengths:
            recommendations.append(
                "Add 1-2 concrete examples of desired output to improve clarity"
            )
        
        if "Specifies output format" in missing_strengths:
            recommendations.append(
                "Specify output format (JSON, markdown, list, etc.) for consistency"
            )
        
        if "Contains clear constraints" in missing_strengths:
            recommendations.append(
                "Add explicit constraints (length, style, must/should requirements)"
            )
        
        if "Defines AI role clearly" in missing_strengths:
            recommendations.append(
                "Consider adding role context (e.g., 'You are an expert in...')"
            )
        
        # Address specific risks
        if "No clear action verb" in str(risks):
            recommendations.append(
                "Start with clear action verb: Create, Generate, Write, Analyze, etc."
            )
        
        if len(recommendations) == 0:
            recommendations.append(
                "Prompt structure is solid - consider A/B testing variations"
            )
        
        return recommendations[:5]  # Limit to top 5
