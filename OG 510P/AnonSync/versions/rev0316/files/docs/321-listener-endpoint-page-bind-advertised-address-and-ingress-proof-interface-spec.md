# Listener endpoint page: bind, advertised address, and ingress proof interface spec

## Purpose

This page answers one ordinary question:

> what endpoint is this seat actually listening on right now, what endpoint is it advertising outward, and how much of that claim is proved versus merely configured?

The page exists because `listening port`, `external port`, `bind interface`, `UPnP`, `NAT-PMP`, and `service started` are not the same truth.

## Core decision

Every seat must render one first-class **Listener endpoint** page.
That page owns:

- local bind facts
- advertised endpoint claims
- ingress-proof grade
- mapping mechanism
- interface and address-family selection
- safest next change if direct ingress is weak or blocked

The workbench must not force the operator to infer ingress health from a peer icon, a speed chart, or a generic `reachable` badge.

## Primary layout

The page always renders the same regions in the same order:

1. seat strip
2. bind contract card
3. advertised endpoint card
4. ingress-proof card
5. mapping and interface card
6. endpoint receipts

### 1) Seat strip

Show:

- seat label
- current listener verdict: `proven-ingress`, `likely-ingress`, `configured-only`, `blocked-ingress`, `ambiguous-ingress`
- active local port/protocol family summary
- one next honest action

### 2) Bind contract card

This card publishes:

- local bind interface selection
- local addresses actually bound
- listening port in force
- protocol families expected (`tcp`, `udp`, address family)
- why this bind won: `default`, `explicit interface bind`, `host-only fallback`, `temporary override`, `unknown`

The operator must be able to answer: **what is this seat actually listening on locally?**

### 3) Advertised endpoint card

This card publishes:

- public and local endpoint claims currently being published
- source of each claim: `tracker publication`, `manual pin`, `local discovery`, `host override`, `learned reflection`, `unknown`
- trust grade for each claim: `proven`, `fresh-but-unproved`, `stale`, `conflicted`
- whether peers should treat the claim as direct-capable or advisory only

The operator must be able to answer: **what endpoint story are other peers being told?**

### 4) Ingress-proof card

This card publishes:

- direct-ingress verdict
- strongest successful proof witness, if any
- strongest blocker if proof is missing: `firewall`, `nat`, `router`, `proxy`, `interface mismatch`, `catalog/bootstrap failure`, `unknown`
- whether failure is global or pair-specific
- minimum safe retest after a change

The operator must be able to answer: **is direct ingress merely configured, or actually working?**

### 5) Mapping and interface card

This card publishes:

- automatic mapping posture (`off`, `upnp`, `nat-pmp`, `other`, `unknown`)
- manual mapping expectation
- external-port override if any
- multiple-NIC or subnet caveats
- address-family skew if IPv4 and IPv6 differ

The operator must be able to answer: **which host or network mechanism is helping or hurting this listener?**

### 6) Endpoint receipts

Receipts show:

- bind changes
- advertised-endpoint changes
- mapping attempts
- proof-grade changes
- operator acknowledgments of ambiguous or stale endpoint claims

## Non-negotiable rules

### Rule 1 — configured port is not proof of ingress

A configured listening port may be real and still not be reachable.
The page must separate configured state from proven direct ingress.

### Rule 2 — local bind and advertised claim stay adjacent

The page must not show a public endpoint claim without the local bind it supposedly represents.

### Rule 3 — interface choice must be attributable

If one NIC, subnet, VPN, or address family won, the page must say why.

## Honest outputs

The page may conclude:

- `Listening on 0.0.0.0:28889 and advertising public endpoint 198.51.100.12:28889; direct ingress proved with fresh pairwise witness.`
- `Listening locally, but public endpoint claim is stale; direct ingress not yet proved after interface change.`
- `External port override conflicts with current bind; peers may be dialing an endpoint this seat is not actually serving.`
- `Proxy posture makes this seat egress-only; listening port remains locally real but not a credible direct ingress path.`

It may not collapse those outcomes into one generic `listening` badge.
