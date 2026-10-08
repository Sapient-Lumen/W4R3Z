# Discovery fallback proof page, tracker, relay, LAN, manual hosts, and join-ceiling interface spec

## Purpose

The archive already had diagnostics, route classes, and repair-ladder language.
What it still lacked was one proof page that can answer the exact operator question left behind by fragmented connectivity docs:

> which discovery lanes are actually alive right now, what proof supports each lane, and what stronger connectivity claim must the product refuse?

Current official Resilio docs are clear that tracker, relay, LAN discovery, and predefined hosts are not interchangeable.
They are also clear that losing one lane does not necessarily kill the others.
But the product still leaves the operator to assemble that truth from several pages.

AnonSync should instead provide one discovery-fallback proof page whenever route certainty matters.

## Core decision

Connectivity proof must be lane-based.
The product must never offer one flat sentence like `peer discovery works` without showing which lanes were actually proven.
At minimum the proof page must separately score:

- bootstrap/catalog freshness
- tracker reachability
- relay reachability
- LAN discovery availability
- manual-host viability
- join ceiling for new peers

## Fixed review order

Every discovery-fallback proof page should render the same sections in the same order:

1. **Lane witnesses**
2. **Current effective envelope**
3. **Join ceiling**
4. **Blocked stronger sentence**

### 1) Lane witnesses

This section should show, lane by lane:

- witness class (`fresh-check`, `cached-witness`, `recent-transfer`, `config-declared`, `not-proven`, `failed`)
- last proof time
- seat scope or peer scope

The operator must be able to answer: **what evidence do we actually have for each discovery lane?**

### 2) Current effective envelope

This section should synthesize the lane witnesses into one envelope such as:

- `full public discovery available`
- `tracker unavailable; relay/manual continuity remains`
- `LAN-only discovery`
- `manual-host direct only`
- `existing peers only; new ambient joins blocked`
- `isolated except for already open sessions`

The operator must be able to answer: **what is the broadest honest connectivity claim right now?**

### 3) Join ceiling

This section should show separate ceilings for:

- existing known peers
- newly reappearing peers
- totally new public joins
- new manual-host joins

The operator must be able to answer: **who can still join or reconnect without further operator help?**

### 4) Blocked stronger sentence

The page must explicitly block lines such as:

- `all peers can connect normally`
- `relay is unavailable`
- `tracker loss broke syncing`
- `new peers can still discover this seat`

unless the lane witnesses support them.

## Public objects

### `discovery_fallback_proof`

Fields:

- `discovery_fallback_proof_id`
- `seat_ref`
- `lane_witnesses[]`
- `effective_envelope`
- `existing_peer_join_ceiling`
- `new_peer_join_ceiling`
- `manual_join_ceiling`
- `strongest_safe_sentence`
- `blocked_stronger_sentences[]`
- `generated_at`

## Main surface

A compact row should read like one of these:

- `full discovery envelope proven`
- `tracker unproven · relay/manual continuity proven`
- `LAN-only discovery proven`
- `existing peers only · new public joins blocked`
- `manual-host path only · ambient discovery absent`

## Event language

Use phrases such as:

- `tracker lane lost; fallback envelope remains via relay/manual hosts`
- `LAN discovery proven; WAN bootstrap still degraded`
- `new public joins no longer provable`
- `existing peer continuity survives on cached or manual lanes`

Avoid phrases such as:

- `network OK`
- `peers should connect`
- `tracker problem only`

Those lines hide the actual proof ceiling.

## CLI shape

```text
anonsync discovery proof show --seat self
anonsync discovery proof explain --seat self
anonsync discovery proof compare --seat self --peer atlas
```

## Non-clone reason

Current official Resilio docs still preserve lane truth only across several separate articles.
AnonSync should instead make discovery fallback proof a single first-class page so the operator does not need support folklore to know which lanes still exist.
