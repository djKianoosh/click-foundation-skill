#!/usr/bin/env python3
"""Data models and validation for Click Foundation & Design Sprints.

Supports Pydantic v2 when available, with a standard-library dataclass fallback
so scripts run seamlessly in zero-dependency environments.
"""

import json
from enum import StrEnum
from typing import Literal

try:
    from pydantic import BaseModel, ValidationError, field_validator

    class Alternatives(BaseModel):
        items: list[str]

    class Diff2x2Axes(BaseModel):
        x_low: str
        x_high: str
        y_low: str
        y_high: str

    class Principles(BaseModel):
        items: list[str]

        @field_validator("items")
        @classmethod
        def must_have_three(cls, v: list[str]) -> list[str]:
            if len(v) != 3:
                raise ValueError(
                    "Must have exactly 3 principles (differentiate, differentiate, safeguard)"
                )
            return v

    class LensEvaluation(BaseModel):
        approach_id: int
        x_position: Literal["high", "low"]
        y_position: Literal["high", "low"]

    class LensEvaluations(BaseModel):
        items: list[LensEvaluation]

    class CustomerReaction(BaseModel):
        customer: str
        reaction: str
        is_reaction: bool

    class CustomerReactions(BaseModel):
        items: list[CustomerReaction]

except ImportError:
    from dataclasses import asdict, dataclass

    class ValidationError(ValueError):
        """Fallback validation error matching pydantic interface."""

    @dataclass
    class Alternatives:
        items: list[str]

        def model_dump_json(self) -> str:
            return json.dumps(asdict(self))

    @dataclass
    class Diff2x2Axes:
        x_low: str
        x_high: str
        y_low: str
        y_high: str

        def __post_init__(self):
            for f in ("x_low", "x_high", "y_low", "y_high"):
                if getattr(self, f) is None:
                    raise ValidationError(f"Field {f} cannot be None")

        def model_dump_json(self) -> str:
            return json.dumps(asdict(self))

    @dataclass
    class Principles:
        items: list[str]

        def __post_init__(self):
            if len(self.items) != 3:
                raise ValidationError(
                    "Must have exactly 3 principles (differentiate, differentiate, safeguard)"
                )

        def model_dump_json(self) -> str:
            return json.dumps(asdict(self))

    @dataclass
    class LensEvaluation:
        approach_id: int
        x_position: str
        y_position: str

        def __post_init__(self):
            if self.x_position not in ("high", "low"):
                raise ValidationError(f"Invalid x_position: {self.x_position}")
            if self.y_position not in ("high", "low"):
                raise ValidationError(f"Invalid y_position: {self.y_position}")

    @dataclass
    class LensEvaluations:
        items: list[LensEvaluation]

        def model_dump_json(self) -> str:
            return json.dumps({"items": [asdict(e) for e in self.items]})

    @dataclass
    class CustomerReaction:
        customer: str
        reaction: str
        is_reaction: bool

    @dataclass
    class CustomerReactions:
        items: list[CustomerReaction]

        def model_dump_json(self) -> str:
            return json.dumps({"items": [asdict(r) for r in self.items]})


class ScorecardAnswer(StrEnum):
    YES = "yes"
    MAYBE = "maybe"
    NOT_YET = "not_yet"
    NO = "no"


class FoundationStep(StrEnum):
    CUSTOMER = "customer"
    PROBLEM = "problem"
    ADVANTAGES = "advantages"
    COMPETITORS = "competitors"
    DIFFERENTIATION = "differentiation"
    PRINCIPLES = "principles"
    MANIFESTO = "manifesto"
    APPROACHES = "approaches"
    LENSES = "lenses"
    HYPOTHESIS = "hypothesis"
    SCORECARD = "scorecard"
    COMPLETE = "complete"


class SourceType(StrEnum):
    FOUNDATION_SPRINT = "foundation_sprint"
    DESIGN_SPRINT = "design_sprint"
    PIVOT = "pivot"
