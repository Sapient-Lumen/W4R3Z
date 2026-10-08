# REV0370 — stack next action now follows the author queue and checked gate

## What changed

- Updated the generated `bin/next_action_json.sh` helper so it consults `bin/macro_author_queue_json.sh` first.
- When the author queue already has a primary macro, `bin/next_action_json.sh` now also opens `bin/macro_dispatch_gate_json.sh <macro>` for that macro.
- The stack-level primary action can now come from:
  - author-queue dispatch attention
  - author-queue next step
  - checked-gate `ready_to_dispatch`
  - checked-gate `use_direct_run`
- The helper now preserves `macro_author_queue` and `dispatch_gate` context in its JSON payload so one top-level read remains actionable for the private-LLM lane.

## Why this matters

The repo's resident-runtime control plane had already moved to the author queue, dispatch-history pressure, and checked-dispatch repair actions. But the generated stack's top-level next-action helper still leaned on older review-queue and latest-run heuristics. This revision makes the stack-level helper match the i3/X11-first warm-runtime control plane instead of bypassing it.

## Tests

Focused generated-stack tests now cover:

- author-queue-driven recorder refresh
- author-queue-driven latest-failure inspection
- checked-gate `ready_to_dispatch` for the primary macro
