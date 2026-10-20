# ADR 0034: Bind stable IoTox principals to each confirmed Tox session in both directions

**Status:** accepted and implemented in rev0009

## Context

A Tox friendship authenticates a transport endpoint. The IoTox authorization ledger names
stable Ed25519 principals that can outlive a Tox endpoint, route, online epoch, or controller
installation. Treating friendship as authority would erase that distinction; treating one
application proof as mutual would confuse two independent decisions.

IoTox already freezes a canonical two-HELLO transcript and requires both peers to confirm it
before application traffic. That exact transcript is the appropriate anti-splicing context for
principal proof.

## Decision

After a compatible session is transcript-confirmed, each endpoint independently acts as:

1. **verifier** — sends one canonical `AUTHORITY_CHALLENGE` against its current local ledger
   head and accepts a signed proof only when the claimed principal is active in that ledger;
2. **claimant** — answers the peer's canonical challenge with a proof signed by the local stable
   IoTox device identity by default.

The directions are separate. A peer may be authorized to invoke local operations while the
peer has not yet accepted this device, or vice versa.

Every challenge and proof binds:

- the verifier's stable device public key;
- the verifier's ownership epoch, ledger sequence, and ledger-tail digest;
- the exact canonical session-transcript digest;
- a fresh 32-byte challenge nonce;
- the challenge frame message identifier;
- the claimant principal public key;
- an Ed25519 signature over the canonical proof body.

The first structurally valid challenge and proof bytes are frozen per online epoch. A transient
Tox `SENDQ` or disconnected-send failure may retry only the exact reserved frame. A successful
local enqueue is never retried by this layer.

The stable device identity answers automatically because it is already held by the running
product. A RecallRoot-derived owner proof remains an explicit, phrase-fed re-entry operation;
the long-running daemon never receives or retains the phrase or owner secret.

## Consequences

Tox remains the encrypted connection substrate, but no Tox key alone grants an IoTox
capability. Route identities may rotate without replacing the stable device principal or
constitution.

`proof-sent` means the local Tox queue accepted the proof. It is not a remote receipt. Future
protocol work may add a proof receipt, but current operation admission must not claim one.

A local authority-ledger mutation invalidates every remote authorization immediately and
requires a fresh challenge against the new exact ledger head. Reconnect creates a new online
epoch and transcript, so previous proofs cannot be replayed into it.

## Rejected alternatives

- **Friendship is authority:** simple but violates the product's ownership model.
- **One mutual proof:** cannot represent asymmetric policy or failure.
- **Sign only a nonce:** permits proof splicing across devices, epochs, or sessions.
- **Send RecallRoot automatically:** exposes the permanent owner secret to the daemon.
- **Vendor-issued session token:** creates the sovereign third party IoTox rejects.
