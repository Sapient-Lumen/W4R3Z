# REV0294 — promotion operator controls

This revision adds `promotion_operator_control_plan` to planner output and threads it through promotion/capability/operator docs.

## What changed

- Added `promotion_operator_control_plan` to `vhk plan-project --json`.
- Added a new plan-project CLI table: **Promotion operator controls**.
- Promotion pack now carries operator-control summaries and a **Promotion operator controls** section.
- Capability-audit docs now render the same operator-control view so status/reload/log ownership is visible next to shipping lanes and startup routes.
- Operator guide now includes promotion operator controls.

## Why

Linux-native automation does not end at choosing an input lane or startup route. Operators still need to know which service/session/daemon/manual loop owns status, reload, logs, and day-2 recovery.
