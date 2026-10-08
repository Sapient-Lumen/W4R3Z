# ADR 0073 — Witness repair is bounded local next action

## Decision

Witness repair planning remains bounded and local.

## Rationale

Witness receipts are evidence, not quorum. When evidence is low-diversity or stale, the client/garden needs practical next actions, not a global reputation system.

## Consequence

`witnessrepair.py` asks missing families, refreshes expired evidence, preserves good evidence, or quarantines contradictions. It does not decide truth.
