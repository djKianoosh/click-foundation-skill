"""Foundation Sprint tools for the Click agent."""

import json
import sqlite3
from click_agent.models import Alternatives, Diff2x2Axes, Principles


def save_basics(
    conn: sqlite3.Connection,
    sprint_id: int,
    *,
    customer: str,
    problem: str,
    capability: str,
    insight: str,
    motivation: str,
    gorilla: str,
    alternatives: list[str],
) -> str:
    """Save the Basics card: customer, problem, advantages, competitors."""
    alts = Alternatives(items=alternatives)
    conn.execute(
        """UPDATE foundation_sprints SET
            customer = ?, problem = ?,
            capability = ?, insight = ?, motivation = ?,
            gorilla = ?, alternatives = ?,
            current_step = 'differentiation'
        WHERE id = ?""",
        (
            customer, problem,
            capability, insight, motivation,
            gorilla, alts.model_dump_json(),
            sprint_id,
        ),
    )
    conn.commit()
    return "Basics saved. Customer, problem, advantages, and competitors recorded."


def save_differentiation(
    conn: sqlite3.Connection,
    sprint_id: int,
    *,
    differentiator_1: str,
    differentiator_2: str,
    diff_2x2_axes: dict,
    principles: list[str],
) -> str:
    """Save differentiation: 2x2 chart, differentiators, and 3 principles."""
    try:
        axes = Diff2x2Axes(**diff_2x2_axes)
        prins = Principles(items=principles)
    except Exception as e:
        return f"Error: {e}"

    conn.execute(
        """UPDATE foundation_sprints SET
            differentiator_1 = ?, differentiator_2 = ?,
            diff_2x2_axes = ?, principles = ?,
            current_step = 'manifesto'
        WHERE id = ?""",
        (
            differentiator_1, differentiator_2,
            axes.model_dump_json(), prins.model_dump_json(),
            sprint_id,
        ),
    )
    conn.commit()
    return "Differentiation saved. 2x2 chart, differentiators, and principles recorded."


def save_approach(
    conn: sqlite3.Connection,
    sprint_id: int,
    *,
    title: str,
    summary: str,
    how_it_works: str,
    is_top_bet: bool = False,
    is_backup: bool = False,
) -> str:
    """Save an approach option with its one-page summary."""
    conn.execute(
        """INSERT INTO approaches
            (foundation_id, title, summary, how_it_works, is_top_bet, is_backup)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (sprint_id, title, summary, how_it_works, is_top_bet, is_backup),
    )
    conn.commit()
    return f"Approach '{title}' saved."


def save_founding_hypothesis(
    conn: sqlite3.Connection,
    sprint_id: int,
    project_id: int,
    *,
    customer: str,
    problem: str,
    approach: str,
    competitors: str,
    differentiation: str,
) -> str:
    """Save the Founding Hypothesis and set it as current on the project."""
    cursor = conn.execute(
        """INSERT INTO hypotheses
            (foundation_id, customer, problem, approach, competitors, differentiation)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (sprint_id, customer, problem, approach, competitors, differentiation),
    )
    hypothesis_id = cursor.lastrowid
    conn.execute(
        "UPDATE projects SET current_hypothesis_id = ? WHERE id = ?",
        (hypothesis_id, project_id),
    )
    conn.execute(
        "UPDATE foundation_sprints SET current_step = 'scorecard' WHERE id = ?",
        (sprint_id,),
    )
    conn.commit()
    return (
        f"Founding Hypothesis saved (version 1). "
        f"'If we help {customer} solve {problem} with {approach}, "
        f"they will choose it over {competitors} because our solution is {differentiation}.'"
    )
