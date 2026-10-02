# ADR 0379: Extend dishonest-storage science to btrfs and flakey writes

Status: accepted and implemented
Date: 2026-09-17

## Context

ADR 0378 accepted the first block-layer dishonest-storage drill: one ext4
`dm-snapshot` valid-old rollback was detected and refused against an external
witness floor. That established the receipt shape but left the more useful
matrix open:

- btrfs, which is the filesystem most users are expected to run;
- cross-family rollback instead of one uniform older generation;
- torn content instead of only valid older records; and
- masked write loss instead of only discarded snapshot COW state.

`dm-log-writes` is present as a kernel target on this host, but the companion
userspace replay tooling is not part of the ordinary PATH. Exact production
Agent write-prefix replay therefore remains a distinct adapter gate rather
than something this ADR can honestly claim.

## Decision

Add a matrix-level harness and verifier:

- `tools/run-sync-dishonest-storage-matrix.py`;
- `tools/verify-sync-dishonest-storage-matrix.py`;
- `tools/iotox-repo.sh sync-dishonest-storage-matrix`; and
- non-privileged CTest self-tests for both tools.

The default matrix runs eight same-host block-layer cells:

| Filesystem | Scenario | Interposer | Cold state |
| --- | --- | --- | --- |
| ext4 | valid-old rollback | `dm-snapshot` | all six families valid generation 1 |
| ext4 | cross-family rollback | `dm-snapshot` | manifest/record generation 2, other families generation 1 |
| ext4 | torn record | `dm-snapshot` | torn manifest beside older valid families |
| ext4 | masked write loss | `dm-flakey drop_writes` | all six families valid generation 1 |
| btrfs | valid-old rollback | `dm-snapshot` | all six families valid generation 1 |
| btrfs | cross-family rollback | `dm-snapshot` | manifest/record generation 2, other families generation 1 |
| btrfs | torn record | `dm-snapshot` | torn manifest beside older valid families |
| btrfs | masked write loss | `dm-flakey drop_writes` | all six families valid generation 1 |

The six content-free IoTox-shaped families are branch pointer, immutable branch
record, manifest, workspace, maintenance, and projection marker.

Every cell writes generation 2 through the faulting device and verifies that it
is visible before teardown. The cold mount then observes either the older
valid state, a mixed valid state, or a torn state. The external floor remembers
the acknowledged generation-2 state, so every cell must detect rollback or
damage and refuse mutation.

## Consequences

This substantially widens dishonest-storage coverage and adds the btrfs path
without pretending the problem is finished. It is still same-host sparse image
evidence, not storage-media certification. It uses production-shaped records and
write families, not live three-Agent production write-prefix capture/replay.
It also does not create independent backup custody or precious-data readiness.

The next exact-prefix adapter should use `dm-log-writes` with replay tooling or
an NBD/virtio block proxy in front of a Sandwurm guest disk. The acceptance
rule is the same: name the selected production write/flush prefix, cold-mount
the replayed image, and refuse unsafe rollback, mixture, tear, or masked error
without deleting evidence.

## Evidence

Committed-source run `run.qGwEvF17` passes:

```text
source revision:        f8bd3b10eb87b4b23c5d6e3baaa1a340967799c6
receipt:                .sandwurm/exports/sync-dishonest-storage/run.qGwEvF17/matrix.json
receipt-sha256:         ca78800eb5e942f51d23017e39c6cd8e5cf71658221d1bb1eac59b9923e60687
verification:           .sandwurm/exports/sync-dishonest-storage/run.qGwEvF17/matrix-verification.json
verification-sha256:    5e0047ccf34dc6753c9854c28844a32f559d9c34ec16da69f90aea3b3233d2c3
cell-count:             8
filesystems:            ext4, btrfs
scenarios:              valid-old-rollback, cross-family-rollback, torn-record, flakey-drop-writes
contains-secrets:       false
raw-retained:           false
```

See `../evidence/2026-09-17-sync-dishonest-storage-matrix.md`.
