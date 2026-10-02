# Application epoch restart v1

Status: frozen and qualified over direct UDP and forced TCP on 2026-08-26.

## Problem

Tox connection callbacks describe the provider's transport epoch. They do not necessarily expose an
IoTox process boundary. In particular, a TCP relay can keep the remote Tox identity continuously
online while the remote Agent is replaced. The replacement must send a fresh HELLO nonce, while the
original IoTox rule correctly treated changed HELLO bytes inside one transport epoch as a conflict.
The result was a fail-closed but indefinitely frozen application session.

IoTox needs a narrower application-epoch transition that does not weaken the existing same-epoch
conflict rule or derive authority from friendship.

## Negotiation

`application-epoch-restart-v1` is feature bit 27. It is named but is not part of the unconditional
implemented-feature mask. An Agent advertises it only after acquiring its separate durable
application-protocol incarnation lease before network startup. Auxiliary route workers receive the
same process incarnation and advertise the feature only through their explicitly constructed
HELLOs.

An in-transport restart is permitted only when all three HELLOs involved advertise bit 27:

- the local HELLO frozen for the continuous Tox epoch;
- the incumbent peer HELLO;
- the candidate peer HELLO.

Legacy peers therefore retain the original one-HELLO-per-transport-epoch behavior.

## Nonce generation layout

When bit 27 is advertised, the existing 16-byte session nonce has this canonical layout:

| Offset | Size | Meaning |
|---:|---:|---|
| 0 | 8 | unsigned durable process incarnation, big-endian, nonzero |
| 8 | 4 | unsigned process-local connection epoch, big-endian, nonzero |
| 12 | 4 | operating-system random entropy |

The ordered generation is the lexicographic tuple `(process incarnation, connection epoch)`. A
process restart advances the first field. An asymmetric reconnect within one process advances the
second. Resetting the connection field to one is valid only with a greater durable incarnation.
Zero in either ordered field makes a bit-27 HELLO structurally invalid.

The durable record is device-signed, stored separately from Ratox state in an owner-private
directory, locked for the Agent lifetime, and incremented before any Tox transport is constructed.
It detects corruption, foreign-device substitution, and concurrent legitimate processes. Like the
other signed local monotonic guards, it does not by itself defeat replay of a complete older record
by an attacker who can replace private durable state; that requires an external monotonic witness.

## Receive state machine

For a connected friend with one frozen valid peer HELLO:

- exact payload retransmission is idempotent;
- a lower generation is rejected as stale and leaves the current application session usable;
- a different payload at the exact same generation retains `conflicting_hello` and freezes closed;
- a higher generation starts a new application epoch inside the continuous Tox transport epoch.

On the higher-generation transition, the receiver:

1. increments its local application `online_epoch`;
2. retains the exact canonical local HELLO bytes and its reserved message identifier;
3. marks that local HELLO unsent so the exact record is enqueued again;
4. accepts and freezes the higher peer HELLO and clears both confirmations;
5. renegotiates the feature and size intersection;
6. retires the old authority proof, sync publisher/subscriber work, Ratox route, cached command
   results, peer description, auxiliary route binding, and live auxiliary transfers;
7. completes the ordinary HELLO/CAPABILITIES and authority ceremonies before application traffic
   can resume.

The transition never carries application authorization, transfer identity, binding state, or
terminal attachment across epochs. A greater generation can force reauthentication but cannot grant
authority. A malicious authenticated Tox peer can still deny service by advancing or conflicting its
own HELLO; friendship has never promised availability.

Counters fail closed on exhaustion. A stale candidate returns a protocol error for evidence but does
not poison the accepted session. Transport offline still closes the ordinary Tox epoch and follows
the existing full session reconstruction path.

## Qualification boundary

ADR 0183 and `evidence/2026-08-26-sandwurm-sync-route-throughput.md` bind the first accepted proof.
Four clean subscriber Agent replacements recover the primary and two auxiliary application sessions
under both direct UDP and forced TCP, run an ABBA fixed/adaptive 16 MiB transfer cell, and then pass
40 protected Ratox samples. This qualifies same-binary application re-handshake in the controlled
two-guest laboratory. It is not a general Tox extension, transparent connection migration, PTY
survival, physical multipath proof, or cross-client compatibility claim.
