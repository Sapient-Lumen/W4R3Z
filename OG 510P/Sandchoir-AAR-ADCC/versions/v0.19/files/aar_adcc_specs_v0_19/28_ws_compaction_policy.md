# 28 — WS Compaction + Eviction Policy (v0.19)

Runaway context growth is the predictable failure mode. WS must stay small and sharp.

## Hard caps (defaults)
- WS object count cap: 60
- HOT list cap: 8
- Per-type caps:
  - C#: 12  T#: 12  P#: 10  E#: 12  CE#: 8  REQ#: 10  LEASE#: 12  CAP#+SUM#: <=6

## Un-evictable anchors
- H0 (active)
- mode/strictness
- selected patch (if any)
- certified CE (if any)
- latest failing canonical check evidence (if any)

## Eviction scoring (lowest first)
- Base score = hotness
- Penalties: stale age, duplicates, pure-talk-without-action
- Bonuses: referenced by selected patch / certified CE; referenced by >=2 active tasks

## Triggers
- WS exceeds caps
- HOT list thrash
- explicit `ws compact` or `compact{yes=...}`

## Compaction outputs
- Create SUM#:
  - kept decisions
  - open questions
  - ledger pointers
- Evicted items become `superseded` (not deleted).

## Value density proxy
If density is low (few E#/P#/CE updates) while churn is high:
- compact, then shrink budgets.
