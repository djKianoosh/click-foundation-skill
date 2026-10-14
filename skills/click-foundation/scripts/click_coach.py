#!/usr/bin/env python3
"""Click Coach CLI - Deterministic state and methodology management for Click Foundation and Design Sprints.

Can be run directly by agents (Antigravity, Claude Code) or founders from the terminal.
"""

import argparse
import json
import sys
from pathlib import Path

# Ensure local script directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from db import (
    create_foundation_sprint,
    create_project,
    get_connection,
    get_project,
    init_db,
)
from docs_generator import generate_docs
from tools import (
    create_design_sprint,
    get_project_context,
    log_sprint_day,
    query_learnings,
    record_learning,
    record_test_results,
    revise_hypothesis,
    save_approach,
    save_basics,
    save_differentiation,
    save_founding_hypothesis,
    save_magic_lens,
    show_scorecard,
    update_scorecard,
    update_sprint_outcome,
)


def find_click_dir() -> Path:
    """Find the .click directory in current or parent directories."""
    current = Path.cwd().resolve()
    for parent in [current, *current.parents]:
        click_dir = parent / ".click"
        if click_dir.is_dir():
            return click_dir
    sys.stderr.write("Error: Not a Click project. Run 'click_coach.py init' first.\n")
    sys.exit(1)


def get_db_path() -> str:
    return str(find_click_dir() / "click.db")


def get_default_output_dir() -> str:
    click_dir = find_click_dir()
    return str(click_dir.parent / "click-output")


def get_project_id(conn) -> int:
    project = conn.execute("SELECT id FROM projects ORDER BY id LIMIT 1").fetchone()
    if not project:
        sys.stderr.write("Error: No project found. Run 'click_coach.py init' first.\n")
        sys.exit(1)
    return project["id"]


def get_current_sprint_id(conn, project_id: int) -> int:
    sprint = conn.execute(
        "SELECT id FROM foundation_sprints WHERE project_id = ? AND status = 'in_progress' ORDER BY created_at DESC LIMIT 1",
        (project_id,),
    ).fetchone()
    if sprint:
        return sprint["id"]
    latest = conn.execute(
        "SELECT id FROM foundation_sprints WHERE project_id = ? ORDER BY created_at DESC LIMIT 1",
        (project_id,),
    ).fetchone()
    if latest:
        return latest["id"]
    return create_foundation_sprint(conn, project_id)


# ==============================================================================
# CLI Handlers
# ==============================================================================


def cmd_init(args):
    click_dir = Path.cwd() / ".click"
    if click_dir.exists():
        print(f"Click is already initialized in {click_dir}")
        return 0

    click_dir.mkdir(parents=True, exist_ok=True)
    db_path = str(click_dir / "click.db")
    init_db(db_path)

    project_name = args.name or Path.cwd().name
    conn = get_connection(db_path)
    create_project(conn, project_name)
    conn.close()

    out_dir = Path.cwd() / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Initialized Click project '{project_name}'.")
    print(f"  Database: {db_path}")
    print(f"  Output directory: {out_dir}")
    return 0


def cmd_foundation_show(_args):
    conn = get_connection(get_db_path())
    project_id = get_project_id(conn)
    print(get_project_context(conn, project_id))
    conn.close()
    return 0


def cmd_foundation_list(_args):
    conn = get_connection(get_db_path())
    project_id = get_project_id(conn)
    sprints = conn.execute(
        "SELECT id, status, current_step, created_at FROM foundation_sprints WHERE project_id = ?",
        (project_id,),
    ).fetchall()
    if not sprints:
        print("No Foundation Sprints recorded yet.")
    for s in sprints:
        print(f"  #{s['id']} [{s['status']}] step: {s['current_step']} ({s['created_at']})")
    conn.close()
    return 0


