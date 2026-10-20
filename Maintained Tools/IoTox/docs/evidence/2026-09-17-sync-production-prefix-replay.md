# Sync live-Agent production prefix replay — 2026-09-17

Status: accepted same-host ext4+btrfs live-Agent production transaction-prefix
replay; not full internal subtransaction coverage, storage-media certification,
independent backup custody, or precious-data readiness.

## Commands

```sh
tools/iotox-repo.sh sync-production-prefix-replay \
  --origin-size-mib 512 \
  --log-size-mib 2048
python3 tools/verify-sync-production-prefix-replay.py \
  .sandwurm/exports/sync-production-prefix/run.HYXJnDzI
tools/iotox-repo.sh storage-readiness
```

## Accepted receipt

```text
run-id:                  run.HYXJnDzI
source revision:         ae4ed0a44f5dbe747f095fbe6a5f98eac46928a6
receipt:                 .sandwurm/exports/sync-production-prefix/run.HYXJnDzI/production-prefix-replay.json
receipt-sha256:          a67552c99f59b55418774b14199d486f42872b2daf11bace44d58a6341910593
verification:            .sandwurm/exports/sync-production-prefix/run.HYXJnDzI/production-prefix-replay-verification.json
verification-sha256:     5320ab9b83c05f80b457babb75879eb85f2ed346bbbed34bc4c7f183ed8ffebc
iotox-binary-sha256:     46663e8a1c360a5dd7b20eb4bc846a49ff46655edbb338b6d7646a86c63ee5a5
toxcore-provider-sha256: a72ad37f7448905b22959e17824ee297ddb1e70b88558c200bdf68be4da65457
replay-tool:             /nix/store/z6ms9cm3ksrlivk1a4a05is9hqgadkym-xfstests-2026.07.21/lib/xfstests/src/log-writes/replay-log
replay-tool-sha256:      ecec252bdc66235440f6e6d1eadc94cd11b6905b027d32f08537fbc162eac28e
cell-count:              2
filesystems:             ext4, btrfs
marks:                   sync-create-generation-1, sync-publish-generation-2
contains-secrets:        false
raw-retained:            false
```

The compact evidence consists of:

```text
production-prefix-replay.json                  16,087 bytes
production-prefix-replay-summary.json             932 bytes
production-prefix-replay-verification.json        298 bytes
```

The raw sparse images, log images, replay images, mount directories, runtime
directories, loop devices, and device-mapper nodes were removed after the
receipt was written.

## Cells

| Filesystem | Mark | Replay entry | Production command boundary | Replay result |
| --- | --- | ---: | --- | --- |
| ext4 | `sync-create-generation-1` | 828 | real Agent `sync-create prodprefix SOURCE read-write 86400`, then `sync-repair` verifies generation 1 | older than acknowledged generation-2 floor; mutation refused by the external floor rule |
| ext4 | `sync-publish-generation-2` | 1031 | real Agent `sync-publish prodprefix SOURCE`, then `sync-repair` verifies generation 2 | accepted as the acknowledged current floor |
| btrfs | `sync-create-generation-1` | 913 | real Agent `sync-create prodprefix SOURCE read-write 86400`, then `sync-repair` verifies generation 1 | older than acknowledged generation-2 floor; mutation refused by the external floor rule |
| btrfs | `sync-publish-generation-2` | 1076 | real Agent `sync-publish prodprefix SOURCE`, then `sync-repair` verifies generation 2 | accepted as the acknowledged current floor |

The generation-1 repair selected one object and 5 bytes. The generation-2
repair selected one current object and 13 bytes while retaining two manifests,
two immutable branch records, and two CAS objects in the namespace inventory.

## Boundary

This is the first proof that wraps actual IoTox sync production code rather
than synthetic IoTox-shaped records. The runner starts the production Agent
with sync enabled and a mock toxcore provider, places the durable Agent state,
source directory, and sync-policy root on a `dm-log-writes` filesystem, runs
ordinary local-control commands, marks exact block-log prefixes, and replays
those prefixes onto fresh images.

It still does not prove:

- every internal subtransaction interleaving inside `sync-create` or
  `sync-publish`;
- storage-media honesty, firmware behavior, or controller cache behavior;
- physical power removal;
- independent immutable/versioned backup custody; or
- precious-data readiness.

The next storage frontier is no longer a same-host synthetic prefix. It is
independent backup custody, with optional deeper internal
production subtransaction cuts if a future bug demands that precision.
