# Dishonest storage plan

Status: ext4+btrfs same-host dishonest-storage matrix, synthetic
`dm-log-writes` prefix replay, and live-Agent production transaction-prefix
replay accepted; versioned recovery custody and precious-data
readiness open.
Updated 2026-09-25.

IoTox has strong same-host KVM/ext4 evidence for honest filesystems, abrupt Agent death, bounded
whole-VMM cuts, ENOSPC, read-only startup refusal, metadata corruption refusal, and retained recovery
drills. Those gates assume the kernel and block stack tell the truth about writes, reads, barriers,
and `fsync`. Dishonest storage is the next boundary: a device, filesystem layer, virtual block
adapter, firmware, or remote volume may acknowledge durability and later return an older, torn, or
cross-file-inconsistent state.

## Threats to model first

Start with storage behaviors that can produce an apparently valid filesystem while violating IoTox's
durability assumptions:

1. **Lying flush:** write and `fsync` return success, but the medium later drops the write.
2. **Reordered durability:** later metadata reaches stable storage while an earlier required data or
   directory update is missing.
3. **Valid-old rollback:** a signed branch pointer, workspace record, maintenance record, policy, or
   witness checkpoint reappears as an older but individually valid value.
4. **Cross-family rollback:** one family advances while another related family rolls back, creating a
   mixed but locally parseable state.
5. **Torn file content:** a durable record contains a prefix, suffix, or block splice that still has
   valid filesystem metadata.
6. **Read lies after write:** immediate reread succeeds, but cold restart returns different bytes.
7. **Error masking:** `ENOSPC`, I/O error, or flush failure is acknowledged as success.

## Harness shape

The gate needs a storage interposer below IoTox and above an ordinary filesystem. Timing-only
process kills are not enough. The useful harness records a write/flush ledger, chooses an exact cut
or lie, boots a fresh kernel against the resulting image, and verifies the cold state before any
Agent repair can paper over the failure.

Viable implementations, in increasing ambition:

- **Device-mapper/logged block lane:** use `dm-log-writes`, `dm-flakey`, `dm-error`, or a small
  device-mapper stack in a Sandwurm guest to replay selected prefixes and inject failed flushes.
- **NBD/Virtio block proxy:** put a tiny block protocol proxy between Cloud Hypervisor and the disk
  image so flush/FUA/barrier lies are explicit and content-free receipts can name the selected lie.
- **Filesystem-level syscall interposer:** useful for early development, but not sufficient for a
  final dishonest-storage claim because it sits above the kernel/filesystem durability model.

The first accepted gate should prefer the smallest block-level path that can say:

```text
selected operation family
selected write/flush boundary
acknowledged durability result seen by IoTox
actual replayed durable prefix
cold-start verifier result
repair/refusal result
contains_secrets=false
```

## Accepted first gate

ADR 0378 adds `tools/iotox-repo.sh sync-dishonest-storage-drill` and the strict
`tools/verify-sync-dishonest-storage-drill.py` receipt verifier. The first
accepted run, `.sandwurm/exports/sync-dishonest-storage/run.UbmYPe1X`, uses a
real device-mapper snapshot beneath ext4:

1. write generation 1 to an ext4 origin image;
2. mount a snapshot COW over that origin;
3. write, fsync, sync, and read back generation 2 through the snapshot;
4. discard the COW, simulating storage that acknowledged durability but later
   returned the older valid origin; and
5. cold-remount the origin read-only with `noload`, detect generation 1 below
   the external generation-2 floor, and refuse mutation.

That closes one substrate cell for branch-pointer, workspace, and maintenance
shaped records. It is not a full production tree-v2 write replay, not storage
media certification, and not precious-data readiness. The value is the
repeatable block-level shape and the retained content-free receipt grammar.

## Accepted matrix gate

ADR 0379 adds `tools/iotox-repo.sh sync-dishonest-storage-matrix` and
`tools/verify-sync-dishonest-storage-matrix.py`. Source-linked run
`.sandwurm/exports/sync-dishonest-storage/run.qGwEvF17` passes eight cells:
ext4 and btrfs each cover valid-old rollback, cross-family rollback, a torn
manifest record, and `dm-flakey drop_writes` masked write loss.

