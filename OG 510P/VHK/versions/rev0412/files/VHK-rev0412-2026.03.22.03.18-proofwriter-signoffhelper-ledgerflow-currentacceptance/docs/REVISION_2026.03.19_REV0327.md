# Revision 0327 — warm-runtime operator control plane

This pass reinforces the i3/X11-first, resident-runtime story by turning the
generated warm-runtime stack into a more usable control surface for both humans
and a private LLM.

## What changed

- `vhk gen-i3-busd-stack` now emits a `bin/` directory alongside systemd units and
  the i3 snippet
- the generated stack now includes:
  - `bin/dispatch_macro.sh`
  - `bin/reload_runtime.sh`
  - `bin/stop_runtime.sh`
  - `bin/status_runtime.sh`
  - `bin/logs_runtime.sh`
- the stack README and runtime docs now treat those scripts as the stable control
  plane for the resident runtime

## Why it matters

The repo had already chosen a warm, session-bound runtime as the flagship lane,
but the operator surface was still fragmented. You could generate units and an i3
snippet, yet higher-level control still required reconstructing raw `vhk`,
`systemctl --user`, and `journalctl --user` calls by hand.

This revision closes part of that gap. The flagship stack now exports a compact,
explicit handoff surface that keeps ad hoc CLI runs available while making the
resident runtime easier to drive from shell, support flows, and LLM-authored
automation.
