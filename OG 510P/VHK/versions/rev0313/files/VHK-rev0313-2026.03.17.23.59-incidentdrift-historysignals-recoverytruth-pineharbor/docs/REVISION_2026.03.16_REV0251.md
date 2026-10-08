# VHK rev0251 — route drift + export surface candidates

This revision pushes the macro-route work from rev0250 one step further:

- `plan-project --json` now emits `macro_export_candidates` alongside `macro_route_profiles`.
- `plan-project` human output now includes a **Macro export candidates** table.
- `lint-project` now emits advisory `ROUTE_DRIFT_*` findings when a macro obviously fits:
  - a remapper tier
  - a text/package tier
  - a watcher/service tier
  - a helper-boundary lane
- targeted tests now cover both the planner JSON surface and route-drift lint output.

## Why this matters

Linux-native automation is not one runtime with one backend. The product shape is a composition of lanes:

- text/package lane
- remapper lane
- watcher/service lane
- launcher lane
- full runner lane
- helper-boundary lane for volatile Wayland edges

This pass makes those lanes more actionable inside the repo so architecture lessons stop living only in docs.