def cmd_foundation_save_basics(args):
    conn = get_connection(get_db_path())
    project_id = get_project_id(conn)
    sprint_id = args.sprint_id or get_current_sprint_id(conn, project_id)

    alts = (
        [a.strip() for a in args.alternatives.split(",") if a.strip()] if args.alternatives else []
    )
    result = save_basics(
        conn,
        sprint_id,
        customer=args.customer,
        problem=args.problem,
        capability=args.capability,
        insight=args.insight,
        motivation=args.motivation,
        gorilla=args.gorilla,
        alternatives=alts,
    )
    conn.close()
    print(result)
    return 0


def cmd_foundation_save_differentiation(args):
    conn = get_connection(get_db_path())
    project_id = get_project_id(conn)
    sprint_id = args.sprint_id or get_current_sprint_id(conn, project_id)

    axes = {
        "x_low": args.axes_x_low,
        "x_high": args.axes_x_high,
        "y_low": args.axes_y_low,
        "y_high": args.axes_y_high,
    }
    prins = [p.strip() for p in args.principles.split(",") if p.strip()]
    result = save_differentiation(
        conn,
        sprint_id,
        differentiator_1=args.diff1,
        differentiator_2=args.diff2,
        diff_2x2_axes=axes,
        principles=prins,
    )
    conn.close()
    print(result)
    return 0 if "Error" not in result else 1


def cmd_foundation_save_approach(args):
    conn = get_connection(get_db_path())
    project_id = get_project_id(conn)
    sprint_id = args.sprint_id or get_current_sprint_id(conn, project_id)

    result = save_approach(
        conn,
        sprint_id,
        title=args.title,
        summary=args.summary,
        how_it_works=args.how_it_works,
        is_top_bet=args.top_bet,
        is_backup=args.backup,
    )
    conn.close()
    print(result)
    return 0


def cmd_foundation_save_hypothesis(args):
    conn = get_connection(get_db_path())
    project_id = get_project_id(conn)
    sprint_id = args.sprint_id or get_current_sprint_id(conn, project_id)

    result = save_founding_hypothesis(
        conn,
        sprint_id,
        project_id,
        customer=args.customer,
        problem=args.problem,
        approach=args.approach,
        competitors=args.competitors,
        differentiation=args.differentiation,
    )
    conn.close()
    print(result)
    return 0


def cmd_foundation_save_magic_lens(args):
    conn = get_connection(get_db_path())
    project_id = get_project_id(conn)
    sprint_id = args.sprint_id or get_current_sprint_id(conn, project_id)

    try:
        evals = json.loads(args.evaluations_json)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Error parsing evaluations JSON: {e}\n")
        conn.close()
        return 1

    result = save_magic_lens(
        conn,
        sprint_id,
        lens_name=args.lens_name,
        x_axis_low=args.axes_x_low,
        x_axis_high=args.axes_x_high,
        y_axis_low=args.axes_y_low,
        y_axis_high=args.axes_y_high,
        evaluations=evals,
    )
    conn.close()
    print(result)
    return 0 if "Error" not in result else 1


def cmd_scorecard_show(_args):
    conn = get_connection(get_db_path())
    project_id = get_project_id(conn)
    project = get_project(conn, project_id)
    hyp_id = project["current_hypothesis_id"] if project else None
    if not hyp_id:
        print("No Founding Hypothesis yet. Run a Foundation Sprint first.")
        conn.close()
        return 0

    print(show_scorecard(conn, hyp_id))
    conn.close()
    return 0


def cmd_scorecard_update(args):
    conn = get_connection(get_db_path())
    project_id = get_project_id(conn)
    project = get_project(conn, project_id)
    hyp_id = project["current_hypothesis_id"] if project else None
    if not hyp_id:
        sys.stderr.write("Error: No Founding Hypothesis yet. Complete Foundation Sprint first.\n")
        conn.close()
        return 1

    result = update_scorecard(
        conn,
        hyp_id,
        right_customer=args.right_customer,
        right_problem=args.right_problem,
        right_approach=args.right_approach,
        will_they_switch=args.will_they_switch,
        right_differentiation=args.right_differentiation,
        does_it_click=args.does_it_click,
        notes=args.notes or "",
    )
    conn.close()
    print(result)
    return 0 if "Error" not in result else 1


