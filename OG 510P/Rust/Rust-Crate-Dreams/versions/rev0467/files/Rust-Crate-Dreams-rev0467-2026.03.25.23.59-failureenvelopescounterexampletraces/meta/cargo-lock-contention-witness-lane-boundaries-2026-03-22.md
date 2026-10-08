# Cargo lock-contention witness lane boundaries — 2026-03-22

Keep **P-0490** separate from these adjacent lanes.

## 1. Not rebuild causality

If the primary question is “why did Cargo recompile this unit?”, that belongs primarily to **P-0469 Cargo Rebuild Explanation Kit**.

P-0490 owns **blocked progress and shared-root truth**, not the full recompilation story.

## 2. Not build-script delegation topology

If the primary question is “which build units existed, which outputs they owned, and which override route was authoritative?”, that belongs primarily to **P-0508 Cargo Build Script Delegation Kit**.

P-0490 may import actor command lanes, but it is not a delegated-build planner.

## 3. Not compile-time sandbox policy

If the primary question is which build-time actor was allowed to access which files or network paths, that belongs primarily to **P-0107 Cargo Sandbox & Capability Policy Kit**.

P-0490 owns waiting/collision evidence, not capability grants.

## 4. Not toolchain/target support

If the primary question is whether a given target/toolchain/support matrix is real, that belongs primarily to **P-0484 Toolchain & Target Support Contract Kit**.

P-0490 may mention target/build-dir scope, but it is not a target-support checker.

## 5. Not generic performance telemetry

Historical timing warehouses and broad compile-performance dashboards remain separate lanes.
P-0490 must stay narrow enough that one issue attachment can be read without reproducing the incident live.

## 2026-03-22 addendum — not cache-policy, not lease coordination, not generic “mitigation succeeded” storytelling

### 6. Not global-cache governance

If the primary question is storage budgets, retention, exemption rules, or cleanup policy for Cargo-home caches, that belongs primarily to **P-0480 Cargo Global Cache Policy & GC Receipt Kit**.

P-0490 may mention package-cache lock modes, but it is not a cache-retention planner.

### 7. Not lease/coordination policy

If the primary question is who is allowed to share a cache root, how leases are acquired, or how cleanup honors those leases, that belongs primarily to **P-0436 Target-Dir Lease & Shared Cache Coordination Kit**.

P-0490 owns the incident witness after contention is observed, not the long-lived policy surface.

### 8. Not “mitigation applied means fixed”

P-0490 must keep these separate:
- topology changed,
- lock mode changed,
- residual contention remained,
- artifact duplication increased,
- or only confidence changed.

That is why mitigation-outcome diffing belongs here and generic success scoring does not.
