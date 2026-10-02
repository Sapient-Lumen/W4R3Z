# ADR 0378: Accept the first dm-snapshot dishonest-storage drill

Status: accepted and implemented
Date: 2026-09-17

## Context

IoTox already has same-host KVM/ext4 evidence for honest filesystems, bounded
whole-VMM power cuts, abrupt Agent death, ENOSPC, read-only startup refusal,
metadata corruption refusal, valid-old witness refusal above the filesystem,
and retained recovery drills. Those gates do not prove that storage below ext4
honors `fsync`, barriers, flushes, or read-after-write truth.

The dishonest-storage frontier needs a harness below the filesystem. A
syscall-level shim is useful for early development, but it cannot support a
durability claim because it sits above the kernel filesystem and block layers.

## Decision

Add a first repository-native dishonest-storage drill:

- `tools/run-sync-dishonest-storage-drill.py`;
- `tools/verify-sync-dishonest-storage-drill.py`;
- `tools/iotox-repo.sh sync-dishonest-storage-drill`;
- non-privileged CTest self-tests for the runner and verifier; and
- workspace cleanup support for `.sandwurm/lab/sync-dishonest-storage/run.*`
  and `.sandwurm/exports/sync-dishonest-storage/run.*`.

The drill uses a real `device-mapper` snapshot target beneath ext4. Generation
1 is written to an origin image. Generation 2 is written through the snapshot
COW, fsynced, synced, and read back. The COW is then discarded, modeling
storage that acknowledged a durable write but later returned the older valid
origin. A cold read-only `noload` mount observes generation 1 while the
content-free external witness floor remembers generation 2. The verifier
accepts only if rollback is detected and mutation is refused.

The first receipt covers three IoTox-shaped state families together:

- branch pointer;
- workspace; and
- maintenance.

## Consequences

This is a real block-layer test, so it is a stronger first dishonest-storage
gate than a process kill or filesystem mock. It is still not a full production
storage qualification. It does not yet replay exact production tree-v2 writes
from three live Agents, does not enumerate every write/flush prefix, and does
not test torn content, masked I/O errors, or storage-media firmware.

The receipt grammar deliberately keeps nonclaims in the machine-verifiable
record. A pass means “this exact acknowledged-write rollback was detected and
refused,” not “all disks are safe.”

The next cells should extend this shape to `dm-log-writes`, `dm-flakey`,
NBD/virtio block proxies, or Sandwurm guest disks so the harness can replay
selected production prefixes and cross-family mixtures.

## Evidence

Committed-source run `run.UbmYPe1X` passes:

```text
source revision:           59a00cdca6c69c53bde6bb01463c4544a2a98731
receipt:                   .sandwurm/exports/sync-dishonest-storage/run.UbmYPe1X/receipt.json
receipt-sha256:            d2a72f7f2d1d5511bd2e3d0f44b73c0d0196e7342489319dee25a39a84b01dc0
verification-sha256:       16d6986300a66df3ba21ad2c0fce05a771cbc46fe18ab19be86c7b087a2f94bb
base generation:           1
acknowledged generation:   2
cold generation:           1
external witness floor:    2
rollback detected:         true
mutation refused:          true
contains secrets:          false
raw retained:              false
```

See `../evidence/2026-09-17-sync-dishonest-storage.md`.
