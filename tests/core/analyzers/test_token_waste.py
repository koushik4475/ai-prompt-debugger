"""
Test suite for the Token Waste Analyzer.
"""
import pytest
from src.core.analyzers.token_waste import TokenWasteAnalyzer
from src.core.models.schemas import IssueCategory


class TestTokenWasteAnalyzer:
    """Test cases for token waste analysis"""
    
    def setup_method(self):
        """Setup for each test"""
        self.analyzer = TokenWasteAnalyzer()
    
    def test_redundant_phrase_detection(self):
        """Test detection of redundant phrases"""
        prompt = "Please note that it is important to note that you should create a document."
        issues, metrics = self.analyzer.analyze(prompt)
        
        # Should detect redundant phrases
        assert len(metrics.redundant_phrases) > 0
        
        # Should have token waste issues
        waste_issues = [i for i in issues if i.category == IssueCategory.TOKEN_WASTE]
        assert len(waste_issues) > 0
    
    def test_filler_word_detection(self):
        """Test detection of filler words"""
        prompt = "Actually, this is basically just really very simple stuff."
        issues, metrics = self.analyzer.analyze(prompt)
        
        # Should flag filler words issue
        waste_issues = [i for i in issues if i.category == IssueCategory.TOKEN_WASTE]
        assert any('filler' in i.title.lower() for i in waste_issues)
    
    def test_token_efficiency_calculation(self):
        """Test that efficiency is calculated correctly"""
        # Efficient prompt
        efficient = "Generate 3 JSON objects with fields: name, age, city."
        _, efficient_metrics = self.analyzer.analyze(efficient)
        
        # Wasteful prompt
        wasteful = (
            "Please note that it is important to note that you should basically "
            "generate, in order to complete this task, several JSON objects."
        )
        _, wasteful_metrics = self.analyzer.analyze(wasteful)
        
        # Efficient prompt should have higher efficiency score
        assert efficient_metrics.token_efficiency > wasteful_metrics.token_efficiency
    
    def test_verbose_section_detection(self):
        """Test detection of overly verbose sections"""
        prompt = (
            "In order to complete this task successfully, it is absolutely essential "
            "that you take into consideration all of the various different factors "
            "that might potentially have an impact on the overall outcome of the "
            "final result that we are trying to achieve here."
        )
        issues, metrics = self.analyzer.analyze(prompt)
        
        # Should detect verbose section
        verbose_issues = [i for i in issues if 'verbose' in i.title.lower()]
        assert len(verbose_issues) > 0
    
    def test_compression_opportunities(self):
        """Test that compression opportunities are identified"""
        prompt = "Please note that in order to achieve this, you need to understand that..."
        _, metrics = self.analyzer.analyze(prompt)
        
        # Should identify compression opportunities
        assert len(metrics.compression_opportunities) > 0
        assert all('tokens_saved' in op for op in metrics.compression_opportunities)
    
    def test_cost_calculation(self):
        """Test that cost is calculated correctly"""
        prompt = "Test prompt " * 100  # ~200 tokens
        _, metrics = self.analyzer.analyze(prompt, cost_per_1k_tokens=0.003)
        
        # Should calculate non-zero cost
        assert metrics.estimated_cost > 0
        assert metrics.total_tokens > 0
    
    def test_unnecessary_tokens_tracking(self):
        """Test that unnecessary tokens are tracked"""
        prompt = "Please note that basically you should really just simply create this."
        _, metrics = self.analyzer.analyze(prompt)
        
        # Should identify some unnecessary tokens
        assert metrics.unnecessary_tokens > 0
    
    def test_clean_prompt_high_efficiency(self):
        """Test that clean prompts get high efficiency scores"""
        prompt = "Create a Python function that calculates fibonacci numbers."
        _, metrics = self.analyzer.analyze(prompt)
        
        # Clean prompt should have high efficiency
        assert metrics.token_efficiency > 90
        assert metrics.unnecessary_tokens < 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
