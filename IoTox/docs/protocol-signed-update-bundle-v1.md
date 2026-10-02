# Signed update bundle v1

Status: frozen construction contract; product activation remains default-off.

## Separation of authority

Tox and the synchronization service deliver immutable bytes. A verified sync HEAD proves which
configured writer published those bytes. Neither fact grants installation authority.

`signed-update-bundle-v1` adds a second, domain-separated Ed25519 signature from a release signer
explicitly pinned in owner-local update policy. The signature binds the exact sync namespace,
deployment target, release sequence, display version, payload kind, payload byte count, and payload
SHA-256. Remote `update.stage` additionally proves the existing `install.firmware` authority
capability, bilateral `signed-ota-v1`, and the exact current accepted HEAD through ADR 0186. Local
same-user staging is not a substitute for that remote proof, and remote staging is not apply or
health-confirmation authority.

Payload kind `1`, `opaque-slot-v1`, is an inert regular-file image. IoTox never executes, loads,
extracts, mounts, or interprets it while verifying or staging it. Payload kind `2`,
`linux-service-v1`, is executable intent for the separately gated sealed Linux service adapter.
Both kinds use the same verification and inert staging path; only kind 2 under matching policy v3
may cross the adapter boundary described in `update-linux-service-v1.md`.

## Canonical manifest

The bundle starts with a 320-byte signed manifest followed immediately by the payload. Its 256-byte
body is:

| Offset | Size | Meaning |
|---:|---:|---|
| 0 | 8 | ASCII `IOTOXUB1` |
| 8 | 1 | format version `1` |
| 9 | 1 | payload kind (`1` = `opaque-slot-v1`, `2` = `linux-service-v1`) |
| 10 | 6 | zero reserved bytes |
| 16 | 8 | nonzero release sequence, big-endian |
| 24 | 8 | nonzero payload bytes, big-endian |
| 32 | 32 | payload SHA-256 |
| 64 | 32 | release-signing Ed25519 public key |
| 96 | 64 | namespace: one length byte, bytes, then zero padding |
| 160 | 64 | target: one length byte, bytes, then zero padding |
| 224 | 32 | version: one length byte, bytes, then zero padding |

The body is followed by the 64-byte Ed25519 signature. The signature input is IoTox's canonical
domain hash `iotox-update-manifest-signature-v1` over the complete body. Namespace and target use the
same conservative lowercase identifier alphabet as sync namespace IDs and are at most 63 bytes.
Version is printable ASCII without leading/trailing whitespace and is at most 31 bytes. Padding is
canonical zero; unknown formats, kinds, reserved bytes, or noncanonical strings fail closed.

The complete bundle size must equal `320 + payload_bytes` exactly. Verification uses one no-follow
descriptor, hashes only the payload interval with SHA-256, and rejects replacement, growth,
truncation, link-count, ownership, permission, or metadata changes across the read. Output creation
is no-clobber and durable; an existing destination is never replaced.

## Owner-local update policy

Before network startup, a default-off update service loads owner-local policy containing:

- one exact sync namespace;
- one exact deployment target;
- one owner-private slot root;
- one or more pinned release-signing public keys;
- a maximum payload size and bounded health-confirmation interval.

Remote data cannot nominate its own trust root, target, path, quota, or health policy. A signer may
authorize code for the configured target, but it cannot change IoTox ownership, RecallRoot, the
authority ledger, or the device identity.

The policy record is UTF-8-compatible ASCII text, newline-terminated, NUL-free, at most 4096 bytes,
and decoded only when it re-encodes byte-identically. Version 1 is still emitted exactly when no
signer-policy epoch or revoked signer set is present:

```text
iotox-update-policy-v1
namespace=NAME
target=TARGET
root-hex=LOWERCASE_HEX_NORMALIZED_ABSOLUTE_NON_ROOT_PATH
maximum-payload-bytes=CANONICAL_DECIMAL
health-timeout-ms=CANONICAL_DECIMAL
signer=PUBLIC_KEY_HEX
...
```

Version 2 keeps the signed bundle manifest unchanged and adds explicit release-signer lifecycle
state to local policy:

```text
iotox-update-policy-v2
namespace=NAME
target=TARGET
root-hex=LOWERCASE_HEX_NORMALIZED_ABSOLUTE_NON_ROOT_PATH
maximum-payload-bytes=CANONICAL_DECIMAL
health-timeout-ms=CANONICAL_DECIMAL
signer-policy-epoch=POSITIVE_CANONICAL_DECIMAL
signer=ACTIVE_PUBLIC_KEY_HEX
...
revoked-signer=REVOKED_PUBLIC_KEY_HEX
...
```

