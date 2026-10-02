# IoTox private route binding v2

Status: live Agent/worker construction and generic-SOCKS mixed-context gate accepted behind
`--enable-private-route-bindings`.

Feature bit: 28, `private-route-binding-v2`; requires authority-ledger-v1 bit 16 and
route-binding-v1 bit 21.

Message types: 26 `private-route-inventory`, 27 `private-route-member-binding`.

## Purpose

Route-binding v1 puts a complete signed route set beside every auxiliary transcript proof. V2 keeps
that frozen format intact but separates disclosure from proof:

```text
authority-authenticated primary session
    -> complete stable-device-signed route inventory

exact auxiliary session already named by that private inventory
    -> one fixed member binding, not the route roster
```

This prevents an auxiliary Tox friendship from learning every native/privacy route merely by
completing HELLO. It does not hide the roster from a principal that the primary authority ledger
already authorizes.

## Primary inventory frame

The frame has message type 26, a nonzero message ID, sequence 6, and zero flags, correlation, and
expiry. Its payload is one unchanged route-set-v1 signed artifact (252..924 bytes). Before creating
or accepting the frame, the implementation requires:

- an application-confirmed primary session that negotiated bit 28;
- one live `PeerAuthoritySnapshot` with the same friend number, peer Tox key, online epoch, and
  independently recomputed transcript digest;
- `remote_authorized=true` and a nonzero remote stable principal;
- on send, the local primary Tox key equals the route-set coordinator and the artifact canonically
  verifies under the local stable device identity; or
- on receive, the artifact verifies under the authority-authenticated remote principal and names
  the exact primary peer Tox key as coordinator.

Admission retains the full route set, its `IoToxHash("iotox-route-set-artifact-v1", artifact)`
digest, and the primary friend/transport-key/online-epoch association. Replacing that primary
authority edge invalidates the admission. A friend number recycled for a different transport key is
a new association with independent epoch numbering.

## Auxiliary member artifact

The member artifact is exactly 256 bytes. All integers are unsigned big-endian; reserved bytes are
zero.

| Offset | Size | Meaning |
|---:|---:|---|
| 0 | 8 | ASCII `IOTOXRB2` |
| 8 | 1 | format version, exactly 2 |
| 9 | 1 | route protocol, exactly 1 |
| 10 | 1 | member role |
| 11 | 1 | member connection class |
| 12 | 4 | zero |
| 16 | 8 | route-set generation |
| 24 | 32 | stable device principal |
| 56 | 32 | coordinator Tox public key |
| 88 | 32 | this auxiliary member Tox public key |
| 120 | 32 | confirmed auxiliary-session transcript digest |
| 152 | 32 | complete signed route-set artifact digest |
| 184 | 8 | zero |
| 192 | 64 | stable-device Ed25519 signature |

The signature message is printable ASCII
`IOTOX-PRIVATE-ROUTE-MEMBER-BINDING-SIGNATURE-V2` followed by bytes 0..191. Binding the complete
artifact digest makes a same-generation route-set fork with different budgets, expiry, or other
members fail even though those fields are intentionally not disclosed on the auxiliary session.

The enclosing frame has message type 27, a nonzero message ID, sequence 7, and zero flags,
correlation, and expiry. Creation and verification both require the original primary authority edge
to remain live, the privately admitted remote inventory to retain that exact primary friend/epoch,
and the auxiliary peer key to be a member of that inventory. Verification additionally requires the
member key, role, connection class, generation, principal, coordinator, inventory digest, transcript
digest, and signature all to match.

## Live construction boundary

Bit 28 remains absent from the default feature mask. The Agent advertises it only with explicit
`--enable-private-route-bindings` after an authenticated route set and exact-key worker supervisor
have been constructed. V1 remains the default worker exchange and is byte-for-byte unchanged.

The gated Agent freezes one outbound primary frame per friend/online epoch and retains a bounded
inbound registry. The registry permits exact replay, rejects same-epoch conflict and observed
generation rollback/fork, retires usable inventory when the exact authority edge disappears, and
preserves process-lifetime generation/digest high-water. Only admitted inventory is passed to the
worker supervisor. V2 workers send no proof before that handoff, exchange only type 27, and clear
proofs, queued sync records, transfers, and coordinator readiness when the primary context is
withdrawn (ADR 0200). On replacement, one early reciprocal frame is retained only long enough to
be reverified against the new exact context. A valid frame closes the receive half of the exchange;
a stale frame gains no authority and is discarded so a fresh proof can arrive (ADR 0201).

The deterministic provider test crosses the whole Agent path and observes primary inventory before
member proof plus readiness withdrawal on primary friendship removal. The accepted two-guest
`sync-tree-route-private-mixed` gate additionally joins independent native and strict generic-SOCKS
worker contexts, reaches reciprocal readiness, and converges one signed tree. This is generic-SOCKS
evidence, not actual Tor (ADR 0201).

This is an authorization-scoped identifier-disclosure control, not anonymity. The primary peer and
the exact auxiliary peer can link the identities they are authorized to use; global observers may
still correlate traffic by other means.
