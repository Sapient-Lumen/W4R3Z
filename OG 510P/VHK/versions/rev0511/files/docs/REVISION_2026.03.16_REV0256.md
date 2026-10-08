# VHK revision 0256 — promotion backlog and executable lane queues

This revision turns the recent promotion/readiness/gate work into something
closer to an execution queue.

## What changed

- `vhk plan-project --json` now emits:
  - `promotion_backlog`
  - `promotion_backlog_summary`
- human-readable `vhk plan-project` now prints a **Promotion backlog** table
- `vhk gen-promotion-pack` now also writes:
  - `docs/VHK_PROMOTION_BACKLOG.md`
- `docs/VHK_PROMOTION_PLAN.md` and `docs/VHK_PROMOTION_FIXUPS.md` now include
  backlog-aware sections instead of stopping at waves/readiness/gates

## Why this matters

Earlier revisions taught VHK to answer:

- which lane each macro belongs to
- which project-level export surfaces should exist
- which surfaces are ready/review/blocked
- which gates make release language honest

This revision adds the next practical question:

- **what should the team do next, in order?**

That means turning Linux-native promotion strategy into a queue of:

- promote-now tasks
- review-before-claiming tasks
- unblock-before-shipping tasks
- gate/claim-discipline tasks

## Backlog model in this revision

The new backlog is intentionally simple and explainable. It derives tasks from
existing planner surfaces instead of inventing a second hidden planning system.
Each task now carries:

- task id
- queue state (`todo`, `review`, `blocked`)
- task kind (`promote`, `review`, `unblock`, `gate`)
- associated wave/surface/gate
- next action, blockers, review notes, and suggested commands

## Tests run

- `python -m compileall -q src/vhk`
- `pytest -q tests/test_plan_project_cli.py tests/test_promotion_pack_cli.py tests/test_lint_project_cli.py tests/test_route_selection_pack_cli.py tests/test_design_pack_cli.py tests/test_validate_cli.py`

All of those targeted suites passed in this revision.
