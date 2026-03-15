"""Typer CLI entry point for Click agent."""

import asyncio
from pathlib import Path

import typer

from click_agent.db import (
    init_db,
    get_connection,
    create_project,
    create_foundation_sprint,
    get_project,
)
from click_agent.agent import run_agent
from click_agent.tools.context import get_project_context, query_learnings
from click_agent.tools.scorecard import show_scorecard
from click_agent.prompts import SYSTEM_PROMPT, FOUNDATION_SPRINT_PROMPT, DESIGN_SPRINT_PROMPT

app = typer.Typer(name="click-coach", help="Click - AI Product Coach")
foundation_app = typer.Typer(help="Foundation Sprint commands")
sprint_app = typer.Typer(help="Design Sprint commands")
hypothesis_app = typer.Typer(help="Hypothesis commands")
scorecard_app = typer.Typer(help="Scorecard commands")

app.add_typer(foundation_app, name="foundation")
app.add_typer(sprint_app, name="sprint")
app.add_typer(hypothesis_app, name="hypothesis")
app.add_typer(scorecard_app, name="scorecard")


def _find_click_dir() -> Path:
    """Find the .click directory in current or parent directories."""
    current = Path.cwd()
    while current != current.parent:
        click_dir = current / ".click"
        if click_dir.exists():
            return click_dir
        current = current.parent
    typer.echo("Error: Not a Click project. Run 'click-coach init' first.")
    raise typer.Exit(1)


def _get_db_path() -> str:
    return str(_find_click_dir() / "click.db")


def _get_output_dir() -> str:
    click_dir = _find_click_dir()
    return str(click_dir.parent / "click-output")


def _get_project_id(conn) -> int:
    project = conn.execute("SELECT id FROM projects ORDER BY id LIMIT 1").fetchone()
    if not project:
        typer.echo("Error: No project found. Run 'click-coach init' first.")
        raise typer.Exit(1)
    return project["id"]


@app.command()
def init(
    output_dir: str = typer.Option("click-output", help="Output directory for generated docs"),
):
    """Initialize Click in the current project directory."""
    click_dir = Path.cwd() / ".click"
    if click_dir.exists():
        typer.echo("Click is already initialized in this directory.")
        raise typer.Exit(0)

    name = typer.prompt("Project name")

    click_dir.mkdir()
    db_path = str(click_dir / "click.db")
    init_db(db_path)

    conn = get_connection(db_path)
    project_id = create_project(conn, name)
    conn.close()

    out = Path.cwd() / output_dir
    out.mkdir(exist_ok=True)

    typer.echo(f"Initialized Click for '{name}'.")
    typer.echo(f"  Database: {db_path}")
    typer.echo(f"  Output: {out}")


@foundation_app.callback(invoke_without_command=True)
def foundation(ctx: typer.Context):
    """Start or resume a Foundation Sprint."""
    if ctx.invoked_subcommand is not None:
        return

    db_path = _get_db_path()
    conn = get_connection(db_path)
    project_id = _get_project_id(conn)

    sprint = conn.execute(
        "SELECT * FROM foundation_sprints WHERE project_id = ? AND status = 'in_progress' ORDER BY created_at DESC LIMIT 1",
        (project_id,),
    ).fetchone()

    if not sprint:
        sprint_id = create_foundation_sprint(conn, project_id)
        typer.echo("Starting a new Foundation Sprint...")
    else:
        typer.echo(f"Resuming Foundation Sprint (currently on: {sprint['current_step']})...")

    context = get_project_context(conn, project_id)
    conn.close()

    prompt = FOUNDATION_SPRINT_PROMPT.format(context=context)
    asyncio.run(run_agent(db_path, project_id, _get_output_dir(), prompt))


@foundation_app.command("show")
def foundation_show():
    """Show the current/most recent Foundation Sprint results."""
    conn = get_connection(_get_db_path())
    project_id = _get_project_id(conn)
    typer.echo(get_project_context(conn, project_id))
    conn.close()


@foundation_app.command("list")
def foundation_list():
    """List all Foundation Sprints."""
    conn = get_connection(_get_db_path())
    project_id = _get_project_id(conn)
    sprints = conn.execute(
        "SELECT id, status, current_step, created_at FROM foundation_sprints WHERE project_id = ?",
        (project_id,),
    ).fetchall()
    for s in sprints:
        typer.echo(f"  #{s['id']} [{s['status']}] step: {s['current_step']} ({s['created_at']})")
    conn.close()


