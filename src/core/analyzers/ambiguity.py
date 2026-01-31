"""
Ambiguity Detector - Identifies conflicting instructions, vague terms, and unclear directives.
"""
from typing import List, Tuple, Set
import re
from ..models.schemas import (
    PromptIssue,
    IssueCategory,
    IssueSeverity,
    AmbiguityMetrics
)


class AmbiguityDetector:
    """
    Analyzes prompts for ambiguity, contradictions, and unclear instructions.
    """
    
    # Patterns that often indicate vague language
    VAGUE_PATTERNS = [
        r'\b(some|many|few|several|various|numerous)\b',
        r'\b(might|maybe|perhaps|possibly|probably)\b',
        r'\b(things|stuff|etc\.?)\b',
        r'\b(good|bad|better|best)\b(?!\s+(?:practice|example))',
        r'\b(appropriate|suitable|relevant)\b',
    ]
    
    # Contradictory instruction pairs
    CONTRADICTORY_PAIRS = [
        ('concise', 'detailed'),
        ('brief', 'comprehensive'),
        ('short', 'extensive'),
        ('simple', 'complex'),
        ('formal', 'casual'),
        ('technical', 'layman'),
        ('creative', 'factual'),
        ('subjective', 'objective'),
    ]
    
    # Indefinite quantifiers that need clarification
    INDEFINITE_QUANTIFIERS = [
        'some', 'many', 'few', 'several', 'multiple',
        'various', 'numerous', 'a lot', 'plenty'
    ]
    
    def __init__(self):
        self.issues: List[PromptIssue] = []
    
    def analyze(self, prompt: str) -> Tuple[List[PromptIssue], AmbiguityMetrics]:
        """
        Perform comprehensive ambiguity analysis.
        
        Args:
            prompt: The prompt text to analyze
            
        Returns:
            Tuple of (issues found, ambiguity metrics)
        """
        self.issues = []
        
        # Run all detection methods
        vague_terms = self._detect_vague_language(prompt)
        conflicts = self._detect_contradictions(prompt)
        undefined = self._detect_undefined_terms(prompt)
        unclear_instructions = self._detect_unclear_instructions(prompt)
        
        # Calculate scores
        ambiguity_score = self._calculate_ambiguity_score(prompt, vague_terms, conflicts)
        clarity_score = 100 - ambiguity_score
        
        metrics = AmbiguityMetrics(
            ambiguity_score=ambiguity_score,
            vague_terms=vague_terms,
            conflicting_instructions=conflicts,
            undefined_terms=undefined,
            clarity_score=clarity_score
        )
        
        return self.issues, metrics
    
    def _detect_vague_language(self, prompt: str) -> List[str]:
        """Detect vague or ambiguous language patterns"""
        vague_terms = []
        prompt_lower = prompt.lower()
        
        for pattern in self.VAGUE_PATTERNS:
            matches = re.finditer(pattern, prompt_lower, re.IGNORECASE)
            for match in matches:
                term = match.group()
                if term not in vague_terms:
                    vague_terms.append(term)
                    
                    severity = IssueSeverity.MEDIUM
                    if term in ['things', 'stuff']:
                        severity = IssueSeverity.HIGH
                    
                    self.issues.append(PromptIssue(
                        category=IssueCategory.AMBIGUITY,
                        severity=severity,
                        title=f"Vague term detected: '{term}'",
                        description=f"The term '{term}' is ambiguous and may lead to inconsistent interpretations.",
                        suggestion=f"Replace '{term}' with specific, measurable criteria.",
                        examples=[
                            f"Instead of 'some examples', specify 'provide 3 examples'",
                            f"Instead of 'good quality', define what 'good' means in this context"
                        ]
                    ))
        
        return vague_terms
    
    def _detect_contradictions(self, prompt: str) -> List[Tuple[str, str]]:
        """Detect contradictory instructions in the prompt"""
        conflicts = []
        prompt_lower = prompt.lower()
        
        for term1, term2 in self.CONTRADICTORY_PAIRS:
            # Look for both terms in the prompt
            has_term1 = term1 in prompt_lower
            has_term2 = term2 in prompt_lower
            
            if has_term1 and has_term2:
                # Check if they're in different instructions (not in same sentence)
                sentences = prompt.split('.')
                term1_sentences = [i for i, s in enumerate(sentences) if term1 in s.lower()]
                term2_sentences = [i for i, s in enumerate(sentences) if term2 in s.lower()]
                
                # If in different sentences, likely a conflict
                if term1_sentences and term2_sentences and term1_sentences[0] != term2_sentences[0]:
                    conflicts.append((term1, term2))
                    
                    self.issues.append(PromptIssue(
                        category=IssueCategory.CONTRADICTION,
                        severity=IssueSeverity.HIGH,
                        title=f"Contradictory instructions: '{term1}' vs '{term2}'",
                        description=f"The prompt contains both '{term1}' and '{term2}' which may conflict.",
                        suggestion=f"Clarify which requirement takes precedence or reconcile the conflict.",
                        examples=[
                            f"If you want both, explain: 'Be {term1} in structure but {term2} in examples'",
                            f"Or prioritize: 'Prefer {term1} output, but include {term2} sections if needed'"
                        ]
                    ))
        
        return conflicts
    
    def _detect_undefined_terms(self, prompt: str) -> List[str]:
        """Detect domain-specific or technical terms that may need definition"""
        undefined = []
        
        # Look for capitalized technical terms or acronyms
        # This is a simplified heuristic
        words = prompt.split()
        
        for word in words:
            # Check for acronyms (2-6 uppercase letters)
            if re.match(r'^[A-Z]{2,6}$', word) and word not in ['USA', 'UK', 'US', 'AI', 'ML', 'API']:
                if word not in undefined:
                    undefined.append(word)
                    
                    self.issues.append(PromptIssue(
                        category=IssueCategory.CLARITY,
                        severity=IssueSeverity.LOW,
                        title=f"Potentially undefined acronym: '{word}'",
                        description=f"The acronym '{word}' may not be universally understood.",
                        suggestion=f"Define '{word}' on first use or ensure it's well-known in context."
                    ))
        
        return undefined
    
    def _detect_unclear_instructions(self, prompt: str) -> List[PromptIssue]:
        """Detect instructions that lack clarity or specificity"""
        unclear_issues = []
        
        # Check for indefinite quantifiers without clarification
        for quantifier in self.INDEFINITE_QUANTIFIERS:
            pattern = rf'\b{quantifier}\b\s+\w+'
            matches = re.finditer(pattern, prompt, re.IGNORECASE)
            
            for match in matches:
                phrase = match.group()
                
                issue = PromptIssue(
                    category=IssueCategory.INSTRUCTION,
                    severity=IssueSeverity.MEDIUM,
                    title=f"Indefinite quantifier: '{phrase}'",
                    description=f"'{phrase}' is imprecise and may lead to variable outputs.",
                    suggestion=f"Specify an exact number or range instead of '{quantifier}'.",
                    examples=[
                        f"Instead of '{phrase}', use 'exactly 5 {phrase.split()[1]}'",
                        f"Or provide a range: 'between 3-7 {phrase.split()[1]}'"
                    ]
                )
                unclear_issues.append(issue)
                self.issues.append(issue)
        
        return unclear_issues
    
    def _calculate_ambiguity_score(
        self, 
        prompt: str, 
        vague_terms: List[str],
        conflicts: List[Tuple[str, str]]
    ) -> float:
        """
        Calculate overall ambiguity score (0-100, lower is better).
        
        Factors:
        - Number of vague terms relative to prompt length
        - Number of conflicts
        - Clarity of instructions
        """
        words = prompt.split()
        if not words:
            return 0.0
        
        # Base score on vague term density
        vague_density = (len(vague_terms) / len(words)) * 100
        vague_score = min(vague_density * 5, 50)  # Max 50 points
        
        # Add points for conflicts (each conflict adds significant ambiguity)
        conflict_score = min(len(conflicts) * 15, 40)  # Max 40 points
        
        # Check instruction structure (sentences with imperatives)
        imperative_count = len(re.findall(r'\b(do|make|create|write|generate|provide)\b', 
                                          prompt.lower()))
        instruction_clarity = max(0, 10 - imperative_count)  # Max 10 points if no clear instructions
        
        total_score = vague_score + conflict_score + instruction_clarity
        return min(total_score, 100)
