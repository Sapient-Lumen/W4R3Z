# ADR 0114: carry the signed route set with each route binding

Status: accepted

Date: 2026-08-21

## Decision

The route-binding-v1 wire message carries the complete stable-device-signed route set immediately
before the exact 224-byte transcript binding. A two-byte big-endian length makes the composition
canonical. Message type 19 uses sequence 5, a nonzero message identifier, and zero flags,
correlation, and expiry. The maximum 16-member exchange is 1,150 bytes, below the existing
1,332-byte application payload ceiling, so no fragmentation or partial trust state is introduced.

Verification requires two local trust inputs: the expected remote stable-device principal and the
minimum acceptable generation. The receiver verifies the route set against those inputs before it
uses that exact set to verify member policy, peer Tox key, stable signature, and confirmed-session
transcript. Values asserted only by the received object never become trust anchors.

## Consequences

A worker exchange is self-contained and deterministic without relying on an ambient, potentially
different route-set object. A captured record still fails on a new transcript, a foreign signed set
still fails against the expected principal, and an older set fails against the local generation
floor. The bounded message fits one existing custom packet.

This decision does not define how a worker learns the expected peer principal, does not retain a
replay high-water mark, and does not change coordinator lifecycle state. Feature bit 21 therefore
remains absent from default advertisement until the supervisor owns those three effects.
