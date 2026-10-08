# Rematch proxy canonicalization snapshot (retained compact stub)

This compact retained stub restores the evidence path referenced by the risk and spec ledgers after archive trimming.
It preserves the minimal implementor-facing claim already threaded through `docs/LIBRARY/topics/rematch_proxy_search_space_canonicalization.md`.

## Snapshot claim

Under the current deterministic no-noise rematch proxy pool (`extortion_chi3_v1` and `mem1_generous_tft_v1`), `243` raw deterministic `memory_one_exit` codes collapse to `63` support-distinct decision families before exit.

## Why this path is retained

- Risk `RK-007` depends on evidence that raw rematch-world discovery counts can be inflated by behaviorally identical exit-policy aliases.
- The archive keeps this compact stub instead of a larger exploratory report to preserve the claim while controlling retained size.

## Handoff

- Human-readable representative family example: `CCEEE` is one readable representative of the broader `CCE**` family in the current proxy.
- Recompute the canonicalization map whenever opponent families, noise topology, or reachability assumptions change.
