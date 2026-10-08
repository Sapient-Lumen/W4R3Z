# Mapping lease watch page: observed port-map freshness, stale suspicion, and clearance proof interface spec

## Purpose

Once automatic mapping exists as a first-class action, the product also needs a first-class place to answer:

> is a port mapping believed live, merely previously observed, suspected stale, or believed cleared?

Without this page, operators are forced back into router folklore and symptom-reading.

## Core decision

Every seat that can request automatic ingress mutation must have one first-class **Mapping lease watch** page.

The page owns:

- last requested mapping action
- last observed mapping state
- freshness window
- stale-suspicion triggers
- clearance proof state
- reopen triggers

## Fixed page order

1. current lease claim
2. evidence timeline
3. stale-suspicion triggers
4. clearance proof card
5. next-safe action rail

### 1) Current lease claim

Show one of:

- `no automatic mapping ever requested`
- `mapping request issued; live state unknown`
- `mapping observed recently`
- `mapping may still exist, but proof is stale`
- `mapping removal requested; clearance not yet proven`
- `mapping cleared with fresh proof`

Include:

- port number
- mechanism (`UPnP`, `NAT-PMP`, `mixed`, `unknown`)
- observation source
- claim ceiling sentence

### 2) Evidence timeline

Render a durable timeline with rows such as:

- mapping enabled
- mapping request attempted
- direct inbound success observed
- route fell back to relay
- mapping disable requested
- external router witness captured
- direct inbound failure observed after disable

Each row carries freshness and trust grade.

### 3) Stale-suspicion triggers

Show triggers that weaken a previous live-mapping claim, such as:

- runtime restart
- listener port change
- router or network change
- long dormancy
- proxy/policy change
- explicit disable request without proof of removal

### 4) Clearance proof card

This card is mandatory when disable/removal has been requested.
Show:

- whether removal was only requested or externally witnessed
- strongest safe sentence now
- stronger rejected sentence
- next proof path

Example rejected sentence:

- `The router definitely no longer exposes this port.`

### 5) Next-safe action rail

Only show actions that preserve claim integrity, such as:

- `Run direct-proof test`
- `Capture external router witness`
- `Reopen auto port-map review`
- `Accept stale claim ceiling`

## Rules

### Rule 1 — time matters to lease truth

A mapping claim without freshness is not enough.

### Rule 2 — disable intent does not equal clearance proof

The page must keep those meanings separate.

### Rule 3 — route symptoms may weaken but not prove lease state

Indirect evidence may downgrade confidence; it must not silently over-prove clearance.

## Acceptance criteria

A later operator can:

- tell the last known mapping state for the listening port
- tell whether that state is fresh, stale, or only requested
- tell what events weakened prior certainty
- tell whether clearance has been proven or merely hoped for
- tell what next proof action is appropriate
