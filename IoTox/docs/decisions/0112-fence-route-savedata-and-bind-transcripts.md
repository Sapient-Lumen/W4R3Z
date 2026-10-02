# ADR 0112: fence route savedata and bind routes to confirmed transcripts

Status: accepted

Date: 2026-08-21

## Decision

Every configured Tox instance must compare the public key reconstructed by `tox_new()` with its
expected authenticated route key before bootstrap, relay registration, or the first `tox_iterate()`.
The primary agent obtains that expectation from the route set's coordinator Tox key. Auxiliary
workers will obtain it from their exact member record.

Route membership presented to a peer uses the fixed route-binding-v1 record. The stable device signs
the route-set principal, coordinator, generation, exact member policy, and the digest of the already
confirmed IoTox session transcript. Creation and verification APIs derive that digest from a
`PeerSessionSnapshot`; they do not accept a caller-asserted `transcript_confirmed` boolean or digest.

Feature bit 21 and message type 19 remain unadvertised until the agent supervises the complete live
exchange. The reserved Ratox v1 frame meanings are unchanged.

## Consequences

A valid policy file cannot accidentally start unrelated Tox savedata. Moving, replacing, or
cross-wiring worker state fails before network activity. A captured route binding cannot be replayed
on another online epoch because its transcript identifiers and nonces change the digest.

The coordinator still needs a worker owner loop, authenticated remote route-set delivery, exact
message replay handling, and lifecycle integration before Gate 2 is complete. The codec is a
prerequisite, not a claim that multi-route product traffic is live.
