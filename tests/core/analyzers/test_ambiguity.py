"""
Test suite for the Ambiguity Detector.
"""
import pytest
from src.core.analyzers.ambiguity import AmbiguityDetector
from src.core.models.schemas import IssueCategory, IssueSeverity


class TestAmbiguityDetector:
    """Test cases for ambiguity detection"""
    
    def setup_method(self):
        """Setup for each test"""
        self.detector = AmbiguityDetector()
    
    def test_vague_terms_detection(self):
        """Test detection of vague language"""
        prompt = "Write some articles about various things in technology."
        issues, metrics = self.detector.analyze(prompt)
        
        # Should detect 'some', 'various', 'things'
        assert len(metrics.vague_terms) >= 2
        assert 'some' in metrics.vague_terms or 'various' in metrics.vague_terms
        
        # Should have corresponding issues
        vague_issues = [i for i in issues if i.category == IssueCategory.AMBIGUITY]
        assert len(vague_issues) > 0
    
    def test_contradiction_detection(self):
        """Test detection of contradictory instructions"""
        prompt = "Write a brief explanation. Then provide a detailed comprehensive analysis."
        issues, metrics = self.detector.analyze(prompt)
        
        # Should detect brief vs detailed/comprehensive conflict
        assert len(metrics.conflicting_instructions) > 0
        
        # Should have high severity issue
        contradiction_issues = [i for i in issues if i.category == IssueCategory.CONTRADICTION]
        assert any(i.severity == IssueSeverity.HIGH for i in contradiction_issues)
    
    def test_no_contradictions_same_sentence(self):
        """Test that contradictions in same sentence are not flagged"""
        prompt = "Make it concise yet detailed in key areas."
        issues, metrics = self.detector.analyze(prompt)
        
        # Should not flag this as contradiction (in same instruction)
        # This is context-dependent contradiction which is okay
        assert len(metrics.conflicting_instructions) == 0
    
    def test_undefined_acronyms(self):
        """Test detection of undefined acronyms"""
        prompt = "Analyze the ROI of our SAAS platform using KPI metrics."
        issues, metrics = self.detector.analyze(prompt)
        
        # Should detect custom acronyms (not common ones)
        assert len(metrics.undefined_terms) > 0
    
    def test_indefinite_quantifiers(self):
        """Test detection of indefinite quantifiers"""
        prompt = "Provide several examples with multiple use cases and many details."
        issues, metrics = self.detector.analyze(prompt)
        
        # Should flag indefinite quantifiers
        instruction_issues = [i for i in issues if i.category == IssueCategory.INSTRUCTION]
        assert len(instruction_issues) > 0
    
    def test_ambiguity_score_calculation(self):
        """Test that ambiguity score is calculated correctly"""
        # Clear, specific prompt
        clear_prompt = "Generate exactly 3 JSON objects with fields: name, age, email."
        _, clear_metrics = self.detector.analyze(clear_prompt)
        
        # Vague, ambiguous prompt
        vague_prompt = "Create some things about various stuff that might be relevant."
        _, vague_metrics = self.detector.analyze(vague_prompt)
        
        # Vague prompt should have higher ambiguity score
        assert vague_metrics.ambiguity_score > clear_metrics.ambiguity_score
        
        # Clear prompt should have higher clarity score
        assert clear_metrics.clarity_score > vague_metrics.clarity_score
    
    def test_empty_prompt(self):
        """Test handling of empty prompt"""
        prompt = ""
        issues, metrics = self.detector.analyze(prompt)
        
        # Should not crash, should return minimal metrics
        assert metrics.ambiguity_score >= 0
        assert metrics.clarity_score >= 0
    
    def test_suggestion_provided(self):
        """Test that issues include helpful suggestions"""
        prompt = "Write some examples about various things."
        issues, _ = self.detector.analyze(prompt)
        
        # All issues should have suggestions
        assert all(issue.suggestion is not None for issue in issues)
        assert all(len(issue.suggestion) > 0 for issue in issues)
    
    def test_examples_provided_for_vague_terms(self):
        """Test that vague term issues include examples"""
        prompt = "Give me some good results."
        issues, _ = self.detector.analyze(prompt)
        
        vague_issues = [i for i in issues if i.category == IssueCategory.AMBIGUITY]
        
        # Should have examples for how to improve
        assert any(i.examples is not None and len(i.examples) > 0 for i in vague_issues)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
