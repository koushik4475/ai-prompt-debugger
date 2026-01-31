"""
Test suite for the Success Predictor.
"""
import pytest
from src.core.analyzers.success_prediction import SuccessPredictor
from src.core.models.schemas import IssueCategory


class TestSuccessPredictor:
    """Test cases for success prediction"""
    
    def setup_method(self):
        """Setup for each test"""
        self.predictor = SuccessPredictor()
    
    def test_high_quality_prompt_prediction(self):
        """Test that high-quality prompts get good predictions"""
        prompt = """
        Create a Python function that calculates the fibonacci sequence.
        
        Requirements:
        - Function should accept an integer n
        - Return list of first n fibonacci numbers
        - Handle edge cases (n <= 0)
        
        Example output for n=5: [0, 1, 1, 2, 3]
        
        Format: Return as JSON with 'result' key containing the list.
        """
        issues, prediction = self.predictor.analyze(prompt)
        
        # Should have high success probability
        assert prediction.success_probability > 70
        
        # Should identify multiple strengths
        assert len(prediction.strengths) >= 3
        
        # Should have few risk factors
        assert len(prediction.risk_factors) < 3
    
    def test_poor_quality_prompt_prediction(self):
        """Test that poor-quality prompts get low predictions"""
        prompt = "Do something with code maybe."
        issues, prediction = self.predictor.analyze(prompt)
        
        # Should have low success probability
        assert prediction.success_probability < 50
        
        # Should identify risk factors
        assert len(prediction.risk_factors) > 0
    
    def test_strength_identification(self):
        """Test that strengths are correctly identified"""
        prompt = """
        You are an expert Python developer.
        
        Task: Create a REST API endpoint.
        
        Context: This is for a e-commerce platform handling user authentication.
        
        Format: Respond with code in markdown format.
        
        Example:
        ```python
        @app.route('/login', methods=['POST'])
        def login():
            pass
        ```
        """
        _, prediction = self.predictor.analyze(prompt)
        
        # Should identify these strengths
        assert any('role' in s.lower() for s in prediction.strengths)
        assert any('context' in s.lower() for s in prediction.strengths)
        assert any('example' in s.lower() for s in prediction.strengths)
        assert any('format' in s.lower() for s in prediction.strengths)
    
    def test_risk_factor_identification(self):
        """Test that risk factors are correctly identified"""
        prompt = "Write anything about whatever topics you think are relevant."
        issues, prediction = self.predictor.analyze(prompt)
        
        # Should identify open-ended risk
        assert any('open-ended' in r.lower() for r in prediction.risk_factors)
    
    def test_missing_examples_flagged(self):
        """Test that complex prompts without examples are flagged"""
        prompt = (
            "Create a comprehensive data analysis pipeline that processes user "
            "behavior data, applies machine learning models, generates insights, "
            "and produces visualizations with interactive dashboards."
        )
        issues, prediction = self.predictor.analyze(prompt)
        
        # Should flag missing examples
        assert any('example' in r.lower() for r in prediction.risk_factors)
    
    def test_recommendations_provided(self):
        """Test that actionable recommendations are provided"""
        prompt = "Make some code."
        _, prediction = self.predictor.analyze(prompt)
        
        # Should have recommendations
        assert len(prediction.recommended_improvements) > 0
        
        # Recommendations should be actionable
        assert all(len(rec) > 10 for rec in prediction.recommended_improvements)
    
    def test_confidence_score(self):
        """Test that confidence scores are reasonable"""
        # Detailed prompt - high confidence
        detailed = "Create exactly 5 JSON objects with these fields: name (string), age (integer)."
        _, detailed_pred = self.predictor.analyze(detailed)
        
        # Very short prompt - lower confidence
        short = "Code it."
        _, short_pred = self.predictor.analyze(short)
        
        # Detailed prompt should have higher confidence
        assert detailed_pred.confidence_score > short_pred.confidence_score
    
    def test_structural_quality_scoring(self):
        """Test that structure affects success prediction"""
        # Well-structured
        structured = """
        1. First, analyze the data
        2. Then, apply transformations
        3. Finally, generate report
        
        Constraints:
        - Must use pandas
        - Output as CSV
        """
        _, structured_pred = self.predictor.analyze(structured)
        
        # Unstructured
        unstructured = "Analyze data, transform it, make report, use pandas, CSV output."
        _, unstructured_pred = self.predictor.analyze(unstructured)
        
        # Structured should score higher
        assert structured_pred.success_probability > unstructured_pred.success_probability


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
