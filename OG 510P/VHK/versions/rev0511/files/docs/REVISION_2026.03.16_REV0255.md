# VHK revision 0255 — promotion gates, claim discipline, and staged honesty

This revision extends the recent route/promotion work with one more operational
layer: **promotion gates**.

## What changed

- `vhk plan-project --json` now emits:
  - `promotion_gates`
  - `promotion_gate_summary`
- human-readable `vhk plan-project` now prints a **Promotion gates** table
- `vhk lint-project` now emits project-level promotion-gate issues:
  - `PROMOTION_GATE_REVIEW`
  - `PROMOTION_GATE_FAIL`
- `vhk gen-promotion-pack` now carries gate information into:
  - `docs/VHK_PROMOTION_PLAN.md`
  - `docs/VHK_PROMOTION_FIXUPS.md`
  - `docs/VHK_PROMOTION_PLAN.json`

## Why this matters

Earlier revisions taught VHK to answer:

- which lane each macro belongs to
- which export surfaces the project wants
- which surfaces look ready/review/blocked

This revision adds the next practical question:

- **what Linux-native claims are safe to make right now?**

That is the difference between an interesting planner and a release-honest one.

## Gate model in this revision

The planner now derives small, explainable gates from staged promotion work:

- **Specialist surface gate** — are text/remapper/service lanes actually ready
  enough to promote first?
- **Helper-boundary gate** — are capture/injection-sensitive surfaces being kept
  as explicit host/session contracts instead of vague parity claims?
- **Promotion sequencing gate** — are later/auxiliary surfaces outrunning the
  stronger specialist lanes?
- **Claim discipline gate** — does the current readiness story justify broad
  Linux-native language, or does it still need tighter target/session wording?

## Tests run

- `python -m compileall -q src/vhk`
- `pytest -q tests/test_plan_project_cli.py tests/test_promotion_pack_cli.py tests/test_lint_project_cli.py tests/test_activation_pack_cli.py tests/test_route_selection_pack_cli.py tests/test_target_route_pack_cli.py tests/test_validate_cli.py`

All of those targeted suites passed in this revision.
