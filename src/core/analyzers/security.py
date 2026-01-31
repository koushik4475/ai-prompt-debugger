"""
Security Scanner - Detects potential prompt injections, jailbreaks, and safety issues.
"""
from typing import List, Tuple, Dict
import re
from ..models.schemas import (
    PromptIssue,
    IssueCategory,
    IssueSeverity,
    SecurityMetrics
)


class SecurityScanner:
    """
    Scans prompts for security vulnerabilities and safety concerns.
    """
    
    # Known prompt injection patterns
    INJECTION_PATTERNS = [
        r'ignore\s+(previous|all|above|prior)\s+(instructions|prompts|rules)',
        r'disregard\s+(previous|all|above|prior)',
        r'forget\s+(everything|all|what\s+you\s+know)',
        r'new\s+(instructions|rules|system\s+prompt)',
        r'system\s*:\s*(you\s+are\s+now|override)',
        r'---\s*BEGIN\s+NEW\s+PROMPT',
        r'sudo\s+mode',
        r'developer\s+mode',
        r'admin\s+(mode|access|override)',
    ]
    
    # Jailbreak attempt patterns
    JAILBREAK_PATTERNS = [
        r'(DAN|jailbreak|unrestricted|evil\s+mode)',
        r'pretend\s+you\s+(have\s+no|don\'t\s+have)\s+(rules|restrictions|limitations)',
        r'act\s+as\s+if\s+you\s+(have|don\'t\s+have)\s+no\s+(ethics|morals|restrictions)',
        r'roleplay\s+(without|ignore)\s+(ethics|safety|restrictions)',
        r'hypothetically\s+speaking.*?(illegal|unethical|harmful)',
    ]
    
    # Sensitive data patterns
    SENSITIVE_PATTERNS = {
        'api_key': r'(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
        'password': r'password\s*[:=]\s*["\']?([^\s"\']+)["\']?',
        'token': r'(access[_-]?token|bearer)\s*[:=]\s*["\']?([a-zA-Z0-9._-]{20,})["\']?',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
    }
    
    # Malicious intent indicators
    MALICIOUS_INDICATORS = [
        r'(how\s+to\s+)?(hack|exploit|bypass|crack|break\s+into)',
        r'(generate|create|make)\s+(malware|virus|ransomware|exploit)',
        r'(bypass|evade|avoid)\s+(security|detection|firewall)',
        r'(steal|exfiltrate|extract)\s+(data|credentials|passwords)',
    ]
    
    def __init__(self):
        self.issues: List[PromptIssue] = []
    
    def analyze(self, prompt: str) -> Tuple[List[PromptIssue], SecurityMetrics]:
        """
        Scan prompt for security and safety issues.
        
        Args:
            prompt: The prompt text to analyze
            
        Returns:
            Tuple of (issues found, security metrics)
        """
        self.issues = []
        
        # Run security checks
        injections = self._detect_prompt_injections(prompt)
        jailbreaks = self._detect_jailbreak_attempts(prompt)
        sensitive_data = self._detect_sensitive_data(prompt)
        malicious = self._detect_malicious_intent(prompt)
        sanitization = self._check_input_sanitization(prompt)
        
        # Calculate security score
        security_score = self._calculate_security_score(
            injections, jailbreaks, len(sensitive_data), malicious, sanitization
        )
        
        metrics = SecurityMetrics(
            security_score=security_score,
            potential_injections=injections,
            jailbreak_attempts=jailbreaks,
            sensitive_data_detected=len(sensitive_data) > 0,
            sanitization_issues=sanitization
        )
        
        return self.issues, metrics
    
    def _detect_prompt_injections(self, prompt: str) -> List[str]:
        """Detect potential prompt injection attempts"""
        injections = []
        prompt_lower = prompt.lower()
        
        for pattern in self.INJECTION_PATTERNS:
            matches = re.finditer(pattern, prompt_lower, re.IGNORECASE)
            for match in matches:
                injection_text = match.group()
                injections.append(injection_text)
                
                self.issues.append(PromptIssue(
                    category=IssueCategory.SECURITY,
                    severity=IssueSeverity.CRITICAL,
                    title=f"Potential prompt injection detected",
                    description=f"Found suspicious pattern: '{injection_text}' which may attempt to override system instructions.",
                    suggestion="Remove or rephrase this instruction. If legitimate, use clear delimiters and context.",
                    examples=[
                        "Use clear section markers: '--- User Input ---'",
                        "Explicitly state: 'The following is user-provided content:'"
                    ]
                ))
        
        return injections
    
    def _detect_jailbreak_attempts(self, prompt: str) -> List[str]:
        """Detect attempts to bypass AI safety measures"""
        jailbreaks = []
        prompt_lower = prompt.lower()
        
        for pattern in self.JAILBREAK_PATTERNS:
            matches = re.finditer(pattern, prompt_lower, re.IGNORECASE)
            for match in matches:
                jailbreak_text = match.group()
                jailbreaks.append(jailbreak_text)
                
                self.issues.append(PromptIssue(
                    category=IssueCategory.SECURITY,
                    severity=IssueSeverity.CRITICAL,
                    title="Potential jailbreak attempt detected",
                    description=f"Found pattern associated with jailbreak attempts: '{jailbreak_text}'",
                    suggestion="Rephrase your request within normal usage parameters.",
                    examples=[
                        "Ask directly: 'Explain the concept of X'",
                        "Don't use roleplay to bypass restrictions"
                    ]
                ))
        
        return jailbreaks
    
    def _detect_sensitive_data(self, prompt: str) -> List[Dict[str, str]]:
        """Detect potentially sensitive data in the prompt"""
        sensitive_items = []
        
        for data_type, pattern in self.SENSITIVE_PATTERNS.items():
            matches = re.finditer(pattern, prompt, re.IGNORECASE)
            for match in matches:
                # Redact the actual sensitive value
                sensitive_value = match.group()
                redacted = sensitive_value[:5] + '*' * (len(sensitive_value) - 5)
                
                sensitive_items.append({
                    'type': data_type,
                    'value': redacted
                })
                
                severity = IssueSeverity.HIGH
                if data_type in ['api_key', 'password', 'token']:
                    severity = IssueSeverity.CRITICAL
                
                self.issues.append(PromptIssue(
                    category=IssueCategory.SECURITY,
                    severity=severity,
                    title=f"Sensitive data detected: {data_type}",
                    description=f"Found what appears to be a {data_type}: {redacted}",
                    suggestion="Remove sensitive data from prompts. Use placeholders or environment variables.",
                    examples=[
                        f"Use placeholder: {data_type.upper()}_PLACEHOLDER",
                        f"Reference: 'Use the API key from environment variable'"
                    ]
                ))
        
        return sensitive_items
    
    def _detect_malicious_intent(self, prompt: str) -> List[str]:
        """Detect indicators of potentially malicious intent"""
        malicious = []
        prompt_lower = prompt.lower()
        
        for pattern in self.MALICIOUS_INDICATORS:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                match = re.search(pattern, prompt_lower, re.IGNORECASE)
                if match:
                    malicious_text = match.group()
                    malicious.append(malicious_text)
                    
                    self.issues.append(PromptIssue(
                        category=IssueCategory.SECURITY,
                        severity=IssueSeverity.HIGH,
                        title="Potentially malicious intent detected",
                        description=f"Found concerning pattern: '{malicious_text}'",
                        suggestion="Ensure your prompt has legitimate, ethical purposes.",
                        examples=[
                            "If educational: Clearly state 'For educational purposes to understand X'",
                            "If security research: Frame as 'defensive security' or 'vulnerability assessment'"
                        ]
                    ))
        
        return malicious
    
    def _check_input_sanitization(self, prompt: str) -> List[str]:
        """Check for potential input sanitization issues"""
        issues = []
        
        # Check for unescaped special characters that might cause issues
        dangerous_chars = {
            '<script>': 'XSS-like pattern',
            '${': 'Template injection pattern',
            '{{': 'Template injection pattern',
            '../../': 'Path traversal pattern',
            '; DROP ': 'SQL injection pattern',
            '<!--': 'HTML comment injection',
        }
        
        for char, issue_type in dangerous_chars.items():
            if char in prompt:
                issues.append(issue_type)
                
                self.issues.append(PromptIssue(
                    category=IssueCategory.SECURITY,
                    severity=IssueSeverity.MEDIUM,
                    title=f"Input sanitization concern: {issue_type}",
                    description=f"Found '{char}' which resembles {issue_type}",
                    suggestion="If this is legitimate content, ensure proper escaping. If user input, sanitize it.",
                    examples=[
                        "Escape special characters: &lt;script&gt; instead of <script>",
                        "Use allowlists for user input validation"
                    ]
                ))
        
        # Check for excessive special characters (might indicate obfuscation)
        special_char_count = len(re.findall(r'[^a-zA-Z0-9\s.,;:\-]', prompt))
        total_chars = len(prompt)
        
        if total_chars > 0 and (special_char_count / total_chars) > 0.15:
            issues.append("Excessive special characters")
            
            self.issues.append(PromptIssue(
                category=IssueCategory.SECURITY,
                severity=IssueSeverity.LOW,
                title="High density of special characters",
                description=f"Special characters make up {(special_char_count/total_chars)*100:.1f}% of the prompt.",
                suggestion="Ensure special characters are necessary. High density may indicate obfuscation.",
            ))
        
        return issues
    
    def _calculate_security_score(
        self,
        injections: List[str],
        jailbreaks: List[str],
        sensitive_count: int,
        malicious: List[str],
        sanitization_issues: List[str]
    ) -> float:
        """Calculate overall security score (0-100, higher is better)"""
        
        # Start at 100 (perfect security)
        score = 100.0
        
        # Major penalties
        score -= len(injections) * 25  # Injections are critical
        score -= len(jailbreaks) * 25  # Jailbreaks are critical
        score -= sensitive_count * 15  # Sensitive data is serious
        score -= len(malicious) * 20   # Malicious intent is serious
        
        # Minor penalties
        score -= len(sanitization_issues) * 5
        
        return max(score, 0.0)
