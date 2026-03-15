"""Pydantic models for JSON field validation in SQLite."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, field_validator


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
            raise ValueError("Must have exactly 3 principles (differentiate, differentiate, safeguard)")
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
    is_reaction: bool  # True = genuine reaction, False = just feedback


class CustomerReactions(BaseModel):
    items: list[CustomerReaction]
