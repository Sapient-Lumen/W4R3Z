# Revision 0328 — recorder/observability control surface for the warm runtime

This pass extends the flagship i3/X11 warm-runtime stack so it carries the
recorder -> inspect loop with it, not just runtime control.

## What changed

- `vhk gen-i3-busd-stack` now generates additional `bin/` scripts:
  - `bin/record_macro.sh`
  - `bin/report_latest.sh`
  - `bin/trace_latest.sh`
  - `bin/history_runs.sh`
- the generated README and runtime-stack docs now treat the warm stack as a
  stable **operator + authoring + observability** surface
- `record_macro.sh` encodes the current preferred X11 recorder defaults for the
  repo's flagship lane: optimize, compress text, promote long literal text to
  clipboard when safe, capture/apply stable window context, and segment by
  window-context with event guards

## Why it matters

The resident runtime was already easier to start and control, but the project's
main authoring loop still leaked back into raw CLI grammar. This revision makes
that loop more explicit and easier to drive from shell or from a private LLM:
record a candidate macro, inspect the newest run, export a trace, and review
recent history without rebuilding the command surface every turn.
