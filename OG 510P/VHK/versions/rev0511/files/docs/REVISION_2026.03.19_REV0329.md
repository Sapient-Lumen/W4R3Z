# Revision 0329 — explicit LLM control-plane contract for the warm runtime

This pass makes the flagship i3/X11 warm-runtime stack easier to inspect and
drive by adding a small machine-readable control-plane contract plus stable
project-pinned wrappers for direct runs and macro discovery.

## What changed

- `vhk gen-i3-busd-stack` now generates:
  - `control-plane.json`
  - `bin/list_macros.sh`
  - `bin/run_macro.sh`
- the generated stack now exposes one clearer contract for:
  - macro discovery
  - direct ad hoc runs through the CLI path
  - warm-runtime dispatch
  - recorder/report/trace/history loops
  - runtime lifecycle / logs / status
- the runtime-stack and bus daemon docs now describe the generated control plane
  as the preferred shell + private-LLM handoff surface

## Why it matters

The repo already had a warmer runtime and a growing set of generated helper
scripts, but the contract was still partly implicit. This revision makes that
contract more explicit for both humans and tools: a private LLM can inspect a
small generated manifest, list the project macros, choose between direct ad hoc
runs and resident-runtime dispatch, and then use the recorder/inspect surface
without reconstructing the repo's command grammar every turn.
