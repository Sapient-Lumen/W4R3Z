# ADR 0313: Add complete witness-service checkpoint floors

- Status: accepted and implemented for explicit operator-retained floors
- Date: 2026-09-02

## Context

ADR 0305 gave the separately runnable witness service signed crash-atomic records, a dedicated
identity, exclusive store ownership, and exact authenticated CAS. Each record is independently
authentic, but the store previously made no signed statement about its complete selector population.
Restoring or omitting old valid service files could therefore defeat Agent-side freshness if the
service's whole storage domain rolled back.

The service cannot honestly infer that a local filesystem, backup, or path is independently
administered. It can, however, emit a portable exact checkpoint and refuse to start below a trusted
copy supplied by the operator. This supplies the protocol needed for independently checkpointed
persistence without relabeling a same-host copy as independence.

## Decision

Freeze `IOTXWCP1`, a bounded service-signed checkpoint over the pinned witness public key and the
complete strictly sorted set of up to 4,096 canonical wire records. The checkpoint retains every
selector, committed head, and optional pending successor/nonce exactly. Verification requires an
out-of-band expected service public key.

Add three operator surfaces:

```text
witness-service-checkpoint ROOT SERVICE_IDENTITY OUTPUT
witness-service-checkpoint-verify CHECKPOINT SERVICE_PUBLIC_KEY_HEX
witness-service-serve ROOT SERVICE_IDENTITY HOST PORT [CHECKPOINT_FLOOR]
```

Checkpoint creation acquires the same exclusive process lock as service operation, validates every
`.witness` file's private regular-file metadata, service signature, canonical record, and filename,
then atomically writes the signed artifact outside the service root. A service start always scans every current record before
binding. When a floor is supplied, every checkpoint selector must exist and the live state must be
an exact or later state:

- a committed floor accepts the same `(position,digest)` or a greater position;
- a pending floor accepts that exact pending record or a committed state at/after its exact
  successor, with matching digest at the successor position; and
- absence, a predecessor, same-position fork, wrong key, malformed population, or corruption
  refuses before the listener exists.

Later no-replace enrollments may appear beyond an older floor. Operators should export after
enrollment and important transitions, retain version history outside the service failure domain,
and make the selected trusted artifact part of the service-manager start command. The format and
comparison rules are specified in `docs/protocol-witness-service-checkpoint-v1.md`.

## Consequences

Four owned checks bring the direct registry to 804. They cover deterministic complete-population
signing, strict ordering, pinned-key and byte-tamper refusal, acceptance of legitimate forward
progress, selective old-record rollback, missing enrollment, and exact pending-to-committed floor
semantics. The retained two-guest gate uses the real CLI to export and offline-verify ten
records, starts with that floor, later exports an advanced floor, rejects a selectively restored old
authority service record before bind, restores the exact current record, and restarts.

This makes independently checkpointed persistence executable, not automatic. A checkpoint held on
the same disk/admin/snapshot domain is not independent; coordinated rollback of both store and
trusted floor still succeeds. Greater positions rely on the exclusive-store/exact-CAS invariant and
do not prove that an administrator never cloned the signing identity into divergent services. This
ADR does not implement a continuous lease, hardware monotonic counter, witness-key replacement,
epoch handoff, emergency re-anchor, or owner-authorized loss ceremony.
