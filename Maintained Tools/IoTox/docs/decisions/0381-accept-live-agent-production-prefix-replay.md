# ADR 0381: Accept live-Agent sync production transaction-prefix replay

Status: accepted and implemented
Date: 2026-09-17

## Context

ADR 0380 accepted exact `dm-log-writes` prefix replay for content-free
IoTox-shaped sync records. That proved the block-log replay substrate, but it
did not yet run the real Agent, real `sync-create`, real `sync-publish`, or
the actual tree-v2 namespace layout that ordinary users exercise.

The next honest frontier was therefore not another synthetic record family. It
was a production adapter that could put the Agent's durable sync state on a
logged block device, mark a transaction boundary after a real command
completed, replay that exact block prefix, and compare the cold replayed state
to the state observed at the boundary.

## Decision

Add a same-host production-prefix replay gate:

- `tools/run-sync-production-prefix-replay.py`;
- `tools/verify-sync-production-prefix-replay.py`;
- `tools/iotox-repo.sh sync-production-prefix-replay`;
- storage-readiness integration; and
- non-privileged CTest self-tests for runner and verifier.

The runner starts a real IoTox Agent with sync enabled and the mock toxcore
provider. It places the durable Agent state, source directory, and sync-policy
root on an ext4 or btrfs filesystem backed by `dm-log-writes`, then runs:

1. RecallRoot authority bootstrap and v3 grant for the fixture owner;
2. `sync-create prodprefix SOURCE read-write 86400`;
3. `sync-repair prodprefix`, then mark `sync-create-generation-1`;
4. a fixture source mutation;
5. `sync-publish prodprefix SOURCE`;
6. `sync-repair prodprefix`, then mark `sync-publish-generation-2`; and
7. exact block-prefix replay of both marks with the `xfstests` `replay-log`
   helper.

Each replay is cold-mounted read-only and compared to the content-free
inventory observed at the transaction mark. The generation-1 prefix is older
than the acknowledged generation-2 floor and is treated as a refused mutation.
The generation-2 prefix must equal the acknowledged current state.

`tools/qualify-storage-readiness.py` now accepts local storage science only
when all three same-host layers verify:

1. ext4+btrfs dishonest-storage matrix;
2. ext4+btrfs synthetic `dm-log-writes` marked-prefix replay; and
3. ext4+btrfs live-Agent production transaction-prefix replay.

## Consequences

The live-Agent production prefix gate closes the largest same-host storage
science gap. IoTox now has evidence that real sync namespace creation and
publication can be replayed from exact block-log prefixes on both ext4 and
btrfs.

This still does not make IoTox sync backup-grade. The accepted gate is a
transaction-boundary proof, not exhaustive internal interleaving coverage for
every rename/fsync inside `sync-create` or `sync-publish`. It is also still a
same-host sparse-image proof. Storage-media behavior, controller behavior, physical power
removal, and independent immutable/versioned backup custody remain separate
gates. `storage-readiness` therefore still reports `status=not-ready` and
`ready_for_precious_data=false`.

## Evidence

Committed-source run `run.HYXJnDzI` passes:

```text
source revision:         ae4ed0a44f5dbe747f095fbe6a5f98eac46928a6
receipt:                 .sandwurm/exports/sync-production-prefix/run.HYXJnDzI/production-prefix-replay.json
receipt-sha256:          a67552c99f59b55418774b14199d486f42872b2daf11bace44d58a6341910593
verification:            .sandwurm/exports/sync-production-prefix/run.HYXJnDzI/production-prefix-replay-verification.json
verification-sha256:     5320ab9b83c05f80b457babb75879eb85f2ed346bbbed34bc4c7f183ed8ffebc
filesystems:             ext4, btrfs
marks:                   sync-create-generation-1, sync-publish-generation-2
contains-secrets:        false
raw-retained:            false
```

See `../evidence/2026-09-17-sync-production-prefix-replay.md`.
