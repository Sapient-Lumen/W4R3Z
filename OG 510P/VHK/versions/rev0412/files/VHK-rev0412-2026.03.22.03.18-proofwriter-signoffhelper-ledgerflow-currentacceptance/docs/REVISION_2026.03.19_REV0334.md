# REV0334 — 2026-03-19

This revision adds a fused stack-state surface to the generated i3/X11 warm-runtime handoff.

Highlights:
- extended `vhk gen-i3-busd-stack` so generated stacks now also include:
  - `bin/stack_state_json.sh`
  - `bin/stack_state.sh`
- `control-plane.json` now records those helpers as part of the preferred operator/private-LLM control surface
- `stack_state_json.sh` combines:
  - manifest/runtime contract data
  - prerequisite blockers and warnings
  - current runtime status/health
  - macro inventory
  - latest-run truth
  - the current recommended next action
- updated `README.md`, `docs/I3_X11_RUNTIME_STACK.md`, and `docs/BUS_DAEMON.md` so the repo story reflects the new fused stack-state surface

Validation run:
- `python -m compileall -q src/vhk tests`
- `pytest -q tests/test_i3_busd_stack_cli.py tests/test_busd_service_cli.py tests/test_busd_socket_units_cli.py tests/test_latest_run_json_cli.py`

Follow-up fixes landed during validation:
- fixed generated `list_macros.sh` and macro-existence checks to call `vhk list-macros PROJECT_DIR` correctly instead of using a nonexistent `--project` flag
- kept the new fused stack-state helper as a single-probe surface by deriving the next action from the already-captured readiness/runtime state instead of recursively re-running `next_action_json.sh`
