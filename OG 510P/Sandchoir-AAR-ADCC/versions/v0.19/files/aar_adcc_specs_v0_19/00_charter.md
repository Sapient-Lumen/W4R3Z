# 00 — Charter (v0.19)

## Problem statement
You have 3–5 local/CLI LLM agents. Each agent can read shared state multiple times “within a turn,” but the number and timing of those subturn slices are **unknown** and vary by model/client. You want them to cooperate on engineering tasks with minimal cost and maximal throughput.

The central constraint is **attention + context** (not CPU). Therefore the router is an **attention scheduler** first, and “deliberation” is a constrained byproduct.

## System components
### AAR — Adaptive Attention Router (prompt composer)
- Maintains per-agent **views**: Mandatory + Hot + Delta(cursor) + Role + (Discovery + Random).
- Enforces **budgets**: item-count caps and per-section caps.
- Implements compaction/eviction rules for the WS.

### ADCC — Adaptive Deliberation Control Conduit (governance)
- Modes + strictness ladder
- Voting (top-K sparse, optionally QV/STAR-style budgets)
- Leases/ownership and patch acceptance rules
- Counterexample (CE) lifecycle and evidence cards
- Minimal dispute micro-phases that don’t assume stable bandwidth

### MetaLLM Steward (outside the worker group)
- Reads telemetry and ledger summaries
- Issues CLI commands to the Rust router (small reversible levers)
- Proposes versioned config/plugin diffs between runs
- Maintains “bootstrap templates” and playbooks over weeks-long sessions

## Operator workflow
- **Worker terminals:** broadcast start prompts (boot templates) to agents.
- **Gearbox terminal:** human issues mode/strictness changes, approves canonicalization, can override intent.
- **MetaLLM terminal:** provides real-time steering recommendations and optional direct CLI control.

## Non-negotiable kernel invariants
1. **H0 first:** Human priority appears first in every view.
2. **WS strictness:** Only structured objects enter WS. Unstructured text remains Ledger-only.
3. **Cursor+deltas:** Agents read `DELTA(CURSOR)` by default, not full refresh.
4. **Mandatory channel:** Mode/strictness changes, lease changes, certified CE, selected patch are always shown.
5. **CE eligibility invariant:** witness + repro + expected signal.
6. **Patch summary for canonical changes** in S1+ (git diff recommended).
7. **Anytime packets:** `@CTRL` must appear early; partial outputs are still useful.

## Success criteria (early)
- Agents produce parseable `@CTRL` in >90% of slices (or repairable with 1 bounded re-ask).
- Canonical workspace stays coherent (low collision rate) using soft leases + patch diffs.
- WS remains small and high-signal; Ledger can be huge.
- MetaLLM can improve outcomes over days/weeks via config/plugin diffs without kernel rewrites.

## Hard choices (accepted)
- Consensus is expensive under jitter: protocol elections are *not* the hot path.
- We bias toward **diverge → select** over “chat until convergence.”
- Personalization is bounded (menu subscriptions) to prevent coordination drift.
