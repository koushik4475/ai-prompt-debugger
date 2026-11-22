import pytest

from src.core.debugger import PromptDebugger


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (100, "A"),
        (90, "A"),
        (89.99, "B"),
        (80, "B"),
        (79.99, "C"),
        (70, "C"),
        (69.99, "D"),
        (60, "D"),
        (59.99, "F"),
        (0, "F"),
    ],
)
def test_grade_thresholds(score, expected):
    assert PromptDebugger()._assign_grade(score) == expected
