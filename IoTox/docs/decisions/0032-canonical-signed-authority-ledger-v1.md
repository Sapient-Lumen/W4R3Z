# ADR 0032: Use a fixed signed append-only authority ledger v1

**Status:** accepted and implemented in rev0009; action set extended by ADR 0054

## Context

Tox friendship and even a mutually confirmed IoTox session do not answer who owns a device or
which operation a peer may perform. IoTox needs an independent durable constitution that is
small enough to encode canonically, replay deterministically, inspect locally, and fuzz/test
without introducing a general policy language.

IoT devices may boot without a trustworthy wall clock. Ordinary filesystems also cannot prove
that an attacker did not restore an older internally valid file.

## Decision

IoTox authority ledger v1 is a bounded sequence of fixed 256-byte records under a fixed 16-byte
file header. Each record has a 192-byte canonical body and 64-byte Ed25519 signature. It binds:

```text
action and role
strict sequence and ownership epoch
zeroed not-before/not-after fields
capability mask
stable device public key
issuer and subject public keys
previous signed-record BLAKE2b-256 digest
```

The original actions are bootstrap, grant, and revoke. ADR 0054 adds the fail-closed action value 4
for an ownership-epoch transition without changing the fixed record envelope. Roles are none,
owner, administrator, operator,
viewer, automation, and service. Capabilities are seven fixed bits: read telemetry, write
settings, actuate, manage principals, install firmware, export diagnostics, and factory reset.
Unknown values and bits fail closed.

The first record is a self-signed owner bootstrap at sequence and epoch one with all
capabilities. Later records advance sequence exactly once and name the current tail digest.
Issuers must be active and possess `manage.principals`; grants cannot exceed issuer capability
or the role ceiling; only an owner can grant owner; the last active owner cannot be revoked.

The daemon prepares the next exact body from current state. A client signs it. The daemon
verifies the signature, replays the candidate complete history, writes it atomically, then
publishes the new snapshot. Time fields remain zero until a trusted-clock policy is accepted.

## Consequences

Authority is independent from Tox friend state and can survive Tox endpoint rotation. The
format is compact, deterministic, inspectable, and difficult to reinterpret accidentally.

The whole bounded file is atomically replaced rather than incrementally appended; this favors
power-loss consistency and simple replay at current research scale. Compaction, very large
histories, quorum/multi-signature records, temporary validity, and destructive physical reclaim
require a new explicit format or superseding decision. ADR 0054 extends the existing envelope with
a successor-possession ownership transition.

Digest chaining detects corruption and record reordering but not malicious rollback to an
older complete valid ledger. Strong rollback resistance remains unsolved without an additional
monotonic or externally witnessed mechanism.
