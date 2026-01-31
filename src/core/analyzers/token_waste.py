"""
Token Waste Analyzer - Identifies unnecessary verbosity and suggests optimizations.
"""
from typing import List, Dict, Any, Tuple
import re
import tiktoken
from ..models.schemas import (
    PromptIssue,
    IssueCategory,
    IssueSeverity,
    TokenMetrics
)


class TokenWasteAnalyzer:
    """
    Analyzes prompts for token efficiency and identifies waste.
    """
    
    # Common redundant phrases
    REDUNDANT_PHRASES = [
        'please note that',
        'it is important to note that',
        'keep in mind that',
        'it should be noted that',
        'as mentioned above',
        'as previously stated',
        'in order to',
        'due to the fact that',
        'for the purpose of',
        'in the event that',
        'with regard to',
        'with respect to',
        'at this point in time',
        'in my opinion',
    ]
    
    # Filler words that add no value
    FILLER_WORDS = [
        'actually', 'basically', 'essentially', 'literally',
        'really', 'very', 'quite', 'rather', 'somewhat',
        'just', 'simply', 'merely'
    ]
    
    # Repetitive patterns
    REPETITION_PATTERNS = [
        r'(\b\w+\b)(?:\s+\w+){0,5}\s+\1',  # Same word within 5 words
        r'(\b\w{4,}\b)\s+\1',  # Immediate repetition of word 4+ chars
    ]
    
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize the analyzer.
        
        Args:
            model: Model name for token encoding (uses tiktoken)
        """
        # Use tiktoken for Claude models (GPT-4 encoding is close enough)
        try:
            self.encoder = tiktoken.encoding_for_model("gpt-4")
        except KeyError:
            self.encoder = tiktoken.get_encoding("cl100k_base")
        
        self.issues: List[PromptIssue] = []
    
    def analyze(self, prompt: str, cost_per_1k_tokens: float = 0.003) -> Tuple[List[PromptIssue], TokenMetrics]:
        """
        Analyze prompt for token waste and efficiency.
        
        Args:
            prompt: The prompt text to analyze
            cost_per_1k_tokens: Cost per 1000 tokens (default for Claude Sonnet)
            
        Returns:
            Tuple of (issues found, token metrics)
        """
        self.issues = []
        
        # Calculate tokens
        total_tokens = len(self.encoder.encode(prompt))
        
        # Detect various types of waste
        redundant_phrases = self._detect_redundant_phrases(prompt)
        filler_words = self._detect_filler_words(prompt)
        repetitions = self._detect_repetitions(prompt)
        verbose_sections = self._detect_verbose_sections(prompt)
        
        # Calculate compression opportunities
        compression_ops = self._calculate_compressions(
            prompt, redundant_phrases, filler_words, repetitions
        )
        
        # Calculate wasted tokens
        unnecessary_tokens = sum(op['tokens_saved'] for op in compression_ops)
        
        # Calculate efficiency
        token_efficiency = ((total_tokens - unnecessary_tokens) / total_tokens * 100) if total_tokens > 0 else 100
        
        # Calculate costs
        estimated_cost = (total_tokens / 1000) * cost_per_1k_tokens
        
        metrics = TokenMetrics(
            total_tokens=total_tokens,
            estimated_cost=round(estimated_cost, 4),
            unnecessary_tokens=unnecessary_tokens,
            token_efficiency=token_efficiency,
            redundant_phrases=redundant_phrases,
            compression_opportunities=compression_ops
        )
        
        return self.issues, metrics
    
    def _detect_redundant_phrases(self, prompt: str) -> List[str]:
        """Detect redundant or unnecessarily verbose phrases"""
        found_phrases = []
        prompt_lower = prompt.lower()
        
        for phrase in self.REDUNDANT_PHRASES:
            if phrase in prompt_lower:
                found_phrases.append(phrase)
                
                # Calculate token waste
                phrase_tokens = len(self.encoder.encode(phrase))
                
                severity = IssueSeverity.LOW
                if phrase_tokens > 5:
                    severity = IssueSeverity.MEDIUM
                
                # Suggest replacements
                replacements = self._get_phrase_replacement(phrase)
                
                self.issues.append(PromptIssue(
                    category=IssueCategory.TOKEN_WASTE,
                    severity=severity,
                    title=f"Redundant phrase: '{phrase}'",
                    description=f"This phrase uses {phrase_tokens} tokens but adds minimal value.",
                    suggestion=replacements['suggestion'],
                    examples=replacements['examples']
                ))
        
        return found_phrases
    
    def _detect_filler_words(self, prompt: str) -> List[str]:
        """Detect filler words that don't add meaning"""
        found_fillers = []
        words = prompt.split()
        
        for word in words:
            clean_word = word.lower().strip('.,!?;:')
            if clean_word in self.FILLER_WORDS:
                if clean_word not in found_fillers:
                    found_fillers.append(clean_word)
        
        if found_fillers:
            total_filler_tokens = sum(
                len(self.encoder.encode(f" {word}")) for word in found_fillers
            )
            
            self.issues.append(PromptIssue(
                category=IssueCategory.TOKEN_WASTE,
                severity=IssueSeverity.LOW,
                title=f"Filler words detected: {', '.join(found_fillers[:5])}",
                description=f"Found {len(found_fillers)} filler words wasting ~{total_filler_tokens} tokens.",
                suggestion="Remove filler words that don't add semantic value.",
                examples=[
                    f"Remove words like: {', '.join(found_fillers[:3])}",
                    "These words rarely change the AI's interpretation"
                ]
            ))
        
        return found_fillers
    
    def _detect_repetitions(self, prompt: str) -> List[str]:
        """Detect repeated words or phrases"""
        repetitions = []
        
        for pattern in self.REPETITION_PATTERNS:
            matches = re.finditer(pattern, prompt, re.IGNORECASE)
            for match in matches:
                repeated_text = match.group()
                if len(repeated_text) > 10:  # Only flag substantial repetitions
                    repetitions.append(repeated_text[:50])
                    
                    self.issues.append(PromptIssue(
                        category=IssueCategory.TOKEN_WASTE,
                        severity=IssueSeverity.MEDIUM,
                        title="Repetitive text detected",
                        description=f"Found repeated content: '{repeated_text[:50]}...'",
                        suggestion="Remove duplicate instructions or consolidate repeated concepts."
                    ))
        
        return repetitions
    
    def _detect_verbose_sections(self, prompt: str) -> List[Dict[str, Any]]:
        """Detect overly verbose sections that could be condensed"""
        verbose_sections = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', prompt)
        
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
            
            words = sentence.split()
            tokens = len(self.encoder.encode(sentence))
            
            # Flag very long sentences (>50 tokens) as potentially verbose
            if tokens > 50:
                avg_tokens_per_word = tokens / len(words) if words else 0
                
                # If tokens per word is high, might be technical (okay)
                # If low, might be unnecessarily verbose
                if avg_tokens_per_word < 1.5:
                    verbose_sections.append({
                        'sentence_number': i + 1,
                        'tokens': tokens,
                        'text': sentence[:100]
                    })
                    
                    self.issues.append(PromptIssue(
                        category=IssueCategory.TOKEN_WASTE,
                        severity=IssueSeverity.MEDIUM,
                        title=f"Verbose section detected (sentence {i+1})",
                        description=f"This sentence uses {tokens} tokens and may be overly verbose.",
                        suggestion="Consider breaking into multiple sentences or removing unnecessary details.",
                        location=f"Sentence {i+1}"
                    ))
        
        return verbose_sections
    
    def _calculate_compressions(
        self, 
        prompt: str,
        redundant_phrases: List[str],
        filler_words: List[str],
        repetitions: List[str]
    ) -> List[Dict[str, Any]]:
        """Calculate potential compression opportunities"""
        compressions = []
        
        # Redundant phrase compressions
        for phrase in redundant_phrases:
            phrase_tokens = len(self.encoder.encode(phrase))
            replacement = self._get_phrase_replacement(phrase)
            replacement_tokens = len(self.encoder.encode(replacement['replacement']))
            
            compressions.append({
                'type': 'redundant_phrase',
                'original': phrase,
                'replacement': replacement['replacement'],
                'tokens_saved': phrase_tokens - replacement_tokens
            })
        
        # Filler word compressions (removing them entirely)
        for word in filler_words:
            word_tokens = len(self.encoder.encode(f" {word}"))
            compressions.append({
                'type': 'filler_word',
                'original': word,
                'replacement': '',
                'tokens_saved': word_tokens
            })
        
        return compressions
    
    def _get_phrase_replacement(self, phrase: str) -> Dict[str, Any]:
        """Get suggested replacement for redundant phrase"""
        replacements = {
            'please note that': {
                'replacement': 'Note:',
                'suggestion': "Replace 'please note that' with 'Note:' or remove entirely",
                'examples': ['Note: The deadline is Friday', 'The deadline is Friday']
            },
            'it is important to note that': {
                'replacement': 'Important:',
                'suggestion': "Replace with 'Important:' or integrate into sentence",
                'examples': ['Important: Check formatting', 'Check formatting carefully']
            },
            'in order to': {
                'replacement': 'to',
                'suggestion': "Replace 'in order to' with 'to'",
                'examples': ['To complete this task...', 'Use this to achieve...']
            },
            'due to the fact that': {
                'replacement': 'because',
                'suggestion': "Replace 'due to the fact that' with 'because' or 'since'",
                'examples': ['Because the system...', 'Since we need...']
            },
        }
        
        return replacements.get(phrase, {
            'replacement': '',
            'suggestion': f"Consider removing or simplifying '{phrase}'",
            'examples': ['Direct statement without preamble']
        })
