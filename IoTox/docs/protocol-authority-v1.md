# IoTox directional authority session v1

**Implemented:** rev0009
**Prerequisite:** mutually confirmed capability-session-v1
**Feature bit:** `authorization-ledger-v1`
**Compatibility status:** canonical for unmigrated ledgers and the v1 prefix of one valid v2 history
**Messages:** `AUTHORITY_CHALLENGE` (17), `AUTHORITY_PROOF` (18)

This exchange authenticates an IoTox application principal for one direction of one confirmed
Tox online epoch. It does not replace Tox transport authentication and does not make friendship
an authorization grant.

Authority-ledger v2 does not rewrite or reinterpret this format. New binaries retain exact v1 read
support; one signed `migrate-v2` record starts the successor domain described in
`protocol-authority-v2.md`. Plain `all` and every v1 capability ceiling remain bits 0–6.

## Directionality

Each endpoint independently acts as:

```text
verifier: sends a challenge against its local ledger head and decides the peer principal
claimant: answers the peer challenge with a selected stable principal
```

One direction may be authorized while the opposite direction remains unproven. A stable device
principal is automatically available to answer challenges. A recalled owner or delegated
controller remains an explicit claimant path.

## Transcript digest

The session digest is BLAKE2b-256 under domain:

```text
iotox-session-transcript-v1
```

Its input is the exact canonical confirmed-session transcript containing ordered Tox endpoint
keys, both HELLO records/nonces, negotiated protocol/features/limits, and confirmation IDs.

## AUTHORITY_CHALLENGE

Outer frame:

```text
type=17
sequence=3
correlation-id=0
expiry=0
payload=160 bytes
protocol=exact negotiated version
```

Payload, unsigned big-endian integers:

| Offset | Size | Field |
|---:|---:|---|
| 0 | 4 | `IAC1` |
| 4 | 1 | format `1` |
| 5 | 3 | zero |
| 8 | 32 | verifier stable device principal |
| 40 | 8 | ownership epoch |
| 48 | 8 | authority ledger sequence |
| 56 | 32 | authority ledger tail digest |
| 88 | 32 | confirmed-session transcript digest |
| 120 | 32 | fresh nonzero challenge nonce |
| 152 | 8 | zero |

The challenge freezes the verifier's exact authority head and online-epoch transcript. A ledger
mutation invalidates outstanding remote authorization and requires a new challenge.

## AUTHORITY_PROOF

Outer frame:

```text
type=18
sequence=4
correlation-id=challenge outer message ID
expiry=0
payload=256 bytes
protocol=exact negotiated version
```

The first 192 bytes are the signed body:

| Offset | Size | Field |
|---:|---:|---|
| 0 | 4 | `IAP1` |
| 4 | 1 | format `1` |
| 5 | 3 | zero |
| 8 | 32 | verifier stable device principal |
| 40 | 32 | claimant stable principal |
| 72 | 8 | ownership epoch |
| 80 | 8 | authority ledger sequence |
| 88 | 32 | authority ledger tail digest |
| 120 | 32 | confirmed-session transcript digest |
| 152 | 32 | challenge nonce |
| 184 | 8 | challenge outer message ID |
| 192 | 64 | Ed25519 signature |

The signature envelope is:

```text
"IOTOXS1"
2-byte domain length
domain = "iotox-authority-session-proof-v1"
exact 192-byte proof body
```

The verifier checks exact challenge equality, signature under the claimant public key, current
ledger head equality, and active-principal membership. It copies the current role/capabilities
from the local replayed ledger; the peer does not self-assert them.

## Frozen records and retry

The first structurally valid challenge/proof for one authority head in an online epoch is frozen.
Byte-identical repetition is idempotent; changed bytes at the same or an older head are conflict.
A challenge from the same verifier device and session may replace an unfinished round only when its
`(ownership epoch, sequence)` is strictly newer and its ledger format does not downgrade. This
prevents two rapid legitimate ledger mutations from deadlocking the claimant while retaining exact
same-head conflict detection. If c-toxcore rejects a local enqueue with `SENDQ` or temporary
disconnection, IoTox retries the exact reserved frame. Once toxcore accepts it, this layer does not
blindly resend.

A local ledger append invalidates its frozen challenge immediately. A proof already queued for that
old exact head is rejected as unavailable but is not frozen and does not move the verifier to
`malformed-proof`; the verifier remains `challenge-ready`, sends a fresh nonce/message-id/head
challenge, and accepts only a proof for that replacement. This closes the bootstrap-then-grant race
without allowing an old proof to authorize a new ledger head or weakening changed-proof conflict.

`proof-sent` means local toxcore queue acceptance only. v1 has no proof-verification receipt.

## Application decision

An operation is admitted only when:

```text
session transcript is confirmed
authorization-ledger-v1 was negotiated
the peer answered the current local challenge
proof signature and every bound field match
the claimant is active in the current local ledger
the claimant's current capabilities include the operation requirement
```

rev0009 admits only `device.describe`, requiring `read.telemetry`. See
`protocol-command-v1.md`.

## Nonclaims

Authority-session-v1 does not by itself provide durable command receipts, trusted-clock expiry,
application replay windows beyond the frozen handshake records, filesystem rollback detection,
route binding, destructive physical reclaim, or safe physical actuation. Ownership-epoch mutation
is the separately signed ledger ceremony in ADR 0054.
