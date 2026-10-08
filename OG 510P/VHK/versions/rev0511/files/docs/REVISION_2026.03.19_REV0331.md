# Revision 0331 — prerequisite checks and fail-fast runtime assertions for the i3/X11 stack

This pass strengthened the generated flagship stack as an operator and LLM handoff
surface by adding explicit prerequisite checks, not just unit-state reporting.

## What changed

- `vhk gen-i3-busd-stack` now also generates:
  - `bin/check_runtime_json.sh`
  - `bin/assert_runtime_ready.sh`
- `control-plane.json` now records both scripts in the generated control-plane contract
- the generated stack README and docs now describe readiness checks as part of the
  flagship i3/X11 warm-runtime lane

## Why this matters

The warm runtime already had direct-run, dispatch, recorder, and status/log surfaces.
This revision adds a stable answer to a different question: **is the stack actually
ready for i3/X11 record/run/dispatch right now?**

`bin/check_runtime_json.sh` emits a focused machine-readable snapshot that covers:

- project presence
- macro inventory
- session env (`DISPLAY`, `XDG_RUNTIME_DIR`, `DBUS_SESSION_BUS_ADDRESS`)
- required X11/runtime tools (`python3`, `systemctl`, `journalctl`, `xdotool`, `xprop`, `xwininfo`)
- recommended helpers (`i3-msg`, `xclip`, `xsel`, `xvkbd`)
- socket/service state
- synthesized blockers/warnings plus compact capability flags

`bin/assert_runtime_ready.sh` is the shell-friendly fail-fast gate built on top of
that JSON contract.

## Validation

- `python -m compileall -q src/vhk tests`
- `pytest -q tests/test_i3_busd_stack_cli.py tests/test_busd_service_cli.py tests/test_busd_socket_units_cli.py`
