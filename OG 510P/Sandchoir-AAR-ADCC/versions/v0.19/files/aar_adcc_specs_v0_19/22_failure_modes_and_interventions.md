# 22 — Failure Modes + Interventions (v0.19)

## Consensus collapse (everyone agrees)
- Require 1 concern per agent
- Promote skeptic role items
- Add discovery/random slots briefly

## Deadlocks (sync without value)
- Force SELECT with patch/check vote
- Assign integrator
- Switch to PatchOnly

## Prompt injection / backchannel drift
- Keep WS strict; ledger only for prose
- Disallow unstructured “DMs”; require REQ# tickets
- Mandatory channel cannot be muted

## Runaway context growth
- Compaction now (SUM#)
- Shrink budgets
- Evict stale low-hotness items

## Thrash on files
- Soft leases
- Patch summaries only
- Escalate to hard leases or PatchOnly

## Operator broadcast footgun
- If using Terminator broadcast, watch for duplicated input; prefer file-based broadcast (see 29_broadcast_ops_guidance.md).
