# IoTox route binding v1

**Implemented:** canonical signed codec, bounded exchange frame, and transcript-derived verification

**Wire allocation:** IoTox message type 19, feature bit 21; the feature remains unadvertised until
the live worker exchange and replay registry are integrated

**Signer:** stable IoTox device identity

**Artifact size:** exactly 224 bytes

A route binding proves that one Tox public key is a current member of one authenticated route set
and that the proof was made for one exact, confirmed IoTox application session. It grants no
authority capability and cannot make an unconfirmed friendship schedulable.

## Canonical record

All integers are unsigned big-endian. Reserved bytes are zero.

| Offset | Size | Meaning |
|---:|---:|---|
| 0 | 8 | ASCII `IOTOXRB1` |
| 8 | 1 | format version, exactly `1` |
| 9 | 1 | route protocol version, exactly `1` |
| 10 | 1 | member role copied from the route set |
| 11 | 1 | connection class copied from the route set |
| 12 | 4 | zero |
| 16 | 8 | route-set generation |
| 24 | 32 | stable device Ed25519 public key |
| 56 | 32 | coordinator Tox public key |
| 88 | 32 | member Tox public key |
| 120 | 32 | canonical IoTox session transcript digest |
| 152 | 8 | zero |
| 160 | 64 | detached Ed25519 signature |

The signature message is ASCII `IOTOX-ROUTE-BINDING-SIGNATURE-V1` followed by the first 160 bytes.
The transcript digest is produced by the existing `iotox-session-transcript-v1` function over the
canonical two-HELLO/two-confirmation transcript. Callers cannot supply the digest directly.

## Admission rules

Creation requires a transcript-confirmed session whose local Tox key is the named member, the exact
role and connection class from the signed route set, the corresponding stable-device signer, and a
bilaterally negotiated route-binding-v1 feature bit.
Verification first authenticates the carried remote route set against the locally expected stable
principal and generation floor. It then requires a transcript-confirmed receiver view whose peer key
is the named member, exact principal/coordinator/generation/policy equality, the locally recomputed
transcript digest, and a valid stable-device signature.

Any stale generation, foreign principal, unknown member, policy substitution, different online
transcript, malformed key, nonzero reserved byte, or signature change fails closed. The raw
224-byte artifact alone does not authenticate distribution of the remote route set. The exchange
frame below carries that set and requires the receiver to anchor it to local trust input.

## Exchange frame

The application frame uses message type 19, sequence 5, and a nonzero message identifier. Flags,
correlation identifier, and expiry are exactly zero. Its payload is:

| Offset | Size | Meaning |
|---:|---:|---|
| 0 | 2 | unsigned big-endian signed route-set length |
| 2 | `N` | complete signed route-set-v1 artifact |
| `2+N` | 224 | route-binding-v1 artifact |

Because a signed route set contains 2..16 members, `N` is 252..924 and the complete payload is
478..1,150 bytes. This remains within the frozen 1,332-byte IoTox application payload ceiling. No
trailing bytes or alternative length encoding are accepted.

The receiver supplies the expected remote stable-device principal and minimum acceptable route-set
generation from local trusted association state; neither value may be learned from the received
payload. It first verifies the complete signed route set, then verifies the binding against that
exact set, the peer Tox key, and the locally reconstructed confirmed transcript. A self-consistent
foreign route set therefore remains foreign rather than becoming its own trust anchor.

## Primary association and replay

The coordinator-owned registry accepts trust only from a separate authority-authenticated primary
session. One record binds the expected stable principal to the exact primary peer Tox key that the
received route set must name as coordinator, a minimum generation, and that primary online epoch.
Trust removal withdraws worker admissions. A continuously trusted principal/coordinator pair keeps
the highest accepted generation and exact route set, rejecting rollback and same-generation forks.

One local worker incarnation may accept one binding in each auxiliary online epoch. Only an exact
retry of the same message identifier, route set, binding, worker, association, and epoch is
idempotent. A second distinct record conflicts; an older epoch or replacement worker is rejected
until the coordinator explicitly retires the prior incarnation. Registry bounds are 64 trusted
primary routes and 16 local workers by default.

## Current integration boundary

The worker supervisor has a construction-gated live send/receive path. Explicit Agent route-worker
construction installs the narrow signer and verifier, so only those auxiliary HELLOs advertise bit
21. Agent derives trust from a separately authority-authenticated primary session and advances a
member to `ready` only after local-send evidence plus reciprocal verification. Default and ordinary
single-route HELLOs remain unadvertised. The transport-neutral immutable-object scheduler may reserve
an exact ready bulk worker, but no network file transfer consumes that assignment yet.
