# REV0342 — fused stack state now carries macro entrypoints

This revision tightens the flagship i3/X11 warm-runtime control plane around one-shot invocation truth.

## What changed

- Extended generated `bin/stack_state_json.sh` so it now consumes `bin/macro_entrypoints_json.sh` and includes a real `macro_entrypoints` payload instead of only pointing callers at that helper in metadata
- The fused state now carries:
  - `macro_count`
  - `interactive_macro_count`
  - `preset_enabled_macro_count`
  - the full per-macro preferred warm-runtime/direct-run/contract entrypoints
- Extended generated `bin/stack_state.sh` so the human/operator summary now prints `interactive_macro_count` and `preset_enabled_macro_count`
- Extended the fused-state helper metadata so `macro_entrypoints_json` reports its counts directly inside `sources.helpers`
- Updated `README.md`, `docs/I3_X11_RUNTIME_STACK.md`, and `docs/BUS_DAEMON.md` to reflect that the fused stack-state snapshot now carries invocation-route truth, not just inventory and health

## Why it matters

The flagship stack already had inventory, contracts, and a project-wide entrypoint helper, but callers still had to merge that information themselves when they wanted a single one-shot answer to “what can I call here and what is the preferred route?” This revision makes the fused state payload materially more useful for a private LLM and for operators who want a single trusted snapshot instead of helper-chaining.
