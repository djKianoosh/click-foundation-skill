# Click Foundation Sprint — Skill

A portable AI skill that guides founders through the Click Foundation Sprint to produce a Founding Hypothesis.

Works as both a Claude Code slash command and a Gemini Gem.

## Claude Code Installation

Copy the skill into your Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills/click-foundation
cp SKILL.md ~/.claude/skills/click-foundation/SKILL.md
```

Then invoke with `/click-foundation` in any Claude Code conversation.

## Gemini Gem Installation

1. Open [gemini.google.com](https://gemini.google.com)
2. Click your profile → Gems → New Gem
3. Name it "Click Foundation Sprint"
4. Paste the entire contents of `SKILL.md` into the Instructions field
5. Save

Then start a conversation with the Gem. When it asks you to paste state, copy from your `.click/state.json` file.

## Usage

Once installed, start a conversation and the skill will:
1. Check for existing `.click/state.json` to resume, or start fresh
2. Walk you through Basics → Differentiation → Approach → Founding Hypothesis
3. Save progress after each decision so you can stop and resume anytime

The final output is `.click/hypothesis.md` — a standalone document with your Founding Hypothesis and initial Scorecard.

## Resetting

To start over, delete the `.click/` directory:

```bash
rm -rf .click/
```
