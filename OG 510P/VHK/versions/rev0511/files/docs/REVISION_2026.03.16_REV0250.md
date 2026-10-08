# Revision note: rev0250 (2026-03-16)

## What changed

### 1) Macro route ownership is now explicit in the planner

VHK already had project-wide stack profiles, runtime seams, and activation
routes, but it still left one practical design question too implicit:

> which Linux-native lane should own each macro?

This revision adds `macro_route_profiles` to `vhk plan-project --json`.

Each macro can now surface as one of the following route shapes:

- `text-tier`
- `remapper-tier`
- `watcher-service`
- `launcher-entry`
- `helper-boundary-runner`
- `runner-core`

Each profile includes:

- route title / fit / owner layer
- execution surface
- chosen activation route
- evidence / risks / capability usage
- Linux tools VHK should learn from
- concrete follow-up commands

### 2) Planner TUI now shows macro route ownership

The human-readable `vhk plan-project` output now includes a “Macro route
ownership” table so route choices are visible without requiring JSON review.

### 3) Docs/specs/issues updated around route ownership

Updated docs now make the route-ownership contract explicit:

- `docs/SPECS.md`
- `docs/ISSUES_2026Q1.md`
- `docs/RESEARCH_2026.03.16_MACRO_ROUTE_OWNERSHIP_AND_LINUX_TOOL_LESSONS.md`

## Test runs completed

Targeted tests executed successfully:

```bash
pytest -q tests/test_plan_project_cli.py
```

Notes:

- this revision focused on planner behavior and docs rather than a new runtime backend
- no live compositor/session integration testing was possible inside this build
  environment, so route-ownership conclusions remain planner-side and docs-side
  rather than claiming live desktop verification
