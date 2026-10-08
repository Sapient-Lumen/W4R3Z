# REV0295 — promotion recovery lanes

This revision adds `promotion_recovery_plan` to planner output and threads it through promotion/operator/capability-audit docs.

- Added `promotion_recovery_plan` to `vhk plan-project --json`.
- Added a new plan-project CLI table: **Promotion recovery lanes**.
- `gen-promotion-pack` now carries recovery summaries and a **Promotion recovery lanes** section in `VHK_PROMOTION_PLAN.md`.
- `gen-capability-audit-pack` now renders the same recovery-lane view.
- `gen-operator-pack` now includes a **Promotion recovery lanes** section.
- Updated README/spec/plan/issues docs and added a research note on Linux recovery lanes.
