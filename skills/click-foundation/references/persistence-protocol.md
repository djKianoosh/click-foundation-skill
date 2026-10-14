# Click Persistence Protocol

This reference outlines the state persistence mechanism used by Click Coach across different agent environments.

---

## 1. Storage Tiers

### Tier A: Agentic / CLI Environments (Antigravity, Claude Code)
When running inside an environment with shell execution:
- State is managed deterministically via `python3 skills/click-foundation/scripts/click_coach.py` (or `python3 scripts/click_coach.py`).
- Storage is managed in an embedded SQLite database at `.click/click.db`.
- Documentation is generated via `export-docs` into `click-output/` (or `.click/`).
- Advantage: Zero chance of schema drift, syntax corruption, or missing keys.

### Tier B: Web Chat Environments (Gemini Gems)
When tool/filesystem execution is unavailable:
- The coach outputs state as fenced JSON blocks after each decision.
- The user is instructed: *"Save this to `.click/<filename>` in your project directory."*
- Resumption occurs when the user pastes their `.click/state.json` into the chat.

---

## 2. CLI State Commands Reference

| Operation | Command |
| :--- | :--- |
| **Initialize project** | `python3 scripts/click_coach.py init --name "<Project>"` |
| **Check status / resume** | `python3 scripts/click_coach.py status` |
| **Save Step 1 (Basics)** | `python3 scripts/click_coach.py foundation save-basics --customer "<c>" --problem "<p>" --capability "<cap>" --insight "<i>" --motivation "<m>" --gorilla "<g>" --alternatives "alt1,alt2"` |
| **Save Step 2 (Differentiation)** | `python3 scripts/click_coach.py foundation save-differentiation --diff1 "<d1>" --diff2 "<d2>" --axes-x-low "<xl>" --axes-x-high "<xh>" --axes-y-low "<yl>" --axes-y-high "<yh>" --principles "p1,p2,p3"` |
| **Save Step 3 (Approach)** | `python3 scripts/click_coach.py foundation save-approach --title "<t>" --summary "<s>" --how-it-works "<h>" [--top-bet]` |
| **Save Step 4 (Hypothesis)** | `python3 scripts/click_coach.py foundation save-hypothesis --customer "<c>" --problem "<p>" --approach "<a>" --competitors "<comp>" --differentiation "<diff>"` |
| **Save Step 4b (Scorecard)** | `python3 scripts/click_coach.py scorecard update --right-customer yes --right-problem yes --right-approach maybe --will-they-switch maybe --right-differentiation yes --does-it-click not_yet --notes "<evidence>"` |
| **Export Documentation** | `python3 scripts/click_coach.py export-docs` |

---

## 3. JSON Schemas (Gemini Fallback)

### `.click/state.json`
```json
{
  "project_name": "Acme",
  "current_step": "basics",
  "current_sub_step": "customer",
  "started_at": "2026-10-13T12:00:00Z",
  "last_updated": "2026-10-13T12:30:00Z"
}
```

### `.click/basics.json`
```json
{
  "customer": "Solo technical founders building B2B SaaS",
  "problem": "Struggle to define clear differentiation against incumbents",
  "capability": "Deep engineering background and product intuition",
  "insight": "Founders build features instead of validating positioning",
  "motivation": "Help founders build things customers actually choose",
  "gorilla": "Y Combinator library / generic accelerators",
  "alternatives": ["Spreadsheets", "Ad-hoc customer calls", "Trial-and-error marketing"]
}
```

### `.click/differentiation.json`
```json
{
  "differentiator_1": "Guided conversational AI coach",
  "differentiator_2": "Evidence-based validation scorecard",
  "axes": {
    "x_low": "Passive advice",
    "x_high": "Interactive coach",
    "y_low": "Lofty theory",
    "y_high": "Practical principles"
  },
  "principles": [
    "Differentiate with step-by-step coaching",
    "Reinforce differentiation with continuous scorecard updates",
    "Safeguard: Never decide for the founder"
  ]
}
```

### `.click/scorecard.json`
```json
{
  "right_customer": "yes",
  "right_problem": "yes",
  "right_approach": "maybe",
  "will_they_switch": "maybe",
  "right_differentiation": "yes",
  "does_it_click": "not_yet",
  "notes": "Founder interviews scheduled for this Friday."
}
```
