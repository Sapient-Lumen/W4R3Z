# Revision 0352 — project-wide author queue for the flagship i3/X11 warm-runtime lane

## What changed

VHK now ships a canonical **project-wide macro triage contract**:

```bash
vhk macro-author-queue-json <project>
```

and the generated flagship stack now includes:

```bash
bin/macro_author_queue_json.sh
```

This surface ranks macros by the same next-step policy used in the per-macro author loop, then exposes one stable answer to the question: **which macro should a private LLM open next?**

## Why this matters

Revision 0351 gave the private-LLM lane a fused per-macro contract. That still left one project-level reconstruction burden: a caller had to merge inventory, entrypoints, recorder drift, and review debt by hand before it could choose one macro to inspect.

Revision 0352 closes that gap on the flagship lane. The warm runtime now has:

- one project-wide triage surface for choosing a macro
- one per-macro fused contract for editing and replaying that macro
- one stack-state snapshot that already carries both

That keeps the i3/X11 warm-runtime handoff tighter and reduces control-plane churn for a private LLM.

## Payload shape

The new queue payload includes:

- project summary counts
- a `primary_macro` recommendation
- per-macro queue items with
  - preferred author/review/source entrypoints
  - preferred execution mode (`direct_run` vs `warm_runtime_dispatch`)
  - recorder freshness and brittle-segment posture
  - per-macro review debt counts
  - latest-run scope/verdict when applicable
  - the recommended next step

## Generated-stack integration

The generated i3/X11 warm-runtime stack now also:

- writes `bin/macro_author_queue_json.sh`
- advertises it in `control-plane.json` as a `runtime_snapshot` with `llm_mode: triage`
- treats it as part of the flagship stack-state helper set
- includes queue summary + `primary_macro` in `bin/stack_state_json.sh` output

## Tests

Revision 0352 adds and extends focused tests for:

- project-wide ranking/order of the author queue
- direct-run vs warm-runtime dispatch posture inside queue items
- generated stack helper emission and manifest wiring
- stack-state inclusion of the new queue surface
