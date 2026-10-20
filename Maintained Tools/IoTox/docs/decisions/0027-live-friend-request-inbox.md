# ADR 0027: Incoming Tox friend requests form a live, explicit operator inbox

**Status:** accepted and implemented in rev0007

## Context

c-toxcore reports an incoming friend request by callback with a 32-byte public key and a
bounded message. The callback does not itself add the peer, persist an IoTox authorization
record, or grant application authority. ratox treated this event as an ordinary Unix object:
it exposed the request and required an explicit accept or reject action. That remains the
right human model for a ratox successor, but IoTox also needs byte preservation, public-key
selection, bounded local IPC, and a clear durability claim.

A request is not a stable device identity. The Tox public key identifies the requesting
transport endpoint. Accepting it calls c-toxcore's no-request friend-add operation and creates
only a Tox friendship.

## Decision

IoTox copies callback bytes immediately into a bounded in-memory inbox keyed by the uppercase
Tox public key. It transactionally projects each complete live record at:

```text
run/requests/<PUBLIC_KEY>/
  public-key
  message
  message-bytes
  received-unix-ms
```

The one executable exposes explicit operations:

```text
iotox requests
iotox request-accept PUBLIC_KEY
iotox request-reject PUBLIC_KEY
```

`request-accept` requires a matching live inbox record and then uses
`tox_friend_add_norequest`. `transport-peer-accept` remains a separate low-level operator
operation that may add a known public key without a recorded request. Both create transport
friendship only. `request-reject` removes only the local request record; Tox has no remote
rejection message in this API.

Duplicate requests from the same public key replace the current live record. Same-key publish,
accept, and reject operations are serialized so the in-memory source and disposable runtime
projection do not expose a half-committed record.

The rev0007 inbox is deliberately **live, not crash-durable**. `/run` is reconstructed on
startup and cannot be treated as an authorization ledger or permanent audit store. A future
durable request history, if wanted, must use a separate private state store with retention,
redaction, capacity, and replay policy.

## Consequences

An operator can inspect and decide incoming friendship requests through the one-binary Unix
surface without reading raw callback logs. Acceptance and rejection are unambiguous and
public-key-first. A CLI typo cannot use `request-accept` to add a key that never appeared in
the current inbox; the explicit low-level transport operation remains available when that is
actually intended.

The inbox does not survive process restart, prove a person's identity, establish ownership,
create roles, or authorize machine commands. Future pairing must consume a transport session
and then perform an independent signed IoTox identity/authorization exchange.
