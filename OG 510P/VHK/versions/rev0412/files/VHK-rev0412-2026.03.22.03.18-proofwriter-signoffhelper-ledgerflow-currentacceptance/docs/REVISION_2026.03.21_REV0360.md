# Revision 0360 — dispatch-history board for repeated-block / forced-override truth

This revision adds a project-wide dispatch receipt history board to the resident i3/X11 control plane.

## Added

- `vhk macro-dispatch-history-board-json <project>`
- generated `bin/macro_dispatch_history_board_json.sh`
- per-macro dispatch-history postures derived from durable receipt history
- fused stack-state integration for dispatch-history board summary and helper metadata

## Tightened

- runtime board items now carry dispatch-history context
- dispatch catalog items now carry dispatch-history context
- checked-dispatch gate payloads now carry dispatch-history context
- generated stack README/control-plane now describe dispatch-history as a first-class resident-runtime surface

## Why

The warm resident runtime and a private LLM should not have to infer repeated checked-dispatch failures or unresolved forced overrides from a single latest receipt.
