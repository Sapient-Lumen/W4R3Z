# Witness service checkpoint v1

Status: checkpoint format frozen by ADR 0313 on 2026-09-02; custody report added by ADR 0360 on 2026-09-10.

This format is a signed, selector-complete snapshot of one IoTox rollback-witness service store.
It is public authenticity material, not a secret. It becomes a rollback floor only when an operator
retains the exact artifact outside the service store's rollback/failure domain and supplies that
trusted copy on a later service start.

## Encoding

All integers are unsigned big-endian. The total size is:

```text
64 + record-count * 184 + 64 bytes
```

`record-count` is in `1..4096`.

```text
offset  bytes  meaning
0       8      ASCII IOTXWCP1
8       1      format version = 1
9       7      zero
16      32     witness-service Ed25519 public key
48      8      record-count
56      8      zero
64      184*N  canonical witness wire records
...     64     Ed25519 signature over every preceding byte
```

Records use the frozen `IOTXWR1` wire-record encoding. They are strictly sorted by domain, device
public key, witness epoch, then numeric lane. Duplicate selectors are invalid. Both committed and
pending records are preserved exactly, including the transaction nonce.

Verification requires an independently obtained expected service public key. Trusting only the key
embedded in the artifact would authenticate nothing.

## Startup-floor relation

Every selector in the checkpoint must still exist in the live store. Extra records enrolled after
the checkpoint are permitted because enrollment is no-replace and append-only.

For a checkpoint record with no pending transition, the live committed position must be greater
than the floor, or equal with the exact same digest. A live pending successor above that committed
head is allowed.

For a checkpoint record with a pending transition, either the live record must be that exact
pending record or its committed head must be at or beyond the pending successor. At the successor's
exact position, the digest must match. A predecessor, same-position fork, missing selector, invalid
record signature, malformed filename, or corrupt record refuses before the TCP listener binds.

Positions are one-step monotonic inside each closed selector. A greater position is therefore a
later service state under the service's exclusive-store and exact-CAS assumptions. A checkpoint is
not a live lease and does not prove that the service identity/store was never cloned and forked.

## Operator commands

With the service stopped so the CLI can acquire its exclusive store lock:

```sh
iotox witness-service-checkpoint \
  /var/lib/iotox-witness \
  /var/lib/iotox-witness/service.identity \
  /independent/checkpoints/iotox-witness.checkpoint

iotox witness-service-checkpoint-verify \
  /independent/checkpoints/iotox-witness.checkpoint \
  PINNED_WITNESS_ED25519_PUBLIC_KEY_HEX

iotox witness-service-checkpoint-custody \
  /var/lib/iotox-witness \
  /independent/checkpoints/iotox-witness.checkpoint \
  PINNED_WITNESS_ED25519_PUBLIC_KEY_HEX \
  custody-system=restic \
  custody-generation=witness-checkpoint-2026-09-10 \
  custody-failure-domain=external-usb-disk

iotox witness-service-serve \
  /var/lib/iotox-witness \
  /var/lib/iotox-witness/service.identity \
  0.0.0.0 37177 \
  /independent/checkpoints/iotox-witness.checkpoint
```

The output path must be outside the service root. `witness-service-checkpoint-custody` separately
requires an existing checkpoint outside the canonical service root, reads it as one bounded
no-follow stable regular file, verifies the signature against the pinned key, reports
`checkpoint-root-devices-differ=0|1`, and emits optional custody labels as hex. Export after
enrollment and after important advancement, transfer the artifact to independently controlled
append-only, versioned, or rollback-resistant storage, verify it there against the pinned key, and
keep prior versions. An artifact stored only beside the service records is an integrity snapshot,
not an independent freshness anchor.

## Nonclaims

The checkpoint does not:

- hide device selectors, lane positions, digests, or pending-transition timing;
- automatically transport, rotate, retain, or choose a trusted checkpoint;
- prove operational independence merely because custody labels were supplied;
- make the service's signing key rollback-resistant;
- detect coordinated rollback of the service and the only trusted checkpoint copy;
- provide a continuously renewed clone-fencing lease;
- authorize witness-key replacement, epoch re-anchor, or emergency loss recovery; or
- establish operational independence merely because a path argument was supplied.
