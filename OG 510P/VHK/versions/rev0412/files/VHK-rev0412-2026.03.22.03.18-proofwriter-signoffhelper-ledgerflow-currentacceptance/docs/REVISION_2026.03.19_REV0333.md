# Revision 0333 — latest-run artifacts + stack observability

This pass tightened the flagship i3/X11 warm-runtime control plane around **latest-run artifact truth** instead of widening scope.

## What changed

- added `vhk latest-run-json PROJECT_DIR`
  - emits a machine-readable snapshot of the newest run log and its main artifact paths
  - includes the latest run log path, default trace-export path, error screenshots, and visual diff artifacts when present
- extended `vhk gen-i3-busd-stack` so generated stacks now also include:
  - `bin/latest_run_json.sh`
  - `bin/latest_artifacts.sh`
- extended the generated `control-plane.json` contract so latest-run artifact inspection is part of the stable LLM/operator surface
- updated:
  - `README.md`
  - `docs/I3_X11_RUNTIME_STACK.md`
  - `docs/BUS_DAEMON.md`

## Why this matters

The warm-runtime stack already had readiness, status, and next-action surfaces. This revision adds a stable answer to a different but equally common question: **what happened last time, and where are the artifacts?**

That matters for both humans and a private LLM because it avoids reconstructing log paths, trace paths, and failure artifacts from scratch every turn.

## Validation

- `python -m compileall -q src/vhk tests`
- `pytest -q tests/test_i3_busd_stack_cli.py tests/test_busd_service_cli.py tests/test_busd_socket_units_cli.py tests/test_latest_run_json_cli.py`
