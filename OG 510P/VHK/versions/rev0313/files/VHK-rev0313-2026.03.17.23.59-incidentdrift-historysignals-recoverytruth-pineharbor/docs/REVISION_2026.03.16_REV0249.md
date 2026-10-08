# Revision note: rev0249 (2026-03-16)

## What changed

### 1) Typed-text throughput is now explicit in lint/planner output

VHK already had typed/clipboard/hybrid text machinery, but the product surface
was still biased toward vision/polling smells. This revision makes long literal
`TypeText` and structured Tab/Enter-rich `TypeText` visible earlier.

New lint hints:

- `LONG_TYPED_TEXT_LITERAL`
- `STRUCTURED_TYPED_TEXT_LITERAL`

New planner/performance surfacing:

- `text-throughput` / `structured-text` performance tags
- `typed-text-throughput` hotspot
- typed-text counters in per-macro/runtime budgets

### 2) Docs extended around Linux-native product shape

Updated docs now make a stronger distinction between:

- X11 as the best near-term full replay lane
- portal/global-shortcut/helper surfaces as conditional Wayland lanes
- text throughput as a first-class Linux-native performance topic

### 3) Research note added

See:

- `docs/RESEARCH_2026.03.16_LINUX_NATIVE_RUNTIME_PORTALS_AND_THROUGHPUT.md`

## Test runs completed

Targeted tests executed successfully:

```bash
pytest -q tests/test_lint_project_cli.py \
          tests/test_plan_project_cli.py \
          tests/test_optimize_cli.py \
          tests/test_text_input_profiles.py

pytest -q tests/test_global_shortcuts_portal.py \
          tests/test_portal_shortcuts_spec.py \
          tests/test_input_backend_overrides.py

pytest -q tests/test_validate_cli.py
```

Notes:

- the repository contains a much larger overall suite; this revision records the
  targeted passes above rather than claiming a completed full-suite run
- no compositor-specific live integration tests were possible inside this build
  environment, so Wayland/X11 runtime claims here stay grounded in unit/CLI
  coverage plus upstream research, not a live desktop session