def cmd_hypothesis_show(_args):
    conn = get_connection(get_db_path())
    project_id = get_project_id(conn)
    print(get_project_context(conn, project_id))
    conn.close()
    return 0


def cmd_hypothesis_update(args):
    conn = get_connection(get_db_path())
    project_id = get_project_id(conn)
    project = get_project(conn, project_id)
    hyp_id = project["current_hypothesis_id"] if project else None
    if not hyp_id:
        sys.stderr.write("Error: No Founding Hypothesis yet.\n")
        conn.close()
        return 1

    result = revise_hypothesis(
        conn,
        project_id,
        hyp_id,
        customer=args.customer,
        problem=args.problem,
        approach=args.approach,
        competitors=args.competitors,
        differentiation=args.differentiation,
        reason=args.reason,
        what_changed=args.what_changed,
    )
    conn.close()
    print(result)
    return 0 if "Error" not in result else 1


def cmd_sprint_new(args):
    conn = get_connection(get_db_path())
    project_id = get_project_id(conn)
    project = get_project(conn, project_id)
    hyp_id = project["current_hypothesis_id"] if project else None
    if not hyp_id:
        sys.stderr.write("Error: No Founding Hypothesis yet. Complete Foundation Sprint first.\n")
        conn.close()
        return 1

    result = create_design_sprint(conn, hyp_id, risk_question=args.risk_question)
    conn.close()
    print(result)
    return 0


def cmd_sprint_log(args):
    conn = get_connection(get_db_path())
    result = log_sprint_day(conn, args.sprint_id, day=args.day, notes=args.notes)
    conn.close()
    print(result)
    return 0 if "Error" not in result else 1


def cmd_sprint_test(args):
    conn = get_connection(get_db_path())
    try:
        reactions = json.loads(args.reactions_json)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Error parsing reactions JSON: {e}\n")
        conn.close()
        return 1

    result = record_test_results(conn, args.sprint_id, reactions=reactions)
    conn.close()
    print(result)
    return 0 if "Error" not in result else 1


def cmd_sprint_complete(args):
    conn = get_connection(get_db_path())
    result = update_sprint_outcome(
        conn,
        args.sprint_id,
        outcome=args.outcome,
        hypothesis_changed=args.hypothesis_changed,
    )
    conn.close()
    print(result)
    return 0


def cmd_sprint_show(args):
    conn = get_connection(get_db_path())
    sprint = conn.execute("SELECT * FROM design_sprints WHERE id = ?", (args.sprint_id,)).fetchone()
    if not sprint:
        sys.stderr.write(f"Error: Design Sprint #{args.sprint_id} not found.\n")
        conn.close()
        return 1

    print(f"Sprint #{sprint['id']} [{sprint['status']}]")
    print(f"  Risk Question: {sprint['risk_question']}")
    for day in ("map", "sketch", "decide", "prototype", "test"):
        if sprint[f"day_{day}"]:
            print(f"  Day {day.title()}: {sprint[f'day_{day}']}")
    if sprint["outcome"]:
        print(f"  Outcome: {sprint['outcome']}")
    conn.close()
    return 0


def cmd_sprint_list(_args):
    conn = get_connection(get_db_path())
    project_id = get_project_id(conn)
    project = get_project(conn, project_id)
    hyp_id = project["current_hypothesis_id"] if project else None
    if not hyp_id:
        print("No Founding Hypothesis yet.")
        conn.close()
        return 0

    sprints = conn.execute(
        "SELECT id, risk_question, status, created_at FROM design_sprints WHERE hypothesis_id = ?",
        (hyp_id,),
    ).fetchall()
    if not sprints:
        print("No Design Sprints found for current hypothesis.")
    for s in sprints:
        print(f"  #{s['id']} [{s['status']}] {s['risk_question']} ({s['created_at']})")
    conn.close()
    return 0


