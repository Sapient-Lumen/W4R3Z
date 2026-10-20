# Sync dishonest-storage matrix — 2026-09-17

Status: accepted same-host ext4+btrfs dishonest-storage matrix; not storage-media
or precious-data qualification.

## Commands

```sh
tools/iotox-repo.sh sync-dishonest-storage-matrix \
  --origin-size-mib 256 \
  --cow-size-mib 128
python3 tools/verify-sync-dishonest-storage-matrix.py \
  .sandwurm/exports/sync-dishonest-storage/run.qGwEvF17
```

## Accepted receipt

```text
run-id:                  run.qGwEvF17
source revision:         f8bd3b10eb87b4b23c5d6e3baaa1a340967799c6
receipt:                 .sandwurm/exports/sync-dishonest-storage/run.qGwEvF17/matrix.json
receipt-sha256:          ca78800eb5e942f51d23017e39c6cd8e5cf71658221d1bb1eac59b9923e60687
verification:            .sandwurm/exports/sync-dishonest-storage/run.qGwEvF17/matrix-verification.json
verification-sha256:     5e0047ccf34dc6753c9854c28844a32f559d9c34ec16da69f90aea3b3233d2c3
cell-count:              8
filesystems:             ext4, btrfs
scenarios:               valid-old-rollback, cross-family-rollback, torn-record, flakey-drop-writes
contains-secrets:        false
raw-retained:            false
```

The compact evidence consists of:

```text
matrix.json               36,553 bytes
matrix-summary.json          720 bytes
matrix-verification.json     337 bytes
```

The raw sparse images, mount directories, loop devices, and device-mapper nodes
were removed after the receipt was written. A follow-up check found no live
mount, mapper, or loop reference under `.sandwurm/lab/sync-dishonest-storage`.

## Cells

| Cell | Filesystem | Scenario | Interposer | Cold observation |
| ---: | --- | --- | --- | --- |
| 0 | ext4 | valid-old-rollback | `dm-snapshot` | all families valid generation 1 |
| 1 | ext4 | cross-family-rollback | `dm-snapshot` | valid mixed generation 1 and 2 |
| 2 | ext4 | torn-record | `dm-snapshot` | invalid JSON manifest beside valid generation 1 families |
| 3 | ext4 | flakey-drop-writes | `dm-flakey drop_writes` | all families valid generation 1 |
| 4 | btrfs | valid-old-rollback | `dm-snapshot` | all families valid generation 1 |
| 5 | btrfs | cross-family-rollback | `dm-snapshot` | valid mixed generation 1 and 2 |
| 6 | btrfs | torn-record | `dm-snapshot` | invalid JSON manifest beside valid generation 1 families |
| 7 | btrfs | flakey-drop-writes | `dm-flakey drop_writes` | all families valid generation 1 |

Every cell wrote generation 2 through the faulting device and read it back
before teardown. Every cold state differed from the acknowledged generation-2
external witness floor, so every cell detected rollback or damage and refused
mutation.

The six IoTox-shaped families are branch pointer, immutable branch record,
manifest, workspace, maintenance, and projection marker.

## Boundary

This is the first accepted btrfs dishonest-storage evidence and the first
accepted masked-write-loss cell. It remains a same-host sparse-image drill. It
does not prove:

- storage-media honesty or firmware behavior;
- exact production Agent write-prefix replay by itself;
- full `dm-log-writes` replay-log coverage;
- an NBD/virtio proxy under a Sandwurm guest;
- independent backup custody;
- physical power removal; or
- precious-data readiness.

ADR 0380 and ADR 0381 later add exact block-prefix replay and live-Agent
production transaction-prefix replay. This matrix remains the cross-family and
masked-write layer beneath those later gates.
