# REV0381 — stack state derives a primary-macro command palette

## What changed

- `stack_state_json.sh` now derives `primary_macro_command_palette` for the author-queue-selected macro.
- The new fused slice normalizes concrete commands already present in the loaded per-macro surfaces:
  - active review-queue review command
  - checked-gate repair action
  - latest-run next step
  - author-loop next step
  - author-loop entrypoint
  - checked warm-runtime dispatch entrypoint
  - direct-run entrypoint
- The slice also names one `recommended` command using a resident-runtime-first priority order.
- `stack_state.sh` now prints the selected macro and recommended command from that palette.

## Why this matters

The fused stack snapshot already carried the selected macro's contract, recorder truth, latest run, checked gate, author loop, review queue, dispatch history, and entrypoints. But actually acting on that diagnosis still required the caller to reconstruct commands from several separate fields.

This revision makes the one-read i3/X11 control plane more executable: once the author queue has already selected a macro, the fused stack snapshot now tells the operator or private LLM which concrete command to run next without adding any new helper hop.

## Tests

Focused generated-stack tests cover:
- selected macro command palette derivation
- selected macro review queue slice
- selected macro latest dispatch slice
- flagship runtime handoff generation
