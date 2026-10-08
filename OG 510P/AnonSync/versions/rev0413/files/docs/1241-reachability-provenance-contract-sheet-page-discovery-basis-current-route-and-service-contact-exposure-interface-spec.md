# Reachability provenance contract sheet page: discovery basis, current route, and service-contact exposure interface spec

## Purpose

The archive already has pages for path identity, interface affinity, queue policy, presence, and operator attestation.
What it still lacked was one ordinary page for the narrower question:

> how did this peer become reachable, how are bytes routed right now, which service contacts were involved, and what stronger privacy or directness sentence is still blocked?

Current official Resilio docs make this seam concrete.
They separately describe tracker discovery, LAN discovery, predefined hosts, relay fallback, bootstrap config lookup, and link-landing privacy behavior.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Reachability provenance contract sheet** whenever a subject or peer has active or recent network reachability.

The sheet exists to answer six things in one place:

1. what discovery basis introduced the peer
2. what transport route is currently witnessed
3. what service-contact exposure occurred
4. what fallback routes remain allowed
5. what privacy and performance ceilings follow from that state
6. what stronger sentence remains blocked

## Fixed page order

1. **Reachability header**
2. **Discovery basis card**
3. **Current transport card**
4. **Service-contact exposure card**
5. **Fallback ladder**
6. **Claim ceiling and action rail**

### 1) Reachability header

Show at minimum:

- `reachability_contract_id`
- local seat / peer refs
- subject ref
- current status (`unresolved`, `discoverable`, `reachable`, `active-transfer`, `degraded`, `offline`)
- strongest safe sentence
- blocked stronger sentence
- freshness of last route witness

Supported discovery bases must include:

- `tracker-introduced`
- `lan-multicast-introduced`
- `predefined-host-introduced`
- `mixed-or-redundant`
- `manual-imported-address`
- `unknown`

Supported current transport routes must include:

- `direct-lan`
- `direct-wan`
- `relay-carried`
- `route-unknown`
- `no-current-route`

### 2) Discovery basis card

Show discovery rows grouped by source:

- tracker witness
- LAN witness
- predefined-host witness
- manual address / import witness
- negative witness (`disabled`, `blocked`, `untested`)

Each row must show:

- whether the mechanism is allowed
- whether it was actually used
- freshness
- corroborating evidence
- why it won over alternatives

The operator must be able to answer:

> how did we actually find each other, not merely how could we have found each other?

### 3) Current transport card

Show:

- current route class
- directness grade
- last route switch
- current performance ceiling
- route witness source
- listener / address pair in use if safe to reveal
- whether the route is policy-preferred or only fallback

The operator must be able to answer:

> are bytes going direct right now or only relayed right now?

### 4) Service-contact exposure card

Separate these exposure classes explicitly:

- bootstrap config contact
- tracker metadata exchange
- relay carriage
- link-landing service use
- zero-third-party-contact witness
- unknown

Each row must show:

- what infrastructure was contacted
- what data class was exposed (`ip:port`, `share-id`, encrypted payload carriage, aggregate click only, none`)
- whether content bytes were exposed
- whether disablement is possible
- what operational consequence follows if disabled

The operator must be able to answer:

> what left the local trust boundary here?

### 5) Fallback ladder

Show the ordered ladder the system may still try:

- direct via existing peer addresses
- tracker reintroduction
- LAN rediscovery
- predefined-host dialout
- relay fallback
- no permitted fallback

Every rung must show allowed / disabled / unavailable / failed / current status.

### 6) Claim ceiling and action rail

Allowed examples:

- `Tracker introduced peer; current route is direct WAN.`
- `Peer is reachable only by relay-carried transport right now.`
- `No third-party byte carriage was witnessed on the current route.`
- `Bootstrap and tracker contact occurred; payload remained peer-encrypted.`

Blocked examples:

- `No third party learned anything.`
- `This peer is direct-only.`
- `This route is private from infrastructure metadata.`
- `The current fast path will persist.`

Primary actions may include:

- `Review discovery branch`
- `Inspect route proof`
- `Inspect exposure details`
- `Tighten allowed fallback`
- `Export reachability receipt`

## What this page prevents

Without this page, the product quietly conflates policy allowance, discovery origin, active route, and privacy posture.
AnonSync must instead publish one effective reachability sentence with one visible claim ceiling.
