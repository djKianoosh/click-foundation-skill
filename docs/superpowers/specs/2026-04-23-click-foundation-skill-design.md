# Click Foundation Skill — Design Spec

## Overview

Convert the Click Coach Foundation Sprint from a standalone Agent SDK CLI app into a portable prompt-based skill that works as both a Claude Code slash command and a Gemini Gem custom instruction.

The skill guides founders through the Foundation Sprint of the Click methodology (Jake Knapp & John Zeratsky), producing a Founding Hypothesis. State is persisted to files so users can pause and resume across sessions.

## Goals

- Single markdown source that deploys to both Claude Code and Gemini
- Full Foundation Sprint methodology (no Design Sprints in this scope)
- File-based persistence with pause/resume across sessions
- Distributable to other founders

## Non-Goals

- Design Sprint support (future work)
- SQLite or any database dependency
- Custom tool implementations — the skill relies on the host AI's native file I/O
- Real-time collaboration or multi-user support

## Skill Structure & Invocation

### Claude Code

Installed as a skill markdown file. Invoked via `/click-foundation`. Uses Claude Code's native Read/Write tools to manage state files in the project directory.

### Gemini Gem

The same markdown content is pasted into a Gem's custom instruction field. Since Gemini Gems cannot write files directly, the skill includes a fallback: the AI outputs structured state blocks as fenced code, labeled with filenames, for the user to save manually. On resume, the user pastes `state.json` content so the AI knows where they left off.

### Environment Detection

The prompt instructs the AI to attempt reading `.click/state.json` on invocation. If file operations work, use direct file I/O. If not, fall back to the paste-based persistence model.

## Foundation Sprint Flow

The skill walks the user through four major steps, advancing one sub-step at a time. State is saved after each decision.

### Step 1 — Basics

- **Customer:** Who are they? Plain language, no jargon. Common sense test: "Does this make sense to someone outside your industry?"
- **Problem:** What real problem do they have? Not a feature wish. Common sense test applied.
- **Advantages:** Three types — Capability (what you can do), Insight (what you understand), Motivation (why you care).
- **Competition:** The 800-pound gorilla, direct alternatives, substitutes. "Do nothing" always counts as a competitor.

### Step 2 — Differentiation

- Score the product on classic differentiation scales.
- Create a 2x2 chart with custom axes.
- Pick 2 key differentiators.
- Define 3 practical principles: differentiate, differentiate, safeguard. These are concrete and actionable, not lofty ideals.
- Combine into a Mini Manifesto (2x2 chart + principles).

### Step 3 — Approach

- Brainstorm 3+ approach options using the Note-and-Vote pattern:
  1. User brainstorms multiple options
  2. AI suggests additional options they haven't considered
  3. AI challenges with plain language and common sense tests
  4. User picks top 2-3
  5. User (as Decider) makes the final choice
- Write one-page summaries for each approach (title, one-sentence summary, description).
- Evaluate through Magic Lenses: customer, pragmatic, growth, money, and optionally custom lenses. Each lens is a 2x2 chart. Look for patterns across lenses.
- Decider picks top bet + backup.

### Step 4 — Founding Hypothesis & Scorecard

- Fill in the Mad Libs formula: "If we help [customer] solve [problem] with [approach], they will choose it over [competitors] because our solution is [differentiation]."
- Set initial scorecard answers for 6 questions:
  1. Right customer?
  2. Right problem?
  3. Right approach?
  4. Will they switch?
  5. Right differentiation?
  6. Does it click?
- Each answer is: yes, maybe, not_yet, or no.
- Output the hypothesis as a standalone markdown file.

### Coaching Behaviors (Embedded Throughout)

- Challenge assumptions: "How do you know that's true?"
- Enforce plain language: Replace jargon with simple words
- Common sense test: "Does this make sense?"
- Encourage alternatives: "What if this approach fails? What else could work?"
- Be direct and concise — founders are busy
- One question at a time — never overwhelm

## File-Based Persistence

All state lives in a `.click/` directory in the project root.

### File Layout

| File | Format | Purpose |
|------|--------|---------|
| `.click/state.json` | JSON | Current step, sub-step, session metadata, timestamps |
| `.click/basics.json` | JSON | Customer, problem, advantages (capability/insight/motivation), competition (gorilla/alternatives) |
| `.click/differentiation.json` | JSON | 2x2 axes, differentiator_1, differentiator_2, principles (array of 3), manifesto summary |
| `.click/approaches.json` | JSON | Array of objects: title, summary, how_it_works, is_top_bet, is_backup |
| `.click/lenses.json` | JSON | Array of lens objects: lens_name, x/y axes, evaluations per approach |
| `.click/hypothesis.md` | Markdown | The Founding Hypothesis — human-readable deliverable |
| `.click/scorecard.json` | JSON | 6 questions with answer (yes/maybe/not_yet/no) and evidence string |

### State Schema

```json
{
  "current_step": "basics | differentiation | approach | hypothesis | scorecard | complete",
  "current_sub_step": "customer | problem | advantages | competitors | scales | chart | differentiators | principles | manifesto | brainstorm | summaries | lenses | decide | mad_libs | scorecard_init",
  "started_at": "ISO-8601 timestamp",
  "last_updated": "ISO-8601 timestamp",
  "project_name": "string"
}
```

### Persistence Rules

- On invocation, read `state.json`. If it exists, resume. If not, create `.click/` and start fresh.
- After each user decision, write the relevant data file and update `state.json`.
- Files are granular (one per step) for readability, diffing, and partial recovery.
- `hypothesis.md` is the final deliverable.

### Gemini Fallback

When file I/O is unavailable:
- After each decision, output the state file content as a fenced code block labeled with the filename (e.g., ` ```json basics.json`).
- Instruct the user to save the block to `.click/<filename>`.
- On resume, ask the user to paste the contents of `state.json` (and optionally other files for full context).

## Prompt Architecture

The skill prompt contains four sections, targeting under 4,000 words total.

### Section 1 — Role & Methodology (~500 words)

Who you are (Click Coach), the 10 Lessons, coaching behaviors. Derived from the existing system prompt.

### Section 2 — Flow Instructions (~1,500 words)

Step-by-step Foundation Sprint sequence. Note-and-Vote pattern. Transition rules for advancing between steps. Sub-step definitions.

### Section 3 — Persistence Protocol (~1,000 words)

File read/write instructions. JSON schemas for each file. Gemini fallback behavior. Resume logic.

### Section 4 — Resume Logic (~500 words)

On invocation: read all `.click/` files, summarize progress, pick up from next incomplete sub-step. Present a brief status to the user before continuing.

### Gemini Character Limit

Gemini Gems have a ~10,000 character instruction limit. If the full prompt exceeds this, split into two Gems:
- **Click Foundation Day 1** — Basics + Differentiation
- **Click Foundation Day 2** — Approach + Hypothesis

The Claude Code skill remains a single file regardless.

## Testing Strategy

- **Manual walkthrough:** Run the skill end-to-end in Claude Code, verifying each state file is written correctly and resume works.
- **Resume test:** Start a session, stop midway, start a new conversation, verify it picks up correctly.
- **Gemini test:** Paste the prompt into a Gemini Gem, run through the flow, verify the paste-based fallback is usable.
- **Edge cases:** Empty inputs, restarting from scratch (deleting `.click/`), re-running a completed sprint.

## Deliverables

1. `click-foundation.md` — The portable skill/prompt file
2. Installation instructions for Claude Code (skill file placement)
3. Installation instructions for Gemini Gem (copy-paste guide)
4. Updated project README reflecting the new skill-based approach
