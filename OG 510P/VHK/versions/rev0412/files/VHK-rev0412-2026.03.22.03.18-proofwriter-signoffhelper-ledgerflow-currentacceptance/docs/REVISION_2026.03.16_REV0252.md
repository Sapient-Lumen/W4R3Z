# Revision note: rev0252 (2026-03-16)

## What changed

### 1) Planner now aggregates route ownership into a route portfolio

VHK already knew which Linux-native lane should own each macro, but reviewers
still had to scan the whole macro list to answer a product-level question:

> which lanes are actually dominating this project?

This revision adds `route_portfolio` to `vhk plan-project --json`.

Each row groups `macro_route_profiles` by `route_id` and surfaces:

- macro count
- dominant fit
- fit distribution
- top activation routes
- top execution surfaces
- example macros

### 2) Planner now emits a project-level export promotion plan

Per-macro export hints were useful, but they still left maintainers to manually
assemble the next Linux-native shipping work.

This revision adds `export_promotion_plan` to `vhk plan-project --json`.

Each row groups promotion candidates by export surface and surfaces:

- priority
- macro count
- route ids feeding the promotion
- tool families
- commands
- activation routes
- reasons / evidence / risks

The point is to turn repeated macro advice into project-level staged work: text
package, remapper export, watcher service, helper dossier, and so on.

### 3) Human-readable planner output now shows both aggregates

`vhk plan-project` now prints:

- a “Route portfolio” table
- an “Export promotion plan” table

So the route/export story is visible even when reviewing the planner in the
terminal instead of consuming the JSON.

### 4) Docs/specs updated

Updated docs now make the new planner contracts explicit:

- `README.md`
- `docs/SPECS.md`
- `docs/ISSUES_2026Q1.md`

## Test runs completed

Targeted tests executed successfully:

```bash
pytest -q tests/test_plan_project_cli.py tests/test_lint_project_cli.py
pytest -q tests/test_activation_pack_cli.py tests/test_route_selection_pack_cli.py tests/test_target_route_pack_cli.py tests/test_optimize_cli.py tests/test_validate_cli.py
```

Notes:

- this revision stayed planner/docs oriented rather than adding a new desktop backend
- no live compositor/session integration testing was possible inside this build environment