@sprint_app.callback(invoke_without_command=True)
def sprint(ctx: typer.Context):
    """Start a Design Sprint."""
    if ctx.invoked_subcommand is not None:
        return

    db_path = _get_db_path()
    conn = get_connection(db_path)
    project_id = _get_project_id(conn)

    project = get_project(conn, project_id)
    if not project["current_hypothesis_id"]:
        typer.echo("No Founding Hypothesis yet. Run 'click-coach foundation' first.")
        raise typer.Exit(1)

    context = get_project_context(conn, project_id)
    conn.close()

    prompt = DESIGN_SPRINT_PROMPT.format(context=context)
    asyncio.run(run_agent(db_path, project_id, _get_output_dir(), prompt))


@sprint_app.command("show")
def sprint_show(sprint_id: int):
    """Show a Design Sprint's details."""
    conn = get_connection(_get_db_path())
    sprint = conn.execute("SELECT * FROM design_sprints WHERE id = ?", (sprint_id,)).fetchone()
    if not sprint:
        typer.echo(f"Sprint #{sprint_id} not found.")
        raise typer.Exit(1)
    typer.echo(f"Sprint #{sprint['id']} [{sprint['status']}]")
    typer.echo(f"  Question: {sprint['risk_question']}")
    if sprint["outcome"]:
        typer.echo(f"  Outcome: {sprint['outcome']}")
    conn.close()


@sprint_app.command("list")
def sprint_list():
    """List all Design Sprints for the current hypothesis."""
    conn = get_connection(_get_db_path())
    project_id = _get_project_id(conn)
    project = get_project(conn, project_id)
    hyp_id = project["current_hypothesis_id"]
    if not hyp_id:
        typer.echo("No hypothesis yet.")
        raise typer.Exit(0)
    sprints = conn.execute(
        "SELECT id, risk_question, status, created_at FROM design_sprints WHERE hypothesis_id = ?",
        (hyp_id,),
    ).fetchall()
    for s in sprints:
        typer.echo(f"  #{s['id']} [{s['status']}] {s['risk_question']}")
    conn.close()


@hypothesis_app.callback(invoke_without_command=True)
def hypothesis(ctx: typer.Context):
    """Show current Founding Hypothesis + Scorecard."""
    if ctx.invoked_subcommand is not None:
        return
    conn = get_connection(_get_db_path())
    project_id = _get_project_id(conn)
    typer.echo(get_project_context(conn, project_id))
    conn.close()


@hypothesis_app.command("update")
def hypothesis_update():
    """Revise hypothesis based on learnings."""
    db_path = _get_db_path()
    conn = get_connection(db_path)
    project_id = _get_project_id(conn)
    context = get_project_context(conn, project_id)
    conn.close()

    prompt = f"The user wants to revise their Founding Hypothesis based on learnings.\n\n{context}\n\nGuide them through what to change and why."
    asyncio.run(run_agent(db_path, project_id, _get_output_dir(), prompt))


@scorecard_app.callback(invoke_without_command=True)
def scorecard(ctx: typer.Context):
    """Show current scorecard."""
    if ctx.invoked_subcommand is not None:
        return
    conn = get_connection(_get_db_path())
    project_id = _get_project_id(conn)
    project = get_project(conn, project_id)
    hyp_id = project["current_hypothesis_id"]
    if not hyp_id:
        typer.echo("No hypothesis yet. Run 'click-coach foundation' first.")
        raise typer.Exit(0)
    typer.echo(show_scorecard(conn, hyp_id))
    conn.close()


@scorecard_app.command("update")
def scorecard_update():
    """Update scorecard with new evidence."""
    db_path = _get_db_path()
    conn = get_connection(db_path)
    project_id = _get_project_id(conn)
    context = get_project_context(conn, project_id)
    conn.close()

    prompt = f"The user wants to update their Scorecard based on new evidence.\n\n{context}\n\nAsk what they learned and update the scorecard."
    asyncio.run(run_agent(db_path, project_id, _get_output_dir(), prompt))


@app.command()
def learnings():
    """Show accumulated learnings across all sprints."""
    conn = get_connection(_get_db_path())
    typer.echo(query_learnings(conn))
    conn.close()
