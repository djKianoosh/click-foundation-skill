# Click Coach

AI product coach that guides founders through the [Click methodology](https://theclickbook.com) by Jake Knapp and John Zeratsky.

---

## What It Does

Click Coach is an agentic AI skill and command-line companion that guides founders through structured strategic processes:

1. **Foundation Sprint** — A guided dialogue to define your product strategy, test your assumptions in plain language, plot a 2x2 competitive positioning matrix, and formulate a testable **Founding Hypothesis** and initial **Scorecard**.
2. **Design Sprints** — Structured test-and-learn loops to validate your hypothesis with real customers before writing production code.

The agent challenges your assumptions, enforces plain language, and tracks state deterministically in `.click/` so you can pause and resume at any point.

---

## The Founding Hypothesis

The primary deliverable of a Foundation Sprint is a single testable statement:

> If we help **[customer]** solve **[problem]** with **[approach]**, they will choose it over **[competitors]** because our solution is **[differentiation]**.

Every Design Sprint tests a specific piece of this hypothesis against real customer reactions.

---

## Using Click Coach

### 1. As an Antigravity Skill (Recommended)
This repo includes a workspace discovery symlink at `.agents/skills/click-foundation`. Antigravity automatically discovers and activates the skill when you open this project.

Simply ask:
> *"Run a Click Foundation Sprint for my startup idea"* or *"Help me define our customer and problem in plain language."*

### 2. In Claude Code
Install into your Claude Code skills:
```bash
mkdir -p ~/.claude/skills/click-foundation
cp -r skills/click-foundation/* ~/.claude/skills/click-foundation/
```
Then invoke `/click-foundation` in any conversation.

### 3. In Gemini Gems
1. Open [gemini.google.com](https://gemini.google.com) → Gems → New Gem.
2. Name it **"Click Foundation Sprint"**.
3. Paste the contents of `skills/click-foundation/SKILL.md` into the Instructions field.
4. Save and begin chatting. Use the JSON paste fallback described in `skills/click-foundation/references/persistence-protocol.md`.

---

## CLI Automation (`click_coach.py`)

The skill bundles a zero-dependency CLI script located at `skills/click-foundation/scripts/click_coach.py`. Both agents and founders can run commands directly:

```bash
# Initialize a project
python3 skills/click-foundation/scripts/click_coach.py init --name "My Startup"

# View current sprint status
python3 skills/click-foundation/scripts/click_coach.py status

# Inspect the current hypothesis and scorecard
python3 skills/click-foundation/scripts/click_coach.py hypothesis show
python3 skills/click-foundation/scripts/click_coach.py scorecard show

# Show accumulated learnings
python3 skills/click-foundation/scripts/click_coach.py learnings show

# Export markdown deliverables (founding-hypothesis.md, scorecard.md, etc.)
python3 skills/click-foundation/scripts/click_coach.py export-docs
```

Or install the package to put `click-coach` on your PATH:
```bash
pip install -e .
click-coach --help
```

---

## Directory Architecture

```text
.
├── .agents/skills/click-foundation    # Antigravity workspace discovery symlink
├── skills/click-foundation/           # Canonical agent skill package
│   ├── SKILL.md                       # Main agent prompt, coaching rules & step-by-step flow
│   ├── README.md                      # Skill-specific setup guide
│   ├── scripts/                       # Deterministic automation scripts
│   │   ├── click_coach.py             # CLI entry point
│   │   ├── db.py                      # SQLite database schema and connection handlers
│   │   ├── models.py                  # Pydantic & dataclass validation models
│   │   ├── tools.py                   # Core business logic for sprints & scorecard
│   │   └── docs_generator.py          # Markdown document generator
│   ├── references/                    # On-demand reference documentation
│   │   ├── persistence-protocol.md    # Database schemas & JSON fallback specs
│   │   └── coaching-guide.md          # Note-and-Vote guide & 2x2 matrix formatting
│   ├── assets/                        # Templates and JSON schemas
│   │   ├── hypothesis-template.md     # Output markdown skeleton
│   │   └── schemas/                   # JSON schemas for state files
│   └── evals/                         # Automated evaluation suites
│       ├── trigger_queries.json       # 20 trigger queries (train/val split)
│       └── evals.json                 # Benchmark scenarios with objective assertions
├── tests/                             # Comprehensive test suite (pytest)
└── pyproject.toml                     # Package definition & ruff config
```

---

## Development & Verification

Run tests and linting:

```bash
# Run the test suite
pytest

# Check code with Ruff
ruff check .

# Check formatting with Ruff
ruff format --check .

# Validate the skill against Open Skills specifications
python3 ~/.gemini/config/skills/skill-architect/scripts/validate_skill.py skills/click-foundation
```
