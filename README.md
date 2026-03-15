# Click Coach

AI product coach that guides founders through the [Click methodology](https://theclickbook.com) by Jake Knapp and John Zeratsky.

## What It Does

Click Coach is a CLI agent that walks you through two structured processes:

1. **Foundation Sprint** — A guided dialogue to define your product strategy and produce a Founding Hypothesis
2. **Design Sprints** — Rapid test-and-learn loops to validate your hypothesis with real customers

The agent challenges your assumptions, enforces plain language, and tracks everything in a local database so you can pick up where you left off.

## The Founding Hypothesis

The core output of a Foundation Sprint is a single testable statement:

> If we help **[customer]** solve **[problem]** with **[approach]**, they will choose it over **[competitors]** because our solution is **[differentiation]**.

Every Design Sprint tests a piece of this hypothesis against real customer reactions.

## Install

```bash
pip install -e ".[dev]"
```

Requires Python 3.11+.

## Setup

Interactive commands (`foundation`, `sprint`, `hypothesis update`, `scorecard update`) require an Anthropic API key:

```bash
export ANTHROPIC_API_KEY='your-key-here'
```

Get a key at [console.anthropic.com](https://console.anthropic.com/). Read-only commands (`foundation show`, `sprint list`, `hypothesis`, `scorecard`, `learnings`) work without a key — they only query the local database.

## Quick Start

```bash
# Initialize in your project directory
click-coach init

# Run a Foundation Sprint (interactive dialogue — requires API key)
click-coach foundation

# After completing the Foundation Sprint, run Design Sprints
click-coach sprint
```

## Commands

| Command | Description |
|---------|-------------|
| `click-coach init` | Initialize Click in the current directory |
| `click-coach foundation` | Start or resume a Foundation Sprint |
| `click-coach foundation show` | Show current Foundation Sprint results |
| `click-coach foundation list` | List all Foundation Sprints |
| `click-coach sprint` | Start a Design Sprint |
| `click-coach sprint show <id>` | Show a Design Sprint's details |
| `click-coach sprint list` | List Design Sprints for current hypothesis |
| `click-coach hypothesis` | Show current Founding Hypothesis + Scorecard |
| `click-coach hypothesis update` | Revise hypothesis based on learnings |
| `click-coach scorecard` | Show current scorecard status |
| `click-coach scorecard update` | Update scorecard with new evidence |
| `click-coach learnings` | Show accumulated learnings |

## Foundation Sprint Flow

The agent guides you through the Click methodology step by step:

**Day 1 — Basics + Differentiation**
- Define your **customer** (plain language, not jargon)
- Define the **problem** they have (common sense test: "does this make sense?")
- Identify your **advantages** (capability, insight, motivation)
- Map the **competition** (800-pound gorilla, alternatives, substitutes)
- Create a **differentiation** 2x2 chart and pick 2 differentiators
- Write 3 **practical principles** (differentiate, differentiate, safeguard)

**Day 2 — Approach**
- Generate 3+ **approach options** (including non-obvious ones)
- Evaluate through **Magic Lenses** (customer, pragmatic, growth, money perspectives)
- Choose a **top bet** and backup
- Write the **Founding Hypothesis**
- Set initial **Scorecard** answers

## The Scorecard

After each Design Sprint, the agent updates six questions:

- Right customer?
- Right problem?
- Right approach?
- Will they switch?
- Right differentiation?
- Does it click?

Answers are evidence-based: `yes`, `maybe`, `not_yet`, or `no`.

## How It Works

- All data stored in `.click/click.db` (SQLite)
- Generated documents saved to `click-output/`
- Session state tracked per step — quit and resume anytime
- Learnings accumulate across sprints, informing future coaching

## The 10 Lessons

The agent's coaching behavior encodes these principles from the book:

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

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```
