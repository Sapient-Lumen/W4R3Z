# ADR 0380: Accept dm-log-writes prefix replay and freeze storage readiness gates

Status: accepted and implemented
Date: 2026-09-17

## Context

ADR 0379 extended dishonest-storage science to ext4 and btrfs, but it still
used snapshot/flakey constructions instead of a real block write log. That was
useful, but the next credible substrate needed to replay exact durable write
prefixes from below the filesystem.

The host has the in-tree `dm-log-writes` kernel target. The replay helper is
available inside the Nix `xfstests` output at
`lib/xfstests/src/log-writes/replay-log`, even though it is not exposed as a
plain PATH command.

## Decision

Add a same-host prefix-replay gate:

- `tools/run-sync-log-writes-prefix-replay.py`;
- `tools/verify-sync-log-writes-prefix-replay.py`;
- `tools/iotox-repo.sh sync-log-writes-prefix-replay`; and
- non-privileged CTest self-tests for runner and verifier.

The runner puts an ordinary ext4 or btrfs filesystem on a `dm-log-writes`
device, marks three content-free IoTox sync boundaries, replays those exact
block-log prefixes onto fresh images, cold-mounts each replay, and verifies the
state:

| Mark | Meaning | Required result |
| --- | --- | --- |
| `generation-1-stable` | older valid branch/workspace floor after directory fsync | detect rollback against generation-2 floor and refuse mutation |
| `manifest-record-prefix` | manifest and immutable branch-record installed before mutable branch pointer | detect mixed prefix against generation-2 floor and refuse mutation |
| `generation-2-stable` | complete pointer/workspace/projection generation after directory fsync | accept as current |

The gate covers ext4 and btrfs. It is still same-host sparse-image substrate
evidence and deliberately does not claim live-Agent production write-prefix
capture/replay, storage-media certification, backup, physical power removal, or precious-data
readiness.

Add `tools/qualify-storage-readiness.py` and
`tools/iotox-repo.sh storage-readiness` as the executable status boundary. That
report accepts the local substrate only when both the ADR 0379 matrix and this
prefix replay verify, and it keeps precious-data readiness blocked until live
Agent production replay and independent backup
custody have their own accepted receipts.

ADR 0381 later adds the live-Agent production transaction-prefix adapter, so
this ADR is now the accepted synthetic block-prefix substrate beneath that
production proof.

## Consequences

The project now has three different same-host dishonest-storage layers:

1. a one-cell ext4 snapshot rollback drill;
2. an ext4+btrfs snapshot/flakey matrix; and
3. an ext4+btrfs `dm-log-writes` marked-prefix replay.

That meaningfully raises confidence in the storage protocol shape, especially
for btrfs users, but it is not a release claim for precious originals. At the
time of this ADR, the remaining frontier was not more synthetic same-host
state. It was:

- a live-Agent production prefix adapter;
- storage-media certification is out of scope after ADR 0400; and
- independent immutable/versioned backup custody.

ADR 0381 closes the first bullet for transaction-boundary production replay.
The latter two remain open.

## Evidence

Committed-source run `run.90LCC7ra` passes:

```text
source revision:        9b0c54d249625fa43c3dfc9070fb0008e545917c
receipt:                .sandwurm/exports/sync-log-writes-prefix/run.90LCC7ra/prefix-replay.json
receipt-sha256:         f897df7503d57b801cbb94f9a6a0e752b703d5203e00764890ca628d80a93e67
verification:           .sandwurm/exports/sync-log-writes-prefix/run.90LCC7ra/prefix-replay-verification.json
verification-sha256:    c1bc23aec693138e31a05dfba9befb479c372f409cdf5fc35d52542a84f36a7c
filesystems:            ext4, btrfs
marks:                  generation-1-stable, manifest-record-prefix, generation-2-stable
contains-secrets:       false
raw-retained:           false
```

See `../evidence/2026-09-17-sync-log-writes-prefix-replay.md`.
