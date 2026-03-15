"""Agent setup: registers tools via SDK MCP server, runs the agent loop."""

import sqlite3
from pathlib import Path

from claude_agent_sdk import (
    tool,
    create_sdk_mcp_server,
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
)

from click_agent.db import get_connection
from click_agent.tools.foundation import (
    save_basics,
    save_differentiation,
    save_approach,
    save_magic_lens,
    save_founding_hypothesis,
)
from click_agent.tools.design_sprint import (
    create_design_sprint,
    log_sprint_day,
    record_test_results,
    update_sprint_outcome,
)
from click_agent.tools.scorecard import update_scorecard, show_scorecard
from click_agent.tools.context import (
    get_project_context,
    query_learnings,
    record_learning,
    revise_hypothesis,
)
from click_agent.docs_generator import generate_docs
from click_agent.prompts import SYSTEM_PROMPT


def _make_tools(db_path: str, project_id: int, output_dir: str):
    """Create MCP tool functions bound to the current db and project."""
    conn = get_connection(db_path)

    def _get_sprint_id():
        sprint = conn.execute(
            "SELECT id FROM foundation_sprints WHERE project_id = ? AND status = 'in_progress' ORDER BY created_at DESC LIMIT 1",
            (project_id,),
        ).fetchone()
        if sprint:
            return sprint["id"]
        complete = conn.execute(
            "SELECT id FROM foundation_sprints WHERE project_id = ? ORDER BY created_at DESC LIMIT 1",
            (project_id,),
        ).fetchone()
        return complete["id"] if complete else None

    def _get_hypothesis_id():
        project = conn.execute("SELECT current_hypothesis_id FROM projects WHERE id = ?", (project_id,)).fetchone()
        return project["current_hypothesis_id"] if project else None

    @tool(
        "save_basics",
        "Save the Basics card: customer, problem, advantages (capability/insight/motivation), competitors (gorilla + alternatives)",
        {"customer": str, "problem": str, "capability": str, "insight": str, "motivation": str, "gorilla": str, "alternatives": list},
    )
    async def tool_save_basics(args):
        result = save_basics(conn, _get_sprint_id(), **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool(
        "save_differentiation",
        "Save differentiation: 2x2 chart axes, 2 differentiators, and 3 practical principles",
        {"differentiator_1": str, "differentiator_2": str, "diff_2x2_axes": dict, "principles": list},
    )
    async def tool_save_differentiation(args):
        result = save_differentiation(conn, _get_sprint_id(), **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool(
        "save_approach",
        "Save an approach option with title, one-sentence summary, and how it works",
        {"title": str, "summary": str, "how_it_works": str, "is_top_bet": bool, "is_backup": bool},
    )
    async def tool_save_approach(args):
        result = save_approach(conn, _get_sprint_id(), **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool(
        "save_magic_lens",
        "Save a Magic Lens 2x2 evaluation for comparing approaches through a specific perspective",
        {"lens_name": str, "x_axis_low": str, "x_axis_high": str, "y_axis_low": str, "y_axis_high": str, "evaluations": list},
    )
    async def tool_save_magic_lens(args):
        result = save_magic_lens(conn, _get_sprint_id(), **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool(
        "save_founding_hypothesis",
        "Save the Founding Hypothesis: If we help [customer] solve [problem] with [approach], they will choose it over [competitors] because our solution is [differentiation]",
        {"customer": str, "problem": str, "approach": str, "competitors": str, "differentiation": str},
    )
    async def tool_save_hypothesis(args):
        result = save_founding_hypothesis(conn, _get_sprint_id(), project_id, **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool(
        "update_scorecard",
        "Update the 6-question scorecard. Answers: yes, maybe, not_yet, no",
        {"right_customer": str, "right_problem": str, "right_approach": str, "will_they_switch": str, "right_differentiation": str, "does_it_click": str, "notes": str},
    )
    async def tool_update_scorecard(args):
        hyp_id = _get_hypothesis_id()
        if not hyp_id:
            return {"content": [{"type": "text", "text": "Error: No hypothesis exists yet."}]}
        result = update_scorecard(conn, hyp_id, **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool("show_scorecard", "Show the current scorecard status with evidence trail", {})
    async def tool_show_scorecard(args):
        hyp_id = _get_hypothesis_id()
        if not hyp_id:
            return {"content": [{"type": "text", "text": "No hypothesis exists yet."}]}
        result = show_scorecard(conn, hyp_id)
        return {"content": [{"type": "text", "text": result}]}

    @tool("create_design_sprint", "Create a new Design Sprint to test a specific risk question", {"risk_question": str})
    async def tool_create_sprint(args):
        hyp_id = _get_hypothesis_id()
        if not hyp_id:
            return {"content": [{"type": "text", "text": "Error: No hypothesis. Run Foundation Sprint first."}]}
        result = create_design_sprint(conn, hyp_id, **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool("log_sprint_day", "Log what happened on a day of the Design Sprint (map, sketch, decide, prototype, test)", {"sprint_id": int, "day": str, "notes": str})
    async def tool_log_day(args):
        result = log_sprint_day(conn, args.pop("sprint_id"), **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool("record_test_results", "Record customer reactions from testing. Distinguish reactions (genuine responses) from feedback (what they say).", {"sprint_id": int, "reactions": list})
    async def tool_record_results(args):
        result = record_test_results(conn, args.pop("sprint_id"), reactions=args["reactions"])
        return {"content": [{"type": "text", "text": result}]}

    @tool("update_sprint_outcome", "Record the Design Sprint outcome and whether the hypothesis needs revision", {"sprint_id": int, "outcome": str, "hypothesis_changed": bool})
    async def tool_update_outcome(args):
        result = update_sprint_outcome(conn, args.pop("sprint_id"), **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool("get_project_context", "Load current project context: hypothesis, scorecard, sprint history", {})
    async def tool_get_context(args):
        result = get_project_context(conn, project_id)
        return {"content": [{"type": "text", "text": result}]}

    @tool("query_learnings", "Retrieve accumulated learnings organized by the 10 Click lessons", {})
    async def tool_query_learnings(args):
        result = query_learnings(conn)
        return {"content": [{"type": "text", "text": result}]}

    @tool("record_learning", "Record a learning tagged with one of the 10 Click lessons (1-10)", {"source_type": str, "source_id": int, "insight": str, "lesson_number": int})
    async def tool_record_learning(args):
        result = record_learning(conn, **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool("revise_hypothesis", "Create a new hypothesis version based on Design Sprint learnings", {"customer": str, "problem": str, "approach": str, "competitors": str, "differentiation": str, "reason": str, "what_changed": str})
    async def tool_revise(args):
        hyp_id = _get_hypothesis_id()
        if not hyp_id:
            return {"content": [{"type": "text", "text": "Error: No hypothesis to revise."}]}
        result = revise_hypothesis(conn, project_id, hyp_id, **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool("generate_docs", "Generate markdown documents. doc_type: all, foundation, sprint, scorecard, learnings, pivot_history", {"doc_type": str})
    async def tool_generate_docs(args):
        result = generate_docs(conn, output_dir, **args)
        return {"content": [{"type": "text", "text": result}]}

    return [
        tool_save_basics, tool_save_differentiation, tool_save_approach,
        tool_save_magic_lens, tool_save_hypothesis,
        tool_update_scorecard, tool_show_scorecard,
        tool_create_sprint, tool_log_day, tool_record_results, tool_update_outcome,
        tool_get_context, tool_query_learnings, tool_record_learning, tool_revise,
        tool_generate_docs,
    ]


async def run_agent(
    db_path: str,
    project_id: int,
    output_dir: str,
    prompt: str,
    system_prompt: str = SYSTEM_PROMPT,
) -> None:
    """Run the Click agent with the given prompt."""
    tools = _make_tools(db_path, project_id, output_dir)
    server = create_sdk_mcp_server("click-tools", tools=tools)

    options = ClaudeAgentOptions(
        mcp_servers={"click": server},
        system_prompt=system_prompt,
        model="claude-opus-4-6",
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text, end="", flush=True)
            elif isinstance(message, ResultMessage):
                if message.result:
                    print(message.result)
