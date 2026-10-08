# Advertised endpoint review page: manual pin, trust scope, and staleness interface spec

## Purpose

This page answers one ordinary question:

> which endpoint claims are currently trusted enough to advertise or pin manually, what scope those claims apply to, and which stale or conflicting claim is degrading route choice right now?

The page exists because `known host`, `predefined host`, `external port`, and `remote IP:port` are not self-authenticating truths.

## Core decision

Every seat that can publish, cache, or pin concrete endpoints must render one first-class **Advertised endpoint review** page.
That page owns:

- endpoint claim inventory
- claim source and freshness
- trust scope
- symmetric versus one-sided pin requirements
- stale or conflicting endpoint residue

The workbench must not force the operator to trust a literal `IP:port` string without provenance.

## Primary layout

The page always renders the same regions in the same order:

1. subject strip
2. endpoint claim table
3. pinning contract card
4. conflict and staleness card
5. apply review card
6. endpoint receipts

### 1) Subject strip

Show:

- seat or subject under review
- current endpoint-claim verdict: `clean`, `usable-with-caveat`, `stale`, `conflicted`, `unsafe-to-pin`
- one next honest action

### 2) Endpoint claim table

Each row shows:

- endpoint literal
- address family and port
- source: `manual pin`, `tracker-learned`, `lan-learned`, `host override`, `local bind projection`, `other`
- freshness
- trust grade
- applicable scope: `this subject`, `this seat`, `peer-pair`, `temporary review`, `global host policy`

The operator must be able to answer: **what endpoint claims exist, and where did they come from?**

### 3) Pinning contract card

This card publishes:

- whether manual pins are in force
- whether both sides need symmetric pins for the intended outcome
- whether the current pin is additive, narrowing, or authoritative
- whether the pin is expected to survive interface changes, NAT rebinding, or storage/profile changes

The operator must be able to answer: **what exactly does this manual pin mean, and who else needs matching configuration?**

### 4) Conflict and staleness card

This card publishes:

- endpoint claims that disagree on port, interface, or address family
- stale claims still affecting route choice
- claims that remain locally visible after narrowing helper posture
- conflicts between manual pins and current listener reality

The operator must be able to answer: **which endpoint story is currently misleading the product?**

### 5) Apply review card

This card publishes reviewed mutations such as:

- add manual endpoint pin
- replace stale pin
- clear learned residue
- downgrade a previously trusted endpoint to advisory only
- widen from pair-specific pin to seat-level publication

The operator must be able to answer: **what safe endpoint mutation should I apply next?**

### 6) Endpoint receipts

Receipts show:

- endpoint claim additions
- pin changes
- residue clears
- conflict acknowledgments
- exported endpoint-trust snapshots

## Non-negotiable rules

### Rule 1 — literal endpoint strings require provenance

The product may not display or reuse `IP:port` as if the string itself were proof.

### Rule 2 — manual pins and learned claims must stay separate

A manual pin must not silently replace the historical record of what was auto-learned.

### Rule 3 — scope must be explicit

A pair-specific endpoint pin is not the same thing as seat-wide publication.

## Honest outputs

The page may conclude:

- `Manual pin 203.0.113.45:28889 is fresh enough for this peer pair but conflicts with the seat's current advertised public port.`
- `Tracker-learned endpoint remains stale after interface change; direct route candidates should treat it as advisory only until re-proved.`
- `This subject relies on symmetric manual pins on both peers because tracker is disabled by policy.`
- `Endpoint inventory is conflicted across IPv4 and IPv6 families; do not widen seat-level publication until listener proof is refreshed.`

It may not collapse those outcomes into one generic `known host configured` badge.
