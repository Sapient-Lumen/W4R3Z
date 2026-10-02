# Durable command store v2

> Legacy format. Current IoTox verifies and atomically migrates this format to
> [`IOTXCMD3`](command-store-v3.md) before transport starts. This document preserves the original
> v2 contract; it is not the current write format.

**Code:** `include/iotox/command_store.hpp`, `src/command_store.cpp`  
**Magic:** `IOTXCMD2`  
**Purpose:** preserve exact IoTox command identity and evidence across process death/restart

## Constitutional properties

```text
private regular file owned by the current user
no symlink following on read
maximum 1,024 records and 8 MiB by implementation contract
persistent nonzero local sender epoch
stable-device Ed25519 signature over canonical header and body
strict canonical record order
exact request/receipt/result bytes retained
atomic temporary-file replacement, fsync, rename, directory fsync
```

The stable device identity signs the store. The Tox route identity does not. Tox savedata can rotate
without making the local command history unverifiable.

## Record locator

```text
direction
peer 32-byte Tox public key
sender epoch
message id
```

Direction distinguishes a remote command from a local command that happens to share the same
sender-defined epoch/message pair.

## Frozen fields

After insert, these fields cannot change:

```text
key and direction
operation
peer principal once nonzero
correlation/result ids once assigned
ownership epoch and authority sequence once assigned
creation time
canonical request
canonical receipt once assigned
canonical result once assigned
```

Lifecycle, delivery state, attempts, last send error, outcome, and updated time may change only
through validated monotonic transitions.

## Persistence transaction

Each mutation currently performs:

```text
copy current in-memory snapshot
validate insert/update and bounds
increment nonzero generation
canonicalize record order
encode header and records
sign canonical unsigned bytes
write private temporary file
fsync temporary file
rename over live file
fsync parent directory
publish candidate as in-memory state
refresh runtime projection
```

A failed write leaves the prior in-memory and on-disk snapshot authoritative.

## Load transaction

```text
open private regular file without following symlinks
check owner, mode, and maximum size
read complete bytes
validate magic/version/length/reserved fields/counts
verify stable-device public key and Ed25519 signature
strictly decode every record and canonical frame
reject duplicate locators and invalid transitions/fields
commit decoded snapshot to memory
```

A missing file creates generation 1 with a random nonzero sender epoch. An existing malformed,
foreign-signed, or non-private file fails closed.

## Capacity and pruning

Before inserting at the record ceiling, IoTox removes the oldest terminal record. It never prunes
an unfinished record to admit new work. If every record is nonterminal, insertion fails with
resource exhaustion.

This is a safety baseline, not a final retention policy. Per-peer quotas, priority, operator alerts,
terminal evidence classes, and archive/export remain open.

## Explicit limits

The signature proves integrity under the stable device key. It does not provide:

```text
confidentiality
whole-file rollback detection
hardware-backed monotonic generation
multi-process writer coordination
incremental append durability
low flash write amplification
remote consensus
backup or disaster recovery
```

A future format must be introduced with a new magic/version and migration ADR. It must not silently
reinterpret v2 bytes.
