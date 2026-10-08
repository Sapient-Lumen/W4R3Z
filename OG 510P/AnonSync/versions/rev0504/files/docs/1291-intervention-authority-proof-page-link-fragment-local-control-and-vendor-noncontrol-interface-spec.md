# Intervention-authority proof page: link fragment, local control, and vendor non-control interface spec

## Purpose

This page exists for the serious question:

> if something goes wrong, what can the vendor actually do, what can only the operator or peers do, and what stronger rescue or takedown sentence is false here?

## Core decision

AnonSync must expose one **Intervention-authority proof** whenever the product shows abuse, revoke, takedown, support, or emergency language that could be mistaken for vendor-side control over the live mesh.

## Proof ladder

### Rung 1 — vendor-visible but non-authoritative

Prove whether the vendor can:

- count landings
- receive purchases or billing identity
- receive diagnostics if sent
- observe tracker-routable identifiers
- operate relay carriage

But also prove that these facts do **not** imply:

- share deletion authority
- peer-graph deletion authority
- guaranteed peer-block authority
- remote wipe authority

### Rung 2 — fragment-local capability proof

Prove whether the capability-bearing part of a join artifact stays after `#` and therefore remains browser-local rather than landing-service-visible.

Allowed outcomes:

- `fragment-local-capability-proven`
- `fragment-split-uncertain`
- `no-fragment-proof`

### Rung 3 — mesh-control boundary

Prove whether the mesh itself is governed only by:

- devices already holding the data
- peers already holding the capability
- user-driven local deletion or revocation actions
- peer-controlled policy changes

Allowed outputs:

- `vendor-cannot-delete-user-held-copies`
- `vendor-cannot-force-universal-peer-non-discovery`
- `vendor-can-only-narrow-its-own-services`
- `mesh-control-boundary-unknown`

### Rung 4 — evidence-send exception

If the user sends logs or crash artifacts, prove the narrower statement:

- the vendor may inspect sent evidence and recommend action
- this still does not imply direct mutation authority over the user mesh

### Rung 5 — blocked stronger sentence

Always end with the strongest blocked sentence, such as:

- `We proved the vendor can receive diagnostics and count link landings, but we did not prove the vendor can invalidate already-held peer credentials or delete data on peer devices.`
- `We proved the vendor can disable its own tracker or relay services, but we did not prove it can erase decentralized peer knowledge already held by participants.`

## Required evidence fields

Every proof must show:

- subject or mesh ref
- current service-contact posture
- current local-control posture
- evidence-send status
- intervention claim being tested
- supported rung
- blocked stronger sentence

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- what the vendor can merely observe
- what the vendor can only inspect after explicit user send
- what the vendor can narrow only on its own infrastructure
- what the vendor cannot delete, revoke, or block across already-connected peers
- what stronger help/takedown sentence the product refused to make
