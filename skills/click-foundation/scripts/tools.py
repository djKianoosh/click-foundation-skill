#!/usr/bin/env python3
"""Core tools for Click Foundation Sprints, Design Sprints, Scorecard, and Context."""

import sqlite3
import sys
from pathlib import Path

_script_dir = Path(__file__).parent.resolve()
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))

from models import (
    Alternatives,
    CustomerReaction,
    CustomerReactions,
    Diff2x2Axes,
    LensEvaluation,
    LensEvaluations,
    Principles,
    ScorecardAnswer,
    SourceType,
    ValidationError,
)

THE_10_LESSONS = [
    "Drop everything and sprint on the most important challenge until it's done",
    "Start by identifying your customer and a real problem you can solve",
    "Take advantage of your advantages",
    "Get real about the competition",
    "Differentiation makes products click",
    "Use practical principles to reinforce differentiation",
    "Seek alternatives to your first idea",
    "Consider conflicting opinions before you commit to an approach",
    "It's just a hypothesis until you prove it",
    "Experiment with tiny loops until your solution clicks. Then build it.",
]

VALID_DAYS = ("map", "sketch", "decide", "prototype", "test")


# ==============================================================================
# Foundation Sprint Tools
# ==============================================================================


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
            customer,
            problem,
            capability,
            insight,
            motivation,
            gorilla,
            alts.model_dump_json(),
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
    except (ValueError, TypeError, ValidationError) as e:
        return f"Error: {e}"

    conn.execute(
        """UPDATE foundation_sprints SET
            differentiator_1 = ?, differentiator_2 = ?,
            diff_2x2_axes = ?, principles = ?,
            current_step = 'manifesto'
        WHERE id = ?""",
        (
            differentiator_1,
            differentiator_2,
            axes.model_dump_json(),
            prins.model_dump_json(),
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


def save_magic_lens(
    conn: sqlite3.Connection,
    sprint_id: int,
    *,
    lens_name: str,
    x_axis_low: str,
    x_axis_high: str,
    y_axis_low: str,
    y_axis_high: str,
    evaluations: list[dict],
) -> str:
    """Save a Magic Lens evaluation (2x2 chart from a specific perspective)."""
    try:
        evals = LensEvaluations(items=[LensEvaluation(**e) for e in evaluations])
    except (ValueError, TypeError, ValidationError) as e:
        return f"Error: {e}"

    conn.execute(
        """INSERT INTO magic_lenses
            (foundation_id, lens_name, x_axis_low, x_axis_high, y_axis_low, y_axis_high, evaluations)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            sprint_id,
            lens_name,
            x_axis_low,
            x_axis_high,
            y_axis_low,
            y_axis_high,
            evals.model_dump_json(),
        ),
    )
    conn.commit()
    return f"Magic Lens '{lens_name}' saved with {len(evaluations)} approach evaluations."


# ==============================================================================
# Design Sprint Tools
# ==============================================================================


def create_design_sprint(
    conn: sqlite3.Connection,
    hypothesis_id: int,
    *,
    risk_question: str,
) -> str:
    """Create a new Design Sprint linked to the current hypothesis."""
    conn.execute(
        """INSERT INTO design_sprints (hypothesis_id, risk_question, status)
        VALUES (?, ?, 'in_progress')""",
        (hypothesis_id, risk_question),
    )
    conn.commit()
    return f"Design Sprint created. Testing: '{risk_question}'"


def log_sprint_day(
    conn: sqlite3.Connection,
    sprint_id: int,
    *,
    day: str,
    notes: str,
) -> str:
    """Record what happened on a specific day of the Design Sprint."""
    if day not in VALID_DAYS:
        return f"Error: '{day}' is not a valid day. Use: {', '.join(VALID_DAYS)}"

    column = f"day_{day}"
    conn.execute(
        f"UPDATE design_sprints SET {column} = ? WHERE id = ?",
        (notes, sprint_id),
    )
    conn.commit()
    return f"Day '{day}' logged."


def record_test_results(
    conn: sqlite3.Connection,
    sprint_id: int,
    *,
    reactions: list[dict],
) -> str:
    """Record customer reactions from Friday testing."""
    try:
        validated = CustomerReactions(items=[CustomerReaction(**r) for r in reactions])
    except (ValueError, TypeError, ValidationError) as e:
        return f"Error: {e}"

    conn.execute(
        "UPDATE design_sprints SET customer_reactions = ? WHERE id = ?",
        (validated.model_dump_json(), sprint_id),
    )
    conn.commit()
    genuine = sum(1 for r in validated.items if r.is_reaction)
    return (
        f"Recorded {len(reactions)} observations "
        f"({genuine} genuine reactions, {len(reactions) - genuine} feedback)."
    )


def update_sprint_outcome(
    conn: sqlite3.Connection,
    sprint_id: int,
    *,
    outcome: str,
    hypothesis_changed: bool,
) -> str:
    """Record the Design Sprint outcome and mark it complete."""
    conn.execute(
        """UPDATE design_sprints SET
            outcome = ?, hypothesis_changed = ?, status = 'complete'
        WHERE id = ?""",
        (outcome, hypothesis_changed, sprint_id),
    )
    conn.commit()
    status = "Hypothesis needs revision." if hypothesis_changed else "Hypothesis unchanged."
    return f"Sprint complete. {status} Outcome: {outcome}"


# ==============================================================================
# Scorecard Tools
# ==============================================================================


def update_scorecard(
    conn: sqlite3.Connection,
    hypothesis_id: int,
    *,
    right_customer: str,
    right_problem: str,
    right_approach: str,
    will_they_switch: str,
    right_differentiation: str,
    does_it_click: str,
    notes: str,
) -> str:
    """Update the scorecard with new answers and evidence."""
    answers = {
        "right_customer": right_customer,
        "right_problem": right_problem,
        "right_approach": right_approach,
        "will_they_switch": will_they_switch,
        "right_differentiation": right_differentiation,
        "does_it_click": does_it_click,
    }
    for field, value in answers.items():
        try:
            ScorecardAnswer(value)
        except ValueError:
            return (
                f"Error: '{value}' is not a valid answer for {field}. Use: yes, maybe, not_yet, no"
            )

    conn.execute(
        """INSERT INTO scorecard_entries
            (hypothesis_id, right_customer, right_problem, right_approach,
             will_they_switch, right_differentiation, does_it_click, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            hypothesis_id,
            right_customer,
            right_problem,
            right_approach,
            will_they_switch,
            right_differentiation,
            does_it_click,
            notes,
        ),
    )
    conn.commit()
    return "Scorecard saved with evidence notes."


def show_scorecard(
    conn: sqlite3.Connection,
    hypothesis_id: int,
) -> str:
    """Show the current scorecard state with evidence trail."""
    cursor = conn.execute(
        """SELECT * FROM scorecard_entries
        WHERE hypothesis_id = ?
        ORDER BY updated_at DESC LIMIT 1""",
        (hypothesis_id,),
    )
    entry = cursor.fetchone()
    if not entry:
        return "No scorecard entries yet. Run a Design Sprint to start validating."

    lines = [
        "## Scorecard",
        f"- Right customer? **{entry['right_customer']}**",
        f"- Right problem? **{entry['right_problem']}**",
        f"- Right approach? **{entry['right_approach']}**",
        f"- Will they switch? **{entry['will_they_switch']}**",
        f"- Right differentiation? **{entry['right_differentiation']}**",
        f"- Does it click? **{entry['does_it_click']}**",
        f"\nNotes: {entry['notes']}",
    ]
    return "\n".join(lines)


# ==============================================================================
# Context, Learnings & Revision Tools
# ==============================================================================


def get_project_context(conn: sqlite3.Connection, project_id: int) -> str:
    """Load current project context: hypothesis, scorecard, sprint history."""
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not project:
        return "Error: Project not found."

    lines = [f"## Project: {project['name']}"]

    hyp_id = project["current_hypothesis_id"]
    if not hyp_id:
        lines.append("\nNo Founding Hypothesis yet. Run a Foundation Sprint first.")
    else:
        hyp = conn.execute("SELECT * FROM hypotheses WHERE id = ?", (hyp_id,)).fetchone()
        lines.append(f"\n### Founding Hypothesis (v{hyp['version']})")
        lines.append(
            f"If we help **{hyp['customer']}** solve **{hyp['problem']}** "
            f"with **{hyp['approach']}**, they will choose it over **{hyp['competitors']}** "
            f"because our solution is **{hyp['differentiation']}**."
        )

        entry = conn.execute(
            "SELECT * FROM scorecard_entries WHERE hypothesis_id = ? ORDER BY updated_at DESC LIMIT 1",
            (hyp_id,),
        ).fetchone()
        if entry:
            lines.append("\n### Scorecard")
            for field in [
                "right_customer",
                "right_problem",
                "right_approach",
                "will_they_switch",
                "right_differentiation",
                "does_it_click",
            ]:
                label = field.replace("_", " ").title()
                lines.append(f"- {label}: **{entry[field]}**")

        count_row = conn.execute(
            "SELECT COUNT(*) FROM design_sprints WHERE hypothesis_id = ?", (hyp_id,)
        ).fetchone()
        count = count_row[0] if count_row else 0
        if count:
            lines.append(f"\n{count} Design Sprint(s) completed for this hypothesis.")

    return "\n".join(lines)


def record_learning(
    conn: sqlite3.Connection,
    *,
    source_type: str,
    source_id: int | None,
    insight: str,
    lesson_number: int,
) -> str:
    """Record a learning tagged with one of the 10 Click lessons."""
    try:
        SourceType(source_type)
    except ValueError:
        return f"Error: '{source_type}' is not valid. Use: foundation_sprint, design_sprint, pivot"

    if not 1 <= lesson_number <= 10:
        return f"Error: lesson_number must be between 1 and 10, got {lesson_number}"

    conn.execute(
        "INSERT INTO learnings (source_type, source_id, insight, lesson_number) VALUES (?, ?, ?, ?)",
        (source_type, source_id, insight, lesson_number),
    )
    conn.commit()
    return f"Learning recorded (Lesson #{lesson_number}: {THE_10_LESSONS[lesson_number - 1]})"


def query_learnings(conn: sqlite3.Connection) -> str:
    """Retrieve all accumulated learnings organized by lesson number."""
    learnings = conn.execute(
        "SELECT * FROM learnings ORDER BY lesson_number, created_at"
    ).fetchall()

    if not learnings:
        return "No learnings recorded yet."

    lines = ["## Accumulated Learnings"]
    current_lesson = None
    for l in learnings:
        if l["lesson_number"] != current_lesson:
            current_lesson = l["lesson_number"]
            lines.append(f"\n### Lesson {current_lesson}: {THE_10_LESSONS[current_lesson - 1]}")
        lines.append(f"- {l['insight']} (from {l['source_type']})")

    return "\n".join(lines)


def revise_hypothesis(
    conn: sqlite3.Connection,
    project_id: int,
    old_hypothesis_id: int,
    *,
    customer: str,
    problem: str,
    approach: str,
    competitors: str,
    differentiation: str,
    reason: str,
    what_changed: str,
) -> str:
    """Create a new hypothesis version and record the pivot."""
    old = conn.execute("SELECT * FROM hypotheses WHERE id = ?", (old_hypothesis_id,)).fetchone()
    if not old:
        return f"Error: Hypothesis #{old_hypothesis_id} not found."
    new_version = old["version"] + 1

    cursor = conn.execute(
        """INSERT INTO hypotheses
            (foundation_id, customer, problem, approach, competitors, differentiation, version)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            old["foundation_id"],
            customer,
            problem,
            approach,
            competitors,
            differentiation,
            new_version,
        ),
    )
    new_id = cursor.lastrowid

    conn.execute(
        "INSERT INTO pivots (old_hypothesis_id, new_hypothesis_id, reason, what_changed) VALUES (?, ?, ?, ?)",
        (old_hypothesis_id, new_id, reason, what_changed),
    )
    conn.execute(
        "UPDATE projects SET current_hypothesis_id = ? WHERE id = ?",
        (new_id, project_id),
    )
    conn.commit()
    return f"Hypothesis revised to v{new_version}. Changed: {what_changed}. Reason: {reason}"
