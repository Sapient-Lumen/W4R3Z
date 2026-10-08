# Revision 0339 — macro contracts + direct-run wrapper fix

This revision adds `vhk macro-contract-json PROJECT_DIR MACRO`, extends the generated i3/X11 warm-runtime stack with `bin/macro_contract_json.sh`, and fixes the generated `bin/run_macro.sh` wrapper so it calls `vhk run` with the correct project-first CLI shape instead of a nonexistent `--project` flag.

## What changed

- added `vhk macro-contract-json PROJECT_DIR MACRO`
  - emits a machine-readable invocation contract for one macro
  - includes preset names, preset vars, prompt-form fields, prompt-profile keys, step-shape hints, and preferred direct-run / warm-dispatch examples
- extended `vhk gen-i3-busd-stack` with:
  - `bin/macro_contract_json.sh`
- extended generated `control-plane.json` so macro-contract discovery is part of the preferred private-LLM/operator surface
- extended generated `stack_state_json.sh` metadata so recommended entrypoints and helper sources now mention the macro-contract surface
- fixed generated `bin/run_macro.sh` to call:
  - `vhk run PROJECT_DIR MACRO ...`
  - instead of the broken `vhk run --project PROJECT_DIR ...`

## Validation

- `python -m compileall -q src/vhk tests`
- `pytest -q tests/test_macro_contract_json_cli.py`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_gen_i3_busd_stack_writes_flagship_runtime_handoff`
- `pytest -q tests/test_macro_inventory_json_cli.py tests/test_latest_run_health_json_cli.py`

The subprocess-heavy generated-stack execution harness remained flaky in this sandbox, so I validated the new slice primarily through compile plus focused CLI/generator tests rather than claiming a fully clean pass on that unstable path.
