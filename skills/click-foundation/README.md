# Click Foundation Sprint — Skill

A portable, production-grade AI agent skill that guides founders through the Click Foundation Sprint to formulate a testable Founding Hypothesis and initial Scorecard. Grounded in the Click methodology by Jake Knapp and John Zeratsky.

Works across **Google Antigravity**, **Claude Code**, and **Gemini Gems**.

---

## Installation & Setup

### 1. Antigravity (Recommended)
This repository includes a workspace discovery symlink at `.agents/skills/click-foundation`. If you open this project in Antigravity or Antigravity CLI (`agy`), the skill is automatically discovered and activated.

To install globally across all your Antigravity workspaces:
```bash
mkdir -p ~/.gemini/config/skills/click-foundation
cp -r . ~/.gemini/config/skills/click-foundation/
```

### 2. Claude Code
Copy the skill directory into your Claude Code skills folder:
```bash
mkdir -p ~/.claude/skills/click-foundation
cp -r . ~/.claude/skills/click-foundation/
```
Then invoke with `/click-foundation` in any conversation.

### 3. Gemini Gem
1. Open [gemini.google.com](https://gemini.google.com) → Gems → New Gem
2. Name: "Click Foundation Sprint"
3. Paste the contents of [`SKILL.md`](SKILL.md) into the Instructions field
4. Save and start chatting. Use the JSON paste fallback described in [`references/persistence-protocol.md`](references/persistence-protocol.md).

---

## Bundled CLI Tool (`scripts/click_coach.py`)

The skill bundles a deterministic, zero-dependency Python script to manage state, track scorecard evaluations, and export markdown deliverables. Both agents and founders can run it directly:

```bash
# Initialize a project
python3 scripts/click_coach.py init --name "My Startup"

# View current progress
python3 scripts/click_coach.py status

# Inspect the scorecard
python3 scripts/click_coach.py scorecard show

# Export markdown deliverables (founding-hypothesis.md, scorecard.md, etc.)
python3 scripts/click_coach.py export-docs
```

---

## Directory Structure

```text
skills/click-foundation/
├── SKILL.md                          # Main agent instructions & step-by-step flow
├── README.md                         # Installation & usage guide
├── scripts/                          # Deterministic automation tools
│   ├── click_coach.py                # Standalone CLI entry point
│   ├── db.py                         # SQLite database schema & queries
│   ├── models.py                     # Data validation models (Pydantic / Dataclass)
│   ├── tools.py                      # Core sprint management functions
│   └── docs_generator.py             # Markdown document generator
├── references/                       # On-demand reference documentation
│   ├── persistence-protocol.md       # SQLite schemas, CLI flags & Gemini fallback
│   └── coaching-guide.md             # Note-and-Vote guide & 2x2 matrix formatting
├── assets/                           # Reusable schemas and markdown templates
│   ├── hypothesis-template.md        # Concrete output document template
│   └── schemas/                      # Standard JSON schemas (basics, differentiation, scorecard)
└── evals/                            # Quality benchmarks and trigger evaluations
    ├── trigger_queries.json          # 20 train/validation trigger test queries
    └── evals.json                    # Benchmark test scenarios with objective assertions
```

---

## Resetting State

To reset and start over fresh:
```bash
rm -rf .click/ click-output/
```
