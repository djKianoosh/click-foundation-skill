"""Markdown document generation from SQLite data."""

import json
from pathlib import Path
import sqlite3


def generate_docs(
    conn: sqlite3.Connection,
    output_dir: str,
    *,
    doc_type: str = "all",
) -> str:
    """Generate markdown documents. doc_type: all, foundation, scorecard, learnings, pivot_history."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    generated = []

    if doc_type in ("all", "foundation"):
        _generate_foundation(conn, output)
        generated.extend(["foundation-sprint.md", "founding-hypothesis.md"])

    if doc_type in ("all", "scorecard"):
        _generate_scorecard(conn, output)
        generated.append("scorecard.md")

    if doc_type in ("all", "learnings"):
        _generate_learnings(conn, output)
        generated.append("learnings.md")

    if doc_type in ("all", "pivot_history"):
        _generate_pivot_history(conn, output)
        generated.append("pivot-history.md")

    if doc_type in ("all", "sprint"):
        _generate_latest_sprint(conn, output)
        generated.append("sprints/")

    return f"Generated: {', '.join(generated)}"


def _generate_foundation(conn: sqlite3.Connection, output: Path) -> None:
    sprint = conn.execute(
        "SELECT * FROM foundation_sprints ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    if not sprint:
        return

    lines = [
        "# Foundation Sprint Summary",
        "",
        "## The Basics",
        f"- **Customer:** {sprint['customer']}",
        f"- **Problem:** {sprint['problem']}",
        "",
        "### Advantage",
        f"- **Capability:** {sprint['capability']}",
        f"- **Insight:** {sprint['insight']}",
        f"- **Motivation:** {sprint['motivation']}",
        "",
        "### Competition",
        f"- **800-pound gorilla:** {sprint['gorilla']}",
    ]

    if sprint["alternatives"]:
        alts = json.loads(sprint["alternatives"])
        if isinstance(alts, dict):
            alts = alts.get("items", [])
        lines.append(f"- **Alternatives:** {', '.join(alts)}")

    if sprint["differentiator_1"]:
        lines.extend([
            "",
            "## Differentiation",
            f"- **Differentiator 1:** {sprint['differentiator_1']}",
            f"- **Differentiator 2:** {sprint['differentiator_2']}",
        ])

    if sprint["principles"]:
        prins = json.loads(sprint["principles"])
        if isinstance(prins, dict):
            prins = prins.get("items", [])
        lines.extend(["", "## Principles"])
        for i, p in enumerate(prins, 1):
            lines.append(f"{i}. {p}")

    (output / "foundation-sprint.md").write_text("\n".join(lines))

    hyp = conn.execute(
        "SELECT * FROM hypotheses WHERE foundation_id = ? ORDER BY version DESC LIMIT 1",
        (sprint["id"],),
    ).fetchone()
    if hyp:
        hyp_lines = [
            "# Founding Hypothesis",
            "",
            f"**Version {hyp['version']}**",
            "",
            f"If we help **{hyp['customer']}** solve **{hyp['problem']}** "
            f"with **{hyp['approach']}**, they will choose it over "
            f"**{hyp['competitors']}** because our solution is **{hyp['differentiation']}**.",
        ]
        (output / "founding-hypothesis.md").write_text("\n".join(hyp_lines))


def _generate_scorecard(conn: sqlite3.Connection, output: Path) -> None:
    entries = conn.execute(
        "SELECT * FROM scorecard_entries ORDER BY updated_at DESC"
    ).fetchall()
    if not entries:
        (output / "scorecard.md").write_text("# Scorecard\n\nNo entries yet.")
        return

    latest = entries[0]
    lines = [
        "# Scorecard",
        "",
        "| Question | Answer |",
        "|----------|--------|",
        f"| Right Customer? | {latest['right_customer']} |",
        f"| Right Problem? | {latest['right_problem']} |",
        f"| Right Approach? | {latest['right_approach']} |",
        f"| Will They Switch? | {latest['will_they_switch']} |",
        f"| Right Differentiation? | {latest['right_differentiation']} |",
        f"| Does It Click? | {latest['does_it_click']} |",
        "",
        f"**Notes:** {latest['notes']}",
    ]

    if len(entries) > 1:
        lines.extend(["", "## History"])
        for e in entries[1:]:
            lines.append(f"- {e['updated_at']}: {e['notes']}")

    (output / "scorecard.md").write_text("\n".join(lines))


def _generate_learnings(conn: sqlite3.Connection, output: Path) -> None:
    learnings = conn.execute(
        "SELECT * FROM learnings ORDER BY lesson_number, created_at"
    ).fetchall()
    if not learnings:
        (output / "learnings.md").write_text("# Learnings\n\nNo learnings recorded yet.")
        return

    lines = ["# Learnings", ""]
    current = None
    for l in learnings:
        if l["lesson_number"] != current:
            current = l["lesson_number"]
            lines.append(f"## Lesson {current}")
        lines.append(f"- {l['insight']} _(from {l['source_type']})_")

    (output / "learnings.md").write_text("\n".join(lines))


def _generate_pivot_history(conn: sqlite3.Connection, output: Path) -> None:
    pivots = conn.execute(
        "SELECT p.*, h.version, h.customer, h.problem, h.approach "
        "FROM pivots p JOIN hypotheses h ON p.new_hypothesis_id = h.id "
        "ORDER BY p.created_at"
    ).fetchall()
    if not pivots:
        (output / "pivot-history.md").write_text("# Pivot History\n\nNo pivots yet.")
        return

    lines = ["# Pivot History", ""]
    for p in pivots:
        lines.extend([
            f"## Version {p['version']}",
            f"- **Changed:** {p['what_changed']}",
            f"- **Reason:** {p['reason']}",
            f"- **New hypothesis:** Help {p['customer']} solve {p['problem']} with {p['approach']}",
            "",
        ])

    (output / "pivot-history.md").write_text("\n".join(lines))


def _generate_latest_sprint(conn: sqlite3.Connection, output: Path) -> None:
    sprint = conn.execute(
        "SELECT * FROM design_sprints ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    if not sprint:
        return

    sprints_dir = output / "sprints"
    sprints_dir.mkdir(exist_ok=True)

    lines = [
        f"# Design Sprint {sprint['id']}",
        "",
        f"**Risk Question:** {sprint['risk_question']}",
        f"**Status:** {sprint['status']}",
        "",
    ]

    for day in ("map", "sketch", "decide", "prototype", "test"):
        val = sprint[f"day_{day}"]
        if val:
            lines.append(f"## {day.title()}")
            lines.append(val)
            lines.append("")

    if sprint["outcome"]:
        lines.append("## Outcome")
        lines.append(sprint["outcome"])

    (sprints_dir / f"sprint-{sprint['id']}.md").write_text("\n".join(lines))
