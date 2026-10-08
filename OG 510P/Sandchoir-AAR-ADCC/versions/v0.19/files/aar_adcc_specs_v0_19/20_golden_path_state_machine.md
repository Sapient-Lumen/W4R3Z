# 20 — Golden Path State Machine (v0.19)

Design goal: progress even when slices are scarce (anytime).

States:
- BOOT: establish H0, minimal WS, leases if needed; optionally probe CAP# for persistent parse failures
- DIVERGE: agents propose parallel approaches (cheap)
- SELECT: choose patch/check/lease using sparse votes
- INTEGRATE: integrator applies selected patch / merges diffs
- STABILIZE: run fast verifiers, emit E# cards
- DISPUTE: short CE/test micro-phase (bounded)
- PARK: snapshot + record open items for next day/week

Anytime collapse rule:
- If bandwidth collapses, loop BOOT→DIVERGE→SELECT with minimal payloads.

MetaLLM hooks:
- shrink budgets, force compaction, assign integrator, switch modes.