def cmd_learnings_show(_args):
    conn = get_connection(get_db_path())
    print(query_learnings(conn))
    conn.close()
    return 0


def cmd_learnings_record(args):
    conn = get_connection(get_db_path())
    result = record_learning(
        conn,
        source_type=args.source_type,
        source_id=args.source_id,
        insight=args.insight,
        lesson_number=args.lesson_number,
    )
    conn.close()
    print(result)
    return 0 if "Error" not in result else 1


def cmd_export_docs(args):
    conn = get_connection(get_db_path())
    out_dir = args.output_dir or get_default_output_dir()
    result = generate_docs(conn, out_dir, doc_type=args.type)
    conn.close()
    print(result)
    return 0


def cmd_status(_args):
    conn = get_connection(get_db_path())
    project_id = get_project_id(conn)
    project = get_project(conn, project_id)
    print(f"Project: {project['name']} (ID: {project['id']})")
    print(f"Created: {project['created_at']}")

    sprint = conn.execute(
        "SELECT id, current_step, status, created_at FROM foundation_sprints WHERE project_id = ? ORDER BY created_at DESC LIMIT 1",
        (project_id,),
    ).fetchone()
    if sprint:
        print(
            f"Foundation Sprint: #{sprint['id']} [status: {sprint['status']}, step: {sprint['current_step']}]"
        )
    else:
        print("Foundation Sprint: None started yet.")

    hyp_id = project["current_hypothesis_id"]
    if hyp_id:
        hyp = conn.execute(
            "SELECT version, created_at FROM hypotheses WHERE id = ?", (hyp_id,)
        ).fetchone()
        print(f"Founding Hypothesis: v{hyp['version']} (active)")
    else:
        print("Founding Hypothesis: Not yet formulated.")

    conn.close()
    return 0


