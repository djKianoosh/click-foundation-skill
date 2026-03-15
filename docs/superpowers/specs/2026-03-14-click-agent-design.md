# Click Agent — Design Specification

## Overview

Click is a Python CLI agent built on the Claude Agent SDK that acts as an autonomous product coach for solo founders and small teams. It guides users through the "Click" methodology (by Jake Knapp and John Zeratsky) via interactive dialogue, generates structured markdown deliverables, stores everything in SQLite, and evolves its methodology over time based on outcomes.

## The Click Methodology

The system from the book consists of two sprint types that work in sequence:

1. **Foundation Sprint** (2 days) — A strategy workshop that produces a Founding Hypothesis
2. **Design Sprints** (5 days each) — Tiny loops to test and prove the hypothesis

The overall flow: Foundation Sprint → Founding Hypothesis → Design Sprints (repeat until it clicks) → Build

### The 10 Lessons

These lessons are encoded into the agent's coaching behavior:

1. Drop everything and sprint on the most important challenge until it's done
2. Start by identifying your customer and a real problem you can solve
3. Take advantage of your advantages
4. Get real about the competition
5. Differentiation makes products click
6. Use practical principles to reinforce differentiation
7. Seek alternatives to your first idea
8. Consider conflicting opinions before you commit to an approach
9. It's just a hypothesis until you prove it
10. Experiment with tiny loops until your solution clicks. Then build it.

### Key Concepts & Tools

- **Note-and-Vote**: Collaboration method — work alone in silence, generate options, vote, Decider decides. The agent simulates this by prompting the user to brainstorm multiple options before converging.
- **The Decider**: The person who makes final calls. In a solo founder context, the user is always the Decider.
- **Magic Lenses**: 2x2 evaluation charts that compare approaches through different perspectives (customer, pragmatic, growth, money, plus custom lenses). Reveals which approach consistently scores well.
- **Founding Hypothesis**: A Mad Libs formula — "If we help [customer] solve [problem] with [approach], they will choose it over [competitors] because our solution is [differentiation]"
- **Scorecard**: Six validation questions — Right customer? Right problem? Right approach? Will they switch? Right differentiation? Does it click?
- **Mini Manifesto**: Differentiation 2x2 chart + 3 practical principles (differentiate, differentiate, safeguard)
- **Plain Language**: Replace jargon with simple words. Customers should be real people, problems should be real problems.
- **Common Sense Test**: After defining customer + problem, ask "Does this make sense?"

## Architecture

### Approach: Single-Agent with Tools

One Claude Agent SDK agent with a rich system prompt encoding the Click methodology. The agent uses tools for SQLite access, dialogue facilitation, and document generation. This keeps the architecture simple while supporting the full interactive workflow.

### CLI Commands

```
click init                # Initialize Click in a project directory (must run first)

click foundation          # Start/resume a Foundation Sprint (interactive dialogue)
click foundation show     # Show current/most recent Foundation Sprint results
click foundation list     # List all Foundation Sprints

click sprint              # Start a Design Sprint (5-day tiny loop)
click sprint show <id>    # Show a Design Sprint's details and test results
click sprint list         # List all Design Sprints for current hypothesis

click hypothesis          # Show current Founding Hypothesis + Scorecard
click hypothesis update   # Revise hypothesis based on learnings (creates new version + pivot record)

click scorecard           # Show current scorecard status with evidence trail
click scorecard update    # Update scorecard answers based on new evidence

click learnings           # Show accumulated learnings across all sprints
```

**`click init` behavior:**
- Creates a `.click/` directory in the project root
- Creates the SQLite database at `.click/click.db`
- Creates the `click-output/` directory for generated documents
- Prompts for a project name and creates the initial `projects` row
- The output directory is configurable: `click init --output-dir=docs/click/`

**Out-of-order safeguards:**
- `click sprint` requires a completed Foundation Sprint and Founding Hypothesis. If neither exists, the agent prompts the user to run `click foundation` first.
- `click hypothesis` with no hypothesis created shows a message guiding the user to `click foundation`.
- `click foundation` with an in-progress Foundation Sprint resumes from the last completed step (the current step is tracked in the `foundation_sprints.current_step` column).

### Agent Tools

**Foundation Sprint Tools:**

