# Sync dm-log-writes prefix replay — 2026-09-17

Status: accepted same-host ext4+btrfs synthetic `dm-log-writes`
marked-prefix replay; superseded for production transaction coverage by
`run.HYXJnDzI`; not storage-media certification, backup, or precious-data
readiness.

## Commands

```sh
tools/iotox-repo.sh sync-log-writes-prefix-replay \
  --origin-size-mib 256 \
  --log-size-mib 512
python3 tools/verify-sync-log-writes-prefix-replay.py \
  .sandwurm/exports/sync-log-writes-prefix/run.90LCC7ra
tools/iotox-repo.sh storage-readiness
```

## Accepted receipt

```text
run-id:                  run.90LCC7ra
source revision:         9b0c54d249625fa43c3dfc9070fb0008e545917c
receipt:                 .sandwurm/exports/sync-log-writes-prefix/run.90LCC7ra/prefix-replay.json
receipt-sha256:          f897df7503d57b801cbb94f9a6a0e752b703d5203e00764890ca628d80a93e67
verification:            .sandwurm/exports/sync-log-writes-prefix/run.90LCC7ra/prefix-replay-verification.json
verification-sha256:     c1bc23aec693138e31a05dfba9befb479c372f409cdf5fc35d52542a84f36a7c
replay-tool:             /nix/store/z6ms9cm3ksrlivk1a4a05is9hqgadkym-xfstests-2026.07.21/lib/xfstests/src/log-writes/replay-log
replay-tool-sha256:      ecec252bdc66235440f6e6d1eadc94cd11b6905b027d32f08537fbc162eac28e
cell-count:              2
filesystems:             ext4, btrfs
marks:                   generation-1-stable, manifest-record-prefix, generation-2-stable
contains-secrets:        false
raw-retained:            false
```

The compact evidence consists of:

```text
prefix-replay.json                  24,383 bytes
prefix-replay-summary.json             929 bytes
prefix-replay-verification.json        317 bytes
```

The raw sparse images, log images, replay images, mount directories, loop
devices, and device-mapper nodes were removed after the receipt was written. A
follow-up check found no live mount, mapper, or loop reference under
`.sandwurm/lab/sync-log-writes-prefix`.

## Cells

| Filesystem | Mark | Replay entry | Cold observation | Result |
| --- | --- | ---: | --- | --- |
| ext4 | `generation-1-stable` | 263 | all six families valid generation 1 | older than acknowledged floor; mutation refused |
| ext4 | `manifest-record-prefix` | 322 | manifest and immutable branch record at generation 2; mutable pointer/workspace/maintenance/projection marker at generation 1 | mixed prefix; mutation refused |
| ext4 | `generation-2-stable` | 462 | all six families valid generation 2 | accepted as current |
| btrfs | `generation-1-stable` | 456 | all six families valid generation 1 | older than acknowledged floor; mutation refused |
| btrfs | `manifest-record-prefix` | 494 | manifest and immutable branch record at generation 2; mutable pointer/workspace/maintenance/projection marker at generation 1 | mixed prefix; mutation refused |
| btrfs | `generation-2-stable` | 580 | all six families valid generation 2 | accepted as current |

The six content-free IoTox-shaped families are branch pointer, immutable branch
record, manifest, workspace, maintenance, and projection marker.

## Boundary

This is stronger than the earlier snapshot/flakey matrix because the cold
images are reconstructed by replaying exact block-log prefixes from
`dm-log-writes`, not by manually choosing a high-level filesystem state.

It still does not prove:

- live Agent production write-prefix capture/replay by itself;
- storage-media honesty, firmware behavior, or controller cache behavior;
- physical power removal;
- independent immutable/versioned backup custody; or
- precious-data readiness.

ADR 0381 adds that live-Agent adapter in
`.sandwurm/exports/sync-production-prefix/run.HYXJnDzI`. This substrate receipt
remains useful because it cuts one synthetic mixed manifest/branch-record
prefix that the first production adapter does not yet cut internally.