The matrix expands the content-free families to branch pointer, immutable
branch record, manifest, workspace, maintenance, and projection marker. It is
still same-host sparse-image evidence. It does not replay exact production
Agent writes, prove hardware/firmware honesty, create recovery custody, or make
synchronization precious-data-ready.

## Accepted prefix-replay substrate gate

ADR 0380 adds `tools/iotox-repo.sh sync-log-writes-prefix-replay`,
`tools/verify-sync-log-writes-prefix-replay.py`, and
`tools/iotox-repo.sh storage-readiness`. Source-linked run
`.sandwurm/exports/sync-log-writes-prefix/run.90LCC7ra` passes ext4 and btrfs
`dm-log-writes` marked-prefix replay.

Each filesystem is created on a `dm-log-writes` device. The runner writes
content-free IoTox-shaped records, marks three block-log boundaries, replays
each exact prefix onto a fresh image with `replay-log`, cold-mounts it, and
verifies:

- `generation-1-stable` replays the older valid state and refuses mutation
  against the acknowledged generation-2 floor;
- `manifest-record-prefix` replays immutable manifest/branch-record generation
  2 beside mutable generation-1 state and refuses mutation; and
- `generation-2-stable` replays the complete acknowledged state and accepts it
  as current.

This closes the first exact block-prefix replay substrate for ext4 and btrfs,
but it is still synthetic: it proves the block-log replay mechanism with
IoTox-shaped records rather than a running Agent namespace.

## Accepted live-Agent production-prefix gate

ADR 0381 adds `tools/iotox-repo.sh sync-production-prefix-replay` and
`tools/verify-sync-production-prefix-replay.py`. Committed-source run
`.sandwurm/exports/sync-production-prefix/run.HYXJnDzI` passes ext4 and btrfs
live-Agent transaction-prefix replay.

Each filesystem is created on a `dm-log-writes` device. The runner starts the
real Agent with sync enabled and the mock toxcore provider, puts durable Agent
state plus source and sync-policy roots on the logged filesystem, performs the
RecallRoot authority bootstrap, runs real `sync-create`, `sync-publish`, and
`sync-repair`, then marks and replays:

- `sync-create-generation-1`, which cold-replays a valid older production
  namespace below the acknowledged generation-2 floor; and
- `sync-publish-generation-2`, which cold-replays the accepted current
  namespace.

This closes the first live-Agent production transaction-prefix replay gate. It
does not exhaust every internal subtransaction interleaving inside
`sync-create` or `sync-publish`, and it is still same-host sparse-image
evidence.

`tools/iotox-repo.sh storage-readiness` is now the executable truth boundary.
It accepts local storage science only when ADR 0379, ADR 0380, and ADR 0381
proofs verify, then still reports precious-data readiness as blocked until
versioned recovery custody has accepted receipts.
The gate definitions live in `storage-readiness-gates.md`.

## Acceptance rules

For every dishonest-storage cell, IoTox must either preserve a permitted old-or-new state or refuse
mutation until exact operator restoration. It must not:

- accept a valid-old rollback as current when a witness/checkpoint floor forbids it;
- synthesize a mixed workspace/branch/manifest/policy state;
- delete corrupt-but-needed evidence before the operator can restore it;
- advance writer membership, authority, terminal policy, or sync policy from an unauthenticated
  rollback; or
- convert a storage lie into silent data loss, conflict erasure, or backup confidence.

## First cells to build

1. Branch pointer valid-old rollback after a newer checkpoint has been observed.
   ADR 0378 accepts the first same-host dm-snapshot substrate version.
2. Workspace record valid-old rollback with current branch records still present.
   ADR 0378 accepts the first same-host dm-snapshot substrate version.
3. Manifest/branch-record cross-family rollback.
   ADR 0379 accepts the first ext4+btrfs substrate version.
4. Projection marker rollback after completed projection exposure.
5. Maintenance/retired-writer record rollback.
   ADR 0378 accepts the first same-host dm-snapshot substrate version.
6. Recovery drill restore from a selected generation whose storage later returns a different valid
   old tree.

Additional substrate cells now accepted by ADR 0379:

- torn manifest record beside older valid state; and
- masked write loss via `dm-flakey drop_writes`.

The pass condition is not “IoTox survives every lie.” The pass condition is narrower and more
valuable: the product detects the lie or preserves a safe old-or-new state, emits content-free
evidence, and refuses to turn dishonest storage into a false backup or freshness claim.