- `note_and_vote` — Guides the user through the Note-and-Vote process for any decision (customer, problem, advantages, competitors, differentiators, principles, approaches). The interaction pattern: (1) Agent asks the user to brainstorm and list multiple options; (2) Agent may suggest additional options the user hasn't considered; (3) Agent challenges options using plain language and common sense tests; (4) Agent asks the user to pick their top 2-3; (5) Agent asks the user (as Decider) to make the final choice. The agent participates as a thinking partner but the user always decides.
- `save_basics` — Stores the Basics card: customer, problem, advantages (capability/insight/motivation), competitors (gorilla + alternatives)
- `save_differentiation` — Stores the 2x2 chart axes, position, chosen differentiators, and 3 practical principles (differentiate, differentiate, safeguard)
- `save_mini_manifesto` — Stores the Mini Manifesto (differentiation + principles combined)
- `save_approach` — Stores approach options with one-page summaries (title, summary, how it works)
- `run_magic_lenses` — Guides evaluation of approaches through multiple lenses (customer, pragmatic, growth, money + custom). For each lens: (1) Agent proposes axis labels based on the lens perspective; (2) User confirms or adjusts axes; (3) Agent asks user to position each approach on the 2x2 (high/low on each axis); (4) Agent records positions and highlights patterns across lenses. Stores each lens as a 2x2 comparison.
- `save_founding_hypothesis` — Stores the Mad Libs: customer, problem, approach, competitors, differentiation. Sets this as the current hypothesis on the project.
- `revise_hypothesis` — Creates a new hypothesis version based on Design Sprint learnings. Records what changed (customer, problem, approach, competitors, or differentiation) and why in the `pivots` table. Updates the project's current hypothesis pointer.
- `update_scorecard` — Updates the 6-question scorecard. Each answer must be one of: `yes`, `maybe`, `not_yet`, `no`. Requires a `notes` field explaining the evidence.
- `show_scorecard` — Reads and displays the current scorecard state with evidence trail from all entries.

**Design Sprint Tools:**

- `create_design_sprint` — Creates a new 5-day sprint linked to the current hypothesis, with the specific risk/question being tested
- `log_sprint_day` — Records what happened on each day (map, sketch, decide, prototype, test)
- `record_test_results` — Captures customer reactions (not just feedback) from Friday testing. Distinguishes reactions vs. feedback per the book.
- `update_sprint_outcome` — Records whether the sprint validated/invalidated parts of the hypothesis, and what changed

**Cross-cutting Tools:**

- `query_learnings` — Retrieve patterns, validated/invalidated assumptions, and pivot history
- `generate_docs` — Produce markdown files. Takes a `doc_type` parameter: `all` (regenerate everything), `foundation` (Foundation Sprint summary + hypothesis card), `sprint` (latest Design Sprint report), `scorecard` (current scorecard), `learnings` (accumulated learnings), or `pivot_history` (hypothesis revision timeline). Defaults to `all`.
- `get_project_context` — Load current hypothesis, scorecard state, and sprint history to ground conversation

### Agent Dialogue Flows

**Foundation Sprint (`click foundation`):**

1. Agent loads any existing context via `get_project_context`
2. Walks through Day 1 Basics using `note_and_vote` for each: customer → problem → advantages → competitors
3. Applies common sense test: "Does this make sense?" Challenges jargon.
4. Moves to Differentiation: classic scales, custom differentiators, 2x2 chart, principles
5. Saves Mini Manifesto
6. Day 2 Approach: lists 3+ options, writes summaries, runs Magic Lenses
7. Presents Founding Hypothesis, asks user to fill in the blanks
8. Shows the Scorecard — "these are the questions your Design Sprints need to answer"
9. Generates all docs

**Design Sprint (`click sprint`):**

1. Agent shows the Scorecard and asks: "Which question do you most need to answer?"
2. Guides through Map → Sketch → Decide → Prototype → Test (compressed into dialogue)
3. After test results, updates the Scorecard
4. If something is invalidated, guides a hypothesis revision
5. Stores learnings for future sprints

