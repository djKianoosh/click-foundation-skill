import pytest
from models import (
    Alternatives,
    CustomerReaction,
    CustomerReactions,
    Diff2x2Axes,
    FoundationStep,
    LensEvaluation,
    LensEvaluations,
    Principles,
    ScorecardAnswer,
    ValidationError,
)


class TestAlternatives:
    def test_valid_alternatives(self):
        alts = Alternatives(items=["Google Maps", "Apple Maps", "do nothing"])
        assert len(alts.items) == 3

    def test_empty_alternatives(self):
        alts = Alternatives(items=[])
        assert alts.items == []

    def test_serializes_to_json(self):
        alts = Alternatives(items=["A", "B"])
        data = alts.model_dump_json()
        assert '"A"' in data


class TestDiff2x2Axes:
    def test_valid_axes(self):
        axes = Diff2x2Axes(x_low="Slow", x_high="Fast", y_low="Expensive", y_high="Cheap")
        assert axes.x_low == "Slow"

    def test_missing_field_raises(self):
        with pytest.raises(ValidationError):
            Diff2x2Axes(x_low="Slow", x_high="Fast", y_low="Expensive")


class TestPrinciples:
    def test_valid_three_principles(self):
        p = Principles(items=["Focus on user", "Fast is better", "Don't be evil"])
        assert len(p.items) == 3

    def test_wrong_count_raises(self):
        with pytest.raises(ValidationError):
            Principles(items=["Only one"])


class TestLensEvaluations:
    def test_valid_evaluations(self):
        evals = LensEvaluations(
            items=[
                LensEvaluation(approach_id=1, x_position="high", y_position="high"),
                LensEvaluation(approach_id=2, x_position="low", y_position="high"),
            ]
        )
        assert len(evals.items) == 2

    def test_invalid_position_raises(self):
        with pytest.raises(ValidationError):
            LensEvaluation(approach_id=1, x_position="middle", y_position="high")


class TestCustomerReactions:
    def test_valid_reactions(self):
        reactions = CustomerReactions(
            items=[
                CustomerReaction(
                    customer="Engineer A",
                    reaction="Leaned forward, asked to sign up",
                    is_reaction=True,
                ),
                CustomerReaction(
                    customer="Engineer B",
                    reaction="Said it looks nice but didn't engage",
                    is_reaction=False,
                ),
            ]
        )
        assert reactions.items[0].is_reaction is True


class TestScorecardAnswer:
    def test_valid_answers(self):
        for answer in ["yes", "maybe", "not_yet", "no"]:
            assert ScorecardAnswer(answer) == answer

    def test_invalid_answer_raises(self):
        with pytest.raises(ValueError):
            ScorecardAnswer("probably")


class TestFoundationStep:
    def test_valid_steps(self):
        steps = [
            "customer",
            "problem",
            "advantages",
            "competitors",
            "differentiation",
            "principles",
            "manifesto",
            "approaches",
            "lenses",
            "hypothesis",
            "scorecard",
            "complete",
        ]
        for step in steps:
            assert FoundationStep(step) == step

    def test_invalid_step_raises(self):
        with pytest.raises(ValueError):
            FoundationStep("invalid")
