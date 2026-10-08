# Revision 0363 - 2026-03-21

## Summary

The project-wide private-LLM author queue now treats warm-runtime dispatch trouble as triage pressure instead of passive observability.

## What changed

- added per-macro `dispatch_attention` to `macro-author-queue-json`
- added dispatch-pressure-aware `priority.dispatch_pressure_rank` and `priority.effective_rank`
- queue ordering now escalates warm-runtime execute-lane macros when dispatch history shows:
  - repeated checked-dispatch blocks
  - unresolved forced overrides
- summary/project counts now expose dispatch-attention and dispatch-pressure escalation counts
- updated the X11/i3 runtime and LLM control-plane docs to describe the new queue policy

## Why

The resident-runtime lane already had a receipt-backed dispatch-history board and a checked-dispatch gate, but the project-wide author queue still behaved as if dispatch trouble were only observability. A private LLM could miss the most operationally important macro because queue rank did not respond to repeated warm-runtime blocks or unresolved `--force` usage.

## Guardrails

- recorder evidence, freshness drift, and brittle cleanup debt still outrank dispatch pressure
- dispatch pressure only escalates warm-runtime macros already in the execute lane
- direct-run-only macros do not use warm-runtime dispatch pressure for queue ordering