### SQLite Schema

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    current_hypothesis_id INTEGER REFERENCES hypotheses(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE foundation_sprints (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    customer TEXT,
    problem TEXT,
    capability TEXT,
    insight TEXT,
    motivation TEXT,
    gorilla TEXT,
    alternatives TEXT,          -- JSON array
    differentiator_1 TEXT,
    differentiator_2 TEXT,
    diff_2x2_axes TEXT,         -- JSON: {x_low, x_high, y_low, y_high}
    principles TEXT,            -- JSON array of 3 principles
    current_step TEXT DEFAULT 'customer',  -- customer, problem, advantages, competitors, differentiation, principles, manifesto, approaches, lenses, hypothesis, scorecard, complete
    status TEXT DEFAULT 'in_progress' CHECK(status IN ('in_progress', 'complete')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE approaches (
    id INTEGER PRIMARY KEY,
    foundation_id INTEGER REFERENCES foundation_sprints(id),
    title TEXT NOT NULL,
    summary TEXT,
    how_it_works TEXT,
    is_top_bet BOOLEAN DEFAULT FALSE,
    is_backup BOOLEAN DEFAULT FALSE
);

CREATE TABLE magic_lenses (
    id INTEGER PRIMARY KEY,
    foundation_id INTEGER REFERENCES foundation_sprints(id),
    lens_name TEXT NOT NULL,
    x_axis_low TEXT,
    x_axis_high TEXT,
    y_axis_low TEXT,
    y_axis_high TEXT,
    evaluations TEXT            -- JSON: [{approach_id, x_position, y_position}]
);

CREATE TABLE hypotheses (
    id INTEGER PRIMARY KEY,
    foundation_id INTEGER REFERENCES foundation_sprints(id),
    customer TEXT NOT NULL,
    problem TEXT NOT NULL,
    approach TEXT NOT NULL,
    competitors TEXT NOT NULL,
    differentiation TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scorecard_entries (
    id INTEGER PRIMARY KEY,
    hypothesis_id INTEGER REFERENCES hypotheses(id),
    right_customer TEXT CHECK(right_customer IN ('yes', 'maybe', 'not_yet', 'no')),
    right_problem TEXT CHECK(right_problem IN ('yes', 'maybe', 'not_yet', 'no')),
    right_approach TEXT CHECK(right_approach IN ('yes', 'maybe', 'not_yet', 'no')),
    will_they_switch TEXT CHECK(will_they_switch IN ('yes', 'maybe', 'not_yet', 'no')),
    right_differentiation TEXT CHECK(right_differentiation IN ('yes', 'maybe', 'not_yet', 'no')),
    does_it_click TEXT CHECK(does_it_click IN ('yes', 'maybe', 'not_yet', 'no')),
    notes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE design_sprints (
    id INTEGER PRIMARY KEY,
    hypothesis_id INTEGER REFERENCES hypotheses(id),
    risk_question TEXT,
    day_map TEXT,
    day_sketch TEXT,
    day_decide TEXT,
    day_prototype TEXT,
    day_test TEXT,
    customer_reactions TEXT,    -- JSON
    outcome TEXT,
    hypothesis_changed BOOLEAN DEFAULT FALSE,
    status TEXT DEFAULT 'planned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE learnings (
    id INTEGER PRIMARY KEY,
    source_type TEXT NOT NULL CHECK(source_type IN ('foundation_sprint', 'design_sprint', 'pivot')),
    source_id INTEGER,
    insight TEXT NOT NULL,
    lesson_number INTEGER CHECK(lesson_number BETWEEN 1 AND 10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pivots (
    id INTEGER PRIMARY KEY,
    old_hypothesis_id INTEGER REFERENCES hypotheses(id),
    new_hypothesis_id INTEGER REFERENCES hypotheses(id),
    reason TEXT,
    what_changed TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Session Management

The Foundation Sprint and Design Sprint dialogues are long, multi-step conversations. Session management works as follows:

**State persistence**: All artifacts are saved to SQLite as they are produced. The `foundation_sprints.current_step` column tracks which step the user is on (customer → problem → advantages → competitors → differentiation → principles → manifesto → approaches → lenses → hypothesis → scorecard → complete). Each step is saved independently via its tool, so no conversational state is lost if the session ends.

**Resumption**: When the user runs `click foundation` with an in-progress sprint, the agent calls `get_project_context` which loads the partial Foundation Sprint. The agent sees which steps have data and which `current_step` is set, and resumes from that point. It briefly summarizes what was decided so far before continuing.

**Design Sprints**: Similarly, `design_sprints.status` tracks state. The individual day columns (`day_map`, `day_sketch`, etc.) are nullable — the agent resumes from the first null day.

**No conversational memory required**: The agent does not need to persist its conversation history between sessions. All decisions are stored as structured data in SQLite. The system prompt + loaded context is sufficient to resume coherently.

### JSON Validation

Several columns store JSON data (`alternatives`, `diff_2x2_axes`, `principles`, `evaluations`, `customer_reactions`). All JSON fields are validated using Pydantic models before writing to SQLite. The models are defined in the implementation and serve as the contract between tools and the database. If validation fails, the tool returns an error to the agent, which can retry with corrected data.

### Output & Document Generation

**After Foundation Sprint:**
- `foundation-sprint.md` — Full summary with Basics, Differentiation 2x2, Mini Manifesto, approaches, Magic Lenses results
- `founding-hypothesis.md` — The Mad Libs card + Scorecard with initial status
- `approaches/` — One file per approach with title, summary, how it works

**After each Design Sprint:**
- `sprints/sprint-{n}.md` — Risk question, daily activities, customer reactions, outcome, scorecard update, hypothesis changes

**Living documents (regenerated on update):**
- `scorecard.md` — Current state of all 6 questions with evidence trail
- `learnings.md` — Accumulated insights organized by the 10 Click lessons
- `pivot-history.md` — Timeline of hypothesis revisions with reasons

All files saved to `click-output/` directory (configurable via `click init`).

## Technology Stack

- **Language**: Python
- **Agent Framework**: Claude Agent SDK
- **Model**: Claude (latest)
- **Database**: SQLite
- **CLI Framework**: Typer (avoids name collision with the project name "Click")
- **Output**: Markdown files + terminal output

## Learning System

The agent evolves through:

1. **Learnings table** — Records insights from every Foundation Sprint, Design Sprint, and pivot, tagged with which of the 10 lessons applies
2. **Pivots table** — Tracks when and why hypotheses change, building a pattern library
3. **Context loading** — Before every new sprint, the agent queries learnings and pivot history to inform coaching. It can say things like "Last time you assumed X about your customer and it turned out to be wrong — let's stress-test that assumption."
4. **Meta-patterns** — Over time, the agent can surface recurring themes: "You've pivoted on differentiation in 3 of your last 4 sprints — your initial differentiators tend to be too abstract. Try being more concrete."

## Target Users

Solo founders and small teams building products. The agent acts as a product coach that guides them through the Click methodology, challenges their assumptions, and helps them build evidence-based conviction before committing to build.
