# Revision 0440 — runtime board receipt lanes for the selected macro

Revision 0439 made receipt scope explicit inside receipt evidence, but one practical LLM/operator gap remained: `macro_runtime_board_json.sh` could classify warm-dispatch posture without carrying the selected macro's own receipt lane directly. That forced callers to hop back into the dispatch-history board even when the project-wide execution board had already chosen the macro worth acting on.

This revision makes the runtime board selected-lane aware by mirroring macro-scoped receipt observability on each item and by exposing explicit project-global vs primary-macro receipt surfaces at board scope.

## What changed

- `macro_runtime_board_json.sh` items now carry:
  - `dispatch_attention`
  - `receipt_observability.macro_latest_dispatch`
  - `receipt_observability.project_latest_dispatch`
  - `preferred_entrypoints.latest_dispatch` / `macro_latest_dispatch` / `project_latest_dispatch`
- the runtime board payload now also mirrors:
  - `receipt_surfaces.project_latest_dispatch`
  - `receipt_surfaces.primary_macro_latest_dispatch`
  - `receipt_surfaces.macro_latest_dispatch_template`
- the runtime board summary now states whether the project-global newest receipt matches the runtime-board primary macro
- fixed the runtime-board primary receipt surface so it is derived from the runtime board's own primary macro, not the dispatch-history board's independently ranked primary macro

## Validation

- `python -m py_compile src/vhk/cli.py tests/test_macro_runtime_board_json_cli.py`
- `pytest -q tests/test_macro_runtime_board_json_cli.py`
