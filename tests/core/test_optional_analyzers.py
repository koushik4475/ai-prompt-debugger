import pytest

from src.core.debugger import PromptDebugger
from src.core.models.schemas import AnalyzerConfig


@pytest.mark.parametrize(
    ("config", "missing_field"),
    [
        (AnalyzerConfig(enable_ambiguity_detection=False), "ambiguity"),
        (AnalyzerConfig(enable_token_analysis=False), "metrics"),
        (AnalyzerConfig(enable_success_prediction=False), "predictions"),
        (AnalyzerConfig(enable_security_scanning=False), "security"),
    ],
)
def test_analyze_supports_individually_disabled_analyzers(config, missing_field):
    result = PromptDebugger(config).analyze("Write a concise Python function.")

    assert getattr(result, missing_field) is None
    assert result.prompt_text == "Write a concise Python function."
    assert 0 <= result.overall_quality_score <= 100


def test_analyze_supports_all_analyzers_disabled():
    config = AnalyzerConfig(
        enable_ambiguity_detection=False,
        enable_token_analysis=False,
        enable_success_prediction=False,
        enable_security_scanning=False,
    )

    result = PromptDebugger(config).analyze("Write a concise Python function.")

    assert result.metrics is None
    assert result.ambiguity is None
    assert result.predictions is None
    assert result.security is None
    assert result.overall_quality_score == 0
    assert result.overall_grade == "F"
