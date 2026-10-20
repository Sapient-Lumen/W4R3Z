# ADR 0048 — Friendship mutations are public-key-bound exact-token decisions

- Status: accepted
- Revision: rev0014
- Date: 2026-08-14
- Extends ADR 0022 and ADR 0027
- Supersedes the removal portion of ADR 0022 where a public command could still become a delayed numeric mutation

## Context

c-toxcore exposes a process-local `Tox_Friend_Number`, but its public contract says gaps may be
filled by later additions, patterns must not be relied upon, and numbers may differ after savedata is
reloaded. A friend number is useful evidence inside one lifecycle; it is not the durable identity to
which an operator intended a destructive decision to apply.

A naïve public-key command that first resolves key to number on one thread and later queues
`tox_friend_delete(number)` can delete the wrong peer if the original peer disappears and the number
is reused before deletion executes. The mutation must bind lookup and delete inside one serialized
owner-thread operation.

ratox's ordinary filesystem model remains desirable. Its request response and friend removal lanes
were tiny FIFOs. IoTox needs the same ease while making framing, result evidence, durability, and
authority boundaries explicit.

## Decision

The stable operator selector for every friendship decision is the uppercase 32-byte Tox public key.
IoTox projects:

```text
<RUNTIME>/requests/<PUBLIC_KEY>/accept
<RUNTIME>/requests/<PUBLIC_KEY>/reject
<RUNTIME>/peers/<PUBLIC_KEY>/remove
<RUNTIME>/friend-events
```

The three writable objects are private FIFOs. One atomic record consists of an exact lowercase token
plus LF:

```text
accept\n
reject\n
remove\n
```

Case changes, whitespace, additional bytes, partial records, and wrong-lane tokens are rejected.
FIFO write success proves only kernel admission. `friend-events` records the later IoTox decision.

Incoming acceptance requires a matching live request record and calls
`tox_friend_add_norequest(public_key)`. Rejection withdraws only IoTox's live request record because
c-toxcore exposes no persistent pending-request object or remote rejection operation. Established
removal calls `tox_friend_delete`, which does not notify the remote peer.

The structured local protocol adds `transport_peer_remove_key`. The one-binary CLI resolves a
numeric compatibility selector to its current public key and sends the key-bound operation. Inside
the transport adapter, `tox_friend_by_public_key` and `tox_friend_delete` execute in one command on
the exclusive toxcore owner thread. The returned friend number is lifecycle evidence only.

Transport removal events carry the deleted public key captured before deletion. Application cleanup,
runtime withdrawal, and journal evidence therefore remain bound to the intended key even if toxcore
later reuses the numeric gap.

Every friendship event states that Tox friendship is transport recognition only. Accepting,
requesting, rejecting, or removing a friend does not grant, revoke, erase, or otherwise mutate the
independent IoTox authorization ledger.

## Consequences

A shell operator can decide live requests and remove peers through ordinary files without making an
incidental index the destructive authority. Delayed numeric-handle reuse cannot redirect the key-
bound transport mutation.

The exact tokens are intentionally less terse than ratox's historical `0`/`1` records. The filename
and body agree, malformed writes have explicit evidence, and scripts are easier to audit.

The request inbox and peer tree remain disposable live projections. `friend-events` is bounded local
operational evidence, not a signed durable audit ledger; its sequence is process-local and may repeat
across daemon restarts. A future durable friendship history must define retention, privacy,
redaction, capacity, rollback, and signature policy rather than silently promoting `/run`.

The local protocol minor version advances to 15. Dynamic and linked toxcore providers must expose
the exact `tox_friend_by_public_key` ABI consumed by the key-bound deletion path.


## Rejected alternatives

### Friend numbers as public mutation keys

Rejected because c-toxcore explicitly permits deletion gaps to be reused and numbers may change
after savedata reload. A human-visible directory or delayed command must not acquire destructive
meaning from an incidental process-local index.

### Resolve a key outside the owner thread, then delete later by number

Rejected because the target can disappear and the gap can be reused between those operations.
Lookup and delete are one indivisible provider turn.

### Treat friendship acceptance as authorization

Rejected because transport recognition is not ownership, role assignment, capability grant, or
recovery authority.

### Simulate rejection by add-then-delete

Rejected because c-toxcore exposes no pending-request object that must be removed. That sequence
creates an unnecessary friend mutation and can emit misleading lifecycle evidence.

### Couple every friend removal to authority revocation

Rejected because route endpoints may be rotated or temporarily removed without changing a stable
principal's authorization. A future revoke-and-remove ceremony must be an explicit compound
operation with its own commit order and failure semantics.

### Add a second friendship daemon

Rejected by the one-product decision. `iotox` owns the local surface, product semantics, and one
serialized toxcore adapter.
