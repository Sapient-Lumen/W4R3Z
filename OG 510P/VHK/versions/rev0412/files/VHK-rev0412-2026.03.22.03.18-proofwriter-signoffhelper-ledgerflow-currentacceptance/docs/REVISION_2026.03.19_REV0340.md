# Revision 0340 — fused stack state carries real macro inventory

This revision makes the generated i3/X11 flagship stack more truthful and more useful to a private LLM by fixing `bin/stack_state_json.sh` so it actually carries macro inventory instead of only macro names. The fused state surface now includes machine-readable macro/preset/group/tag inventory derived from `bin/macro_inventory_json.sh`, and `bin/stack_state.sh` exposes compact preset/group/tag counts for operators.

## What changed

- updated `bin/stack_state_json.sh` generation so it now consumes `bin/macro_inventory_json.sh`
- added `macro_inventory` to the fused stack-state payload with:
  - `macro_count`
  - `visible_macro_count`
  - `hidden_macro_count`
  - `preset_total`
  - `groups`
  - `tags`
  - full macro inventory entries
- updated `bin/stack_state.sh` so the human summary now prints `preset_total`, `group_count`, and `tag_count`
- corrected the control-plane manifest text so `stack_state_json` explicitly advertises latest-run health as part of the fused snapshot
- updated `README.md`, `docs/I3_X11_RUNTIME_STACK.md`, and `docs/BUS_DAEMON.md` to reflect the stronger fused control-plane truth

## Why this matters

Before this revision, the generated stack advertised a fused state surface that included macro inventory, but in practice it only surfaced macro names. After this revision, a private LLM can inspect one JSON payload and see not just whether the warm runtime is healthy, but also what macros exist, how many presets they expose, and what groups/tags shape the project.