Active release signers are sorted by raw public-key bytes, unique, nonzero, and bounded to eight.
Revoked release signers are sorted the same way, unique, nonzero, disjoint from the active set, and
bounded to thirty-two. Every active signer line precedes every revoked-signer line. A revoked list
without a positive signer-policy epoch is invalid. A v1 record cannot contain revoked signers.

Version 3 is the only policy that expresses executable service intent. It requires a positive signer
epoch and adds one canonical kind field before the signer lists:

```text
iotox-update-policy-v3
namespace=NAME
target=TARGET
root-hex=LOWERCASE_HEX_NORMALIZED_ABSOLUTE_NON_ROOT_PATH
maximum-payload-bytes=CANONICAL_DECIMAL
health-timeout-ms=CANONICAL_DECIMAL
signer-policy-epoch=POSITIVE_CANONICAL_DECIMAL
payload-kind=linux-service-v1
signer=ACTIVE_PUBLIC_KEY_HEX
...
revoked-signer=REVOKED_PUBLIC_KEY_HEX
...
```

Policy v1 and v2 always mean `opaque-slot-v1`; they cannot carry a payload-kind field. A policy-v3
bundle must carry manifest kind 2, and its stable-device-signed lifecycle state carries kind 2 as
well. Historical opaque state keeps the old reserved bytes at zero and retains its exact encoding
and signature. There is no state encoding that can reinterpret historical opaque kind 1 as an
executable service.

The revoked set is a local future-staging denial and audit boundary. It prevents a retired release key
from reappearing as active in the same policy epoch and makes a rotated policy reject future bundles
signed by that key. It does not retroactively reinterpret already staged or confirmed update state,
delete inactive slots or lower the confirmed sequence. Owner-local key authoring, public inspection,
reviewable epoch rotation, and backup/custody guidance are specified in `update-operations.md`; they
do not change this bundle format or create a hardware policy-epoch witness.

## Implemented construction slot lifecycle

The construction lifecycle is deliberately separate from ordinary sync activation:

1. `stage` joins an exact accepted sync HEAD to its immutable artifact, verifies the signed bundle,
   copies only its payload into a digest-named inactive private slot, rehashes it, and records a
   device-signed staged state.
2. `apply` commits a pending transition before atomically switching a derived `current` pointer. It
   returns a random health token and cannot confirm in the applying Agent incarnation.
3. The first later Agent incarnation verifies the pointer and both slots, records exactly one boot
   attempt, and opens a bounded health-confirmation window.
4. `confirm` requires that incarnation and the exact token. Only then does the candidate sequence
   become the anti-rollback high-water value.
5. An incomplete switch, a second restart, or an expired health window returns the pointer to the
   last confirmed slot before finalizing rollback state. Corrupt slots, invalid signed state, and
   invalid tokens fail closed; timeout/restart can roll back only while the signed state and confirmed
   target remain independently valid.

Startup recognizes both state-first apply interruption and pointer-first rollback interruption and
finishes the exact transition deterministically. The hot store retains at most eight immutable slots
and fails closed before pointer mutation when that bound is full. `update-gc dry-run|quarantine` may
move only slots not named by signed confirmed/candidate state into a bounded owner-private recovery
directory. Quarantine is resumable across partial moves and never unlinks bytes; no purge collector
exists.

A failed unconfirmed candidate may be retried because it never advances the confirmed high-water
sequence. Once confirmed, an older sequence cannot be staged or selected. Restoring old content
after confirmation requires republishing it under a new higher signed sequence; there is no command
that lowers the counter.

For a matching service policy, the later Agent incarnation additionally reopens the exact selected
slot, rehashes it into a sealed anonymous executable image, and requires the sequence-bound
`IOTOXSR1` readiness record from the live process before local confirmation can succeed. Candidate
exec failure, early exit, malformed readiness, or timeout invokes the same signed rollback and then
relaunches the confirmed service. This adds no remote apply, restart, helper selection, or health-
confirmation authority.

## Explicit nonclaims

This format is not a package manager, archive format, bootloader protocol, firmware transparency
log, hardware anti-rollback counter, secure-boot chain, or recovery partition. The named kind-2
adapter executes one native Linux service image but does not make the bundle a general executable
format. A device-state
attacker who can replay every complete valid policy and signed state record together is outside a
software-only monotonic guarantee. Physical target integration, power-cut testing, manager/cgroup
policy, flash wear, secure boot, hardware health semantics, and recovery media remain independent
qualification gates. Release-key custody and quarantine operations are specified owner-local
construction, not a bootable-target claim.
