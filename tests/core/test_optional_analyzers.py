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


def test_compare_supports_disabled_non_token_analyzers():
    config = AnalyzerConfig(
        enable_ambiguity_detection=False,
        enable_success_prediction=False,
        enable_security_scanning=False,
    )

    result = PromptDebugger(config).compare("Write code.", "Write clear Python code.")

    assert result.prompt_a.ambiguity is None
    assert result.prompt_a.predictions is None
    assert result.prompt_a.security is None
    assert result.token_difference != 0 or result.prompt_a.metrics.total_tokens == result.prompt_b.metrics.total_tokens


def test_compare_requires_token_analysis():
    debugger = PromptDebugger(AnalyzerConfig(enable_token_analysis=False))

    with pytest.raises(ValueError, match="requires token analysis"):
        debugger.compare("Write code.", "Write clear Python code.")