# ==============================================================================
# Argument Parsing Setup
# ==============================================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="click_coach.py",
        description="Click Coach - Deterministic State & Automation Tool for Click Sprints.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # init
    p_init = subparsers.add_parser("init", help="Initialize Click in current directory")
    p_init.add_argument("--name", help="Project name (defaults to current folder name)")
    p_init.add_argument(
        "--output-dir",
        default="click-output",
        help="Output directory for generated docs",
    )
    p_init.set_defaults(func=cmd_init)

    # status
    p_status = subparsers.add_parser(
        "status", help="Show current sprint status and project progress"
    )
    p_status.set_defaults(func=cmd_status)

    # export-docs
    p_docs = subparsers.add_parser("export-docs", help="Generate markdown documentation")
    p_docs.add_argument("--output-dir", help="Target output directory")
    p_docs.add_argument(
        "--type",
        default="all",
        choices=[
            "all",
            "foundation",
            "scorecard",
            "learnings",
            "pivot_history",
            "sprint",
        ],
    )
    p_docs.set_defaults(func=cmd_export_docs)

    # foundation
    p_foundation = subparsers.add_parser("foundation", help="Foundation sprint operations")
    sub_f = p_foundation.add_subparsers(dest="subcommand", help="Foundation subcommands")

    f_show = sub_f.add_parser("show", help="Show current Foundation Sprint results")
    f_show.set_defaults(func=cmd_foundation_show)

    f_list = sub_f.add_parser("list", help="List all Foundation Sprints")
    f_list.set_defaults(func=cmd_foundation_list)

    f_basics = sub_f.add_parser(
        "save-basics", help="Save customer, problem, advantages, and competition"
    )
    f_basics.add_argument("--sprint-id", type=int, help="Optional sprint ID")
    f_basics.add_argument("--customer", required=True)
    f_basics.add_argument("--problem", required=True)
    f_basics.add_argument("--capability", required=True)
    f_basics.add_argument("--insight", required=True)
    f_basics.add_argument("--motivation", required=True)
    f_basics.add_argument("--gorilla", required=True)
    f_basics.add_argument("--alternatives", help="Comma-separated alternatives")
    f_basics.set_defaults(func=cmd_foundation_save_basics)

    f_diff = sub_f.add_parser(
        "save-differentiation", help="Save 2x2 axes, differentiators, and 3 principles"
    )
    f_diff.add_argument("--sprint-id", type=int, help="Optional sprint ID")
    f_diff.add_argument("--diff1", required=True)
    f_diff.add_argument("--diff2", required=True)
    f_diff.add_argument("--axes-x-low", required=True)
    f_diff.add_argument("--axes-x-high", required=True)
    f_diff.add_argument("--axes-y-low", required=True)
    f_diff.add_argument("--axes-y-high", required=True)
    f_diff.add_argument("--principles", required=True, help="3 comma-separated principles")
    f_diff.set_defaults(func=cmd_foundation_save_differentiation)

    f_app = sub_f.add_parser("save-approach", help="Save approach option")
    f_app.add_argument("--sprint-id", type=int, help="Optional sprint ID")
    f_app.add_argument("--title", required=True)
    f_app.add_argument("--summary", required=True)
    f_app.add_argument("--how-it-works", required=True)
    f_app.add_argument("--top-bet", action="store_true")
    f_app.add_argument("--backup", action="store_true")
    f_app.set_defaults(func=cmd_foundation_save_approach)

    f_lens = sub_f.add_parser("save-magic-lens", help="Save magic lens evaluation")
    f_lens.add_argument("--sprint-id", type=int, help="Optional sprint ID")
    f_lens.add_argument("--lens-name", required=True)
    f_lens.add_argument("--axes-x-low", required=True)
    f_lens.add_argument("--axes-x-high", required=True)
    f_lens.add_argument("--axes-y-low", required=True)
    f_lens.add_argument("--axes-y-high", required=True)
    f_lens.add_argument(
        "--evaluations-json",
        required=True,
        help="JSON list of {approach_id, x_position, y_position}",
    )
    f_lens.set_defaults(func=cmd_foundation_save_magic_lens)

    f_hyp = sub_f.add_parser("save-hypothesis", help="Save founding hypothesis")
    f_hyp.add_argument("--sprint-id", type=int, help="Optional sprint ID")
    f_hyp.add_argument("--customer", required=True)
    f_hyp.add_argument("--problem", required=True)
    f_hyp.add_argument("--approach", required=True)
    f_hyp.add_argument("--competitors", required=True)
    f_hyp.add_argument("--differentiation", required=True)
    f_hyp.set_defaults(func=cmd_foundation_save_hypothesis)

    # scorecard
    p_sc = subparsers.add_parser("scorecard", help="Scorecard operations")
    sub_sc = p_sc.add_subparsers(dest="subcommand", help="Scorecard subcommands")

    sc_show = sub_sc.add_parser("show", help="Show current scorecard")
    sc_show.set_defaults(func=cmd_scorecard_show)

    sc_up = sub_sc.add_parser("update", help="Update scorecard answers and evidence")
    sc_up.add_argument("--right-customer", required=True, choices=["yes", "maybe", "not_yet", "no"])
    sc_up.add_argument("--right-problem", required=True, choices=["yes", "maybe", "not_yet", "no"])
    sc_up.add_argument("--right-approach", required=True, choices=["yes", "maybe", "not_yet", "no"])
    sc_up.add_argument(
        "--will-they-switch", required=True, choices=["yes", "maybe", "not_yet", "no"]
    )
    sc_up.add_argument(
        "--right-differentiation",
        required=True,
        choices=["yes", "maybe", "not_yet", "no"],
    )
    sc_up.add_argument("--does-it-click", required=True, choices=["yes", "maybe", "not_yet", "no"])
    sc_up.add_argument("--notes", default="")
    sc_up.set_defaults(func=cmd_scorecard_update)

    # hypothesis
    p_hyp = subparsers.add_parser("hypothesis", help="Founding hypothesis operations")
    sub_hyp = p_hyp.add_subparsers(dest="subcommand", help="Hypothesis subcommands")

    h_show = sub_hyp.add_parser("show", help="Show current hypothesis")
    h_show.set_defaults(func=cmd_hypothesis_show)

    h_up = sub_hyp.add_parser("update", help="Revise hypothesis based on learnings")
    h_up.add_argument("--customer", required=True)
    h_up.add_argument("--problem", required=True)
    h_up.add_argument("--approach", required=True)
    h_up.add_argument("--competitors", required=True)
    h_up.add_argument("--differentiation", required=True)
    h_up.add_argument("--reason", required=True)
    h_up.add_argument("--what-changed", required=True)
    h_up.set_defaults(func=cmd_hypothesis_update)

    # sprint (Design Sprint)
    p_sprint = subparsers.add_parser("sprint", help="Design sprint operations")
    sub_sp = p_sprint.add_subparsers(dest="subcommand", help="Design sprint subcommands")

    sp_new = sub_sp.add_parser("new", help="Create a new Design Sprint")
    sp_new.add_argument("--risk-question", required=True)
    sp_new.set_defaults(func=cmd_sprint_new)

    sp_log = sub_sp.add_parser("log", help="Log a day in the sprint")
    sp_log.add_argument("--sprint-id", type=int, required=True)
    sp_log.add_argument(
        "--day", required=True, choices=["map", "sketch", "decide", "prototype", "test"]
    )
    sp_log.add_argument("--notes", required=True)
    sp_log.set_defaults(func=cmd_sprint_log)

    sp_test = sub_sp.add_parser("test", help="Record test reactions")
    sp_test.add_argument("--sprint-id", type=int, required=True)
    sp_test.add_argument(
        "--reactions-json",
        required=True,
        help="JSON array of {customer, reaction, is_reaction}",
    )
    sp_test.set_defaults(func=cmd_sprint_test)

    sp_comp = sub_sp.add_parser("complete", help="Complete design sprint")
    sp_comp.add_argument("--sprint-id", type=int, required=True)
    sp_comp.add_argument("--outcome", required=True)
    sp_comp.add_argument("--hypothesis-changed", action="store_true")
    sp_comp.set_defaults(func=cmd_sprint_complete)

    sp_show = sub_sp.add_parser("show", help="Show sprint details")
    sp_show.add_argument("--sprint-id", type=int, required=True)
    sp_show.set_defaults(func=cmd_sprint_show)

    sp_list = sub_sp.add_parser("list", help="List design sprints")
    sp_list.set_defaults(func=cmd_sprint_list)

    # learnings
    p_learn = subparsers.add_parser("learnings", help="Learnings operations")
    sub_l = p_learn.add_subparsers(dest="subcommand", help="Learnings subcommands")

    l_show = sub_l.add_parser("show", help="Show accumulated learnings")
    l_show.set_defaults(func=cmd_learnings_show)

    l_rec = sub_l.add_parser("record", help="Record a learning tagged with a lesson number (1-10)")
    l_rec.add_argument(
        "--source-type",
        required=True,
        choices=["foundation_sprint", "design_sprint", "pivot"],
    )
    l_rec.add_argument("--source-id", type=int)
    l_rec.add_argument("--insight", required=True)
    l_rec.add_argument("--lesson-number", type=int, required=True)
    l_rec.set_defaults(func=cmd_learnings_record)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # If subcommands invoked without sub-subcommand, provide intelligent defaults
    if args.command == "foundation" and not getattr(args, "subcommand", None):
        return cmd_foundation_show(args)
    if args.command == "scorecard" and not getattr(args, "subcommand", None):
        return cmd_scorecard_show(args)
    if args.command == "hypothesis" and not getattr(args, "subcommand", None):
        return cmd_hypothesis_show(args)
    if args.command == "learnings" and not getattr(args, "subcommand", None):
        return cmd_learnings_show(args)
    if args.command == "sprint" and not getattr(args, "subcommand", None):
        return cmd_sprint_list(args)

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
