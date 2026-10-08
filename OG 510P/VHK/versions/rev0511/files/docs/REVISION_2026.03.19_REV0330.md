# Revision 0330 — machine-readable warm-runtime health plus stricter macro wrappers

This pass makes the flagship i3/X11 warm-runtime stack easier to operate and
safer for both humans and a private LLM by adding a JSON readiness/status helper
and making the generated run/dispatch wrappers fail fast on unknown macro names.

## What changed

- `vhk gen-i3-busd-stack` now also generates:
  - `bin/status_runtime_json.sh`
- `control-plane.json` now records:
  - the resolved bus-socket path for the generated stack
  - the new JSON runtime-status helper in the control-plane contract
- generated wrappers are stricter:
  - `bin/run_macro.sh` now checks that the requested macro exists before running
  - `bin/dispatch_macro.sh` now checks that the requested macro exists before
    emitting a warm-runtime dispatch event
- docs updated:
  - `README.md`
  - `docs/I3_X11_RUNTIME_STACK.md`
  - `docs/BUS_DAEMON.md`

## Why it matters

The repo already had a better shell/LLM control surface than before, but runtime
health and bad macro names were still easier to discover after the fact than up
front. This revision improves the operator contract in two practical ways: a
controller can read one stable JSON health snapshot to see whether the session-
bound runtime is actually present and loaded, and direct/dispatch wrappers now
fail early with a clearer error when the requested macro is not in the project.
