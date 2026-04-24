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

## Install — As a Skill (Recommended)

The Foundation Sprint is available as a portable AI skill that works in Claude Code and Gemini.

### Claude Code

```bash
mkdir -p ~/.claude/skills/click-foundation
cp skills/click-foundation/SKILL.md ~/.claude/skills/click-foundation/SKILL.md
```

Then run `/click-foundation` in any conversation.

### Gemini Gem

1. Open [gemini.google.com](https://gemini.google.com) → Gems → New Gem
2. Name it "Click Foundation Sprint"
3. Paste the contents of `skills/click-foundation/SKILL.md` into Instructions
4. Save and start a conversation

See `skills/click-foundation/README.md` for details.

## Install — As a CLI (Alternative)

The full CLI includes Foundation Sprints, Design Sprints, and learnings tracking.

```bash
pip install -e ".[dev]"
```

Requires Python 3.11+ and an Anthropic API key:

```bash
export ANTHROPIC_API_KEY='your-key-here'
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

## Demo Walkthrough

Here's what a Foundation Sprint looks like in practice, using a fictional meal-planning app as an example.

### Step 1 — Basics

The coach asks about your customer, problem, advantages, and competition — one at a time, in plain language.

```
Coach: Who is your customer? Describe them in plain language — no jargon,
       no personas. Just who they are and what their life looks like.

You:   Busy parents who cook dinner most weeknights but run out of ideas
       and end up ordering takeout more than they want to.

Coach: Common sense check — does "busy parents who cook most weeknights"
       make sense to someone outside your industry? Yes, that's clear.
       What real problem do they have?

You:   They waste 20+ minutes every evening figuring out what to cook,
       then realize they're missing ingredients.

Coach: That's a real problem, not a feature wish. Good.
```

### Step 2 — Differentiation

You plot your product against competitors on scales, then build a 2x2 chart to find where you win.

```
                    Personalized
                         |
                    [You] |
                         |
     Simple ─────────────┼──────────────── Complex
                         |
                         | [Competitor A]
               [Do Nothing]
                         |
                      Generic
```

From the chart, you pick 2 differentiators and write 3 practical principles:

```
Differentiators:
  1. Personalized to your family's actual preferences
  2. Simple — 5 ingredients or fewer, always

Principles:
  1. Differentiate: Recommend meals based on what this family actually eats
  2. Differentiate: Never suggest a recipe with more than 5 ingredients
  3. Safeguard: Never require the user to manually enter preferences
```

### Step 3 — Approach

You brainstorm 3+ approaches, evaluate each through Magic Lenses (customer, pragmatic, growth, money — each a 2x2 chart), and pick a top bet.

```
Magic Lens: Customer

              High want
                 |
           [App] | [Chatbot]
                 |
  Low effort ────┼──────── High effort
                 |
                 | [Meal kit]
                 |
              Low want
```

Patterns across lenses reveal which approach wins consistently.

### Step 4 — Founding Hypothesis

Everything rolls up into one testable statement:

> If we help **busy parents** solve **nightly meal-planning paralysis** with **a 5-ingredient recipe app that learns their preferences**, they will choose it over **generic recipe sites and meal kits** because our solution is **personalized and radically simple**.

Plus an initial scorecard:

| Question | Answer | Evidence |
|----------|--------|----------|
| Right customer? | yes | We are these people |
| Right problem? | yes | We experience this daily |
| Right approach? | maybe | Need to test if 5-ingredient constraint works |
| Will they switch? | not_yet | Haven't tested with real users |
| Right differentiation? | yes | Nothing else combines personalization + simplicity |
| Does it click? | not_yet | Hypothesis needs validation through Design Sprints |

All progress is saved to `.click/` — stop anytime and pick up where you left off.

## How It Works

- Session state saved to `.click/` directory as JSON files
- Resume from any step across conversations
- Final deliverable: `.click/hypothesis.md`
- Works in Claude Code (file I/O) and Gemini (paste-based fallback)

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
