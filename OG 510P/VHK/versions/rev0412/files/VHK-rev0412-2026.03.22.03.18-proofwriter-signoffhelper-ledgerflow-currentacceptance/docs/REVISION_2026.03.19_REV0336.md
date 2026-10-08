# Revision 0336 — developer-tree bootstrap for the flagship i3/X11 stack

This pass tightened the i3/X11 warm-runtime lane for real repo-local use.

## What changed

- added `--vhk-pythonpath` to:
  - `vhk gen-i3-busd-stack`
  - `vhk gen-vhk-busd-service`
  - `vhk gen-vhk-busd-socket-units`
- generated `bin/` wrappers that invoke `vhk` now export that Python path when present
- generated busd systemd user units now embed the same bootstrap in `ExecStart` via `/usr/bin/env PYTHONPATH=...`
- `control-plane.json` now records:
  - `runtime.vhk_cmd`
  - `runtime.vhk_pythonpath`
  - `runtime.developer_tree_mode`
- expanded the i3/X11 stack test coverage around wrapped local `python -m vhk.cli` usage

## Why it matters

The flagship stack is supposed to be easy for both humans and a private LLM to drive. Before this pass, a generated stack built against a local wrapper like `python -m vhk.cli` could fail once it ran outside the repo root because the module path was no longer implicit. Now the generated stack can carry its own explicit bootstrap for uninstalled/developer-tree use, which makes the warm-runtime lane more trustworthy during active repo work.
