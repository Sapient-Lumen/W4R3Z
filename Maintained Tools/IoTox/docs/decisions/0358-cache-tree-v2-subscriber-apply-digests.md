# ADR 0358: Cache tree-v2 subscriber apply source digests

- Status: accepted and implemented
- Date: 2026-09-09

## Context

ADR 0356 made retained tree-v2 pull status include the final local reconciliation result, and ADR
0357 carried those counters into Sandwurm three-writer receipts. The first fresh cap-8 run with those
counters passed, but it showed that completed pull/apply cycles still reported `source-reused=0`
while repeatedly hashing selected worktree files during final reconciliation.

Agent-owned local publish/reconcile already has a volatile `TreeV2SourceDigestCache` from ADR 0344.
Subscriber completion did not use that cache path; it called `reconcile_tree_v2_workspace()` directly
after accepting the signed frontier and committing missing immutable objects.

## Decision

`TreeV2SubscriberService` now owns an in-process source digest cache keyed by namespace id,
namespace root, and local worktree. Pull completion passes that cache into
`reconcile_tree_v2_workspace()` when applying the accepted tree-v2 frontier.

The cache remains volatile. It is not serialized, signed, exported, or sent to peers.

## Consequences

Repeated no-op pull/apply cycles can inspect the local tree but reuse unchanged file digests instead
of hashing every selected regular file. This targets recurring automation and near-ceiling follower
pull churn without changing any Tox frame, durable sync record, authority rule, signed branch, CAS
object, or projection marker.

The existing reconciler still controls validity. It creates updated cache entries only after stable
file identity checks and clears the cache after a workspace projection exchange because projected
files may have new local identities. Any namespace/source/projection mismatch, restart, metadata
change, or content change falls back to hashing.

This is an apply-side CPU optimization only. It does not prove backup readiness, dishonest-storage
tolerance, or production latency.

## Evidence

The owned unit/integration registry now verifies the subscriber cache behavior directly:

- the initial pull projects four files;
- the first unchanged follow-up pull hashes those four files and warms the subscriber cache; and
- the second unchanged follow-up pull reports zero hashed file digests and four reused file digests.

Accepted local check:

```text
nix develop -c bash -lc 'cmake --build build -j2 --target iotox_tests && ctest --test-dir build -R "^iotox\\.unit-and-integration$" --output-on-failure'
```

Accepted VM evidence:

```text
./tools/iotox-sandwurm-lab.sh up-three-writer near-ceiling-cap-8
./tools/iotox-sandwurm-lab.sh export-three-writer .sandwurm/lab/three-writer-near-ceiling-cap-8/run.T6m7lxAN
./tools/iotox-sandwurm-lab.sh verify-three-writer .sandwurm/exports/three-writer/run.T6m7lxAN
python3 tools/verify-sandwurm-vm-smoke.py .sandwurm/exports/three-writer/run.T6m7lxAN device
```

The retained compact proof `.sandwurm/exports/three-writer/run.T6m7lxAN` passed and reported
`source_hashed=0` / `source_reused=28008` on two nodes' retained final apply counters. The same run
also showed this optimization is not the near-ceiling throughput fix: catch-up took 940.891 seconds,
with follower CAS full-inventory scans at 92/94 and late-offer cancellations at 14/11.
