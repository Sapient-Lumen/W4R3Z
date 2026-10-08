# Reachability contract sheet page: helper budget, discovery lanes, and exposure ceiling interface spec

## Purpose

Before an operator changes network reachability, they need one ordinary page that answers:

> what helper lanes are allowed, what discovery methods are active, and what is the strongest honest exposure sentence right now?

This page exists so tracker, relay, multicast, predefined hosts, proxy, bind-interface, and listener posture do not remain scattered trivia.

## Core decision

Every serious reachability or helper-policy surface must open one first-class **Reachability contract sheet**.

The sheet owns:

- requested route policy
- effective helper budget
- discovery lanes in force
- transfer lanes in force
- exposure ceiling
- strongest safe sentence
- stronger rejected sentence

## Fixed page order

1. route claim header
2. helper budget matrix
3. discovery and transfer lane map
4. exposure ceiling card
5. next-safe action rail

### 1) Route claim header

Show at minimum:

- subject / seat / cohort scope
- current reachability class (`lan-only candidate`, `local-network preferred`, `mixed direct+helper`, `internet-capable`, `unknown`)
- strongest safe sentence
- stronger rejected sentence

Example safe sentence:

- `Tracker and relay are disabled for this share, but prior outside-LAN route memory has not yet been cleared.`

### 2) Helper budget matrix

Render one row per helper family with columns:

- helper family
- current policy (`allowed`, `blocked`, `required`, `not configured`, `unknown`)
- source plane (`share`, `seat`, `config`, `runtime residue`, `other`)
- widening risk
- proof basis

Minimum helper rows:

- tracker discovery
- relay transfer
- LAN multicast/broadcast discovery
- predefined hosts
- listener / direct ingress
- UPnP / automatic port mapping
- proxy-mediated egress
- bound-interface restriction

### 3) Discovery and transfer lane map

Keep discovery and transfer separate.
For each lane show:

- lane family
- discovery role or transfer role
- active now? (`yes`, `no`, `fallback only`, `unknown`)
- evidence freshness
- route witness

Minimum lanes:

- LAN broadcast / multicast discovery
- tracker discovery
- predefined-host bootstrapping
- direct TCP/UDP peer path
- relayed transfer path
- proxy-constrained egress path

### 4) Exposure ceiling card

This card is mandatory.
Show:

- widest network audience the current posture could still reach
- whether internet discovery remains possible
- whether internet transfer remains possible
- whether prior outside-LAN memory weakens the claim
- what must be proven false before `LAN-only` becomes a strong sentence

### 5) Next-safe action rail

Only show actions that preserve route semantics, such as:

- `Review LAN-only contract`
- `Tighten helper budget`
- `Inspect route provenance`
- `Clear public-route residue`
- `Switch to wider route policy`

## Rules

### Rule 1 — helper toggles never speak alone

Every visible toggle must be represented again as part of the resolved helper budget.

### Rule 2 — discovery lanes and transfer lanes stay separate

A surface must not let `reachable` hide whether the route depends on discovery helper, transfer helper, or both.

### Rule 3 — strongest safe sentence is mandatory

The page must explicitly say what can honestly be claimed now, not only what policy was requested.

### Rule 4 — rejected stronger sentence is mandatory

The page must preserve at least one stronger overclaim that the current evidence does not support.

## Acceptance criteria

A later operator can:

- tell which helper families are allowed or blocked
- tell which discovery and transfer lanes remain in force
- tell whether internet discovery or relay is still possible
- tell whether `LAN-only` is already proven or only requested
- tell what next page to open for stronger proof
