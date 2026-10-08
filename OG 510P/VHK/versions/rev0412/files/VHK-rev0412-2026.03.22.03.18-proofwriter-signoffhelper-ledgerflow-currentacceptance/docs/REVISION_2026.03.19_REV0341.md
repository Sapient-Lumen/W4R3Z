# REV0341 — macro entrypoints control-plane surface

This revision strengthens the i3/X11 warm-runtime control plane around **macro invocation discovery** instead of adding breadth.

## What changed

- Added `vhk macro-entrypoints-json PROJECT_DIR`
  - machine-readable project-wide map of preferred macro invocation routes
  - includes per-macro preferred warm-runtime/direct-run/contract entrypoints, preset names, prompt-profile keys, capability hints, and direct-run/dispatch option surfaces
- Extended `vhk gen-i3-busd-stack` with generated `bin/macro_entrypoints_json.sh`
- Extended generated `control-plane.json` so macro entrypoints are part of the preferred operator/private-LLM handoff surface
- Extended generated `stack_state_json.sh` metadata so recommended entrypoints now mention `bin/macro_entrypoints_json.sh`
- Updated generated stack README wording to call out project-wide macro entrypoint discovery

## Why it matters

A private LLM no longer has to merge `macro_inventory_json` and many per-macro `macro_contract_json` calls just to answer “how should I invoke what exists here?” The warm-runtime stack now exposes a single project-wide entrypoint map for that.
