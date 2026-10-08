# Transport route proof page: direct LAN, direct WAN, relay, and route-switch evidence interface spec

This page exists so `connected` and `relay` stop pretending to answer the whole route question.
The operator often needs to know not only whether a peer is reachable, but **how bytes are actually moving right now** and whether that answer just changed.

## Operator question

> what route is currently carrying data, how strong is the witness for that claim, and what route switch just happened or remains likely?

## When this page must appear

Render whenever the product is about to:

- claim a direct route
- claim relay fallback
- explain a speed or latency drop
- justify why a privacy posture has changed
- explain why tracker success still did not yield transfer
- diagnose route switching between LAN, WAN, and relay states

## Fixed page order

1. **Current route verdict**
2. **Witness stack**
3. **Route-switch timeline**
4. **Performance and privacy ceilings**
5. **Blocked stronger sentence**

## 1) Current route verdict

Show one verdict:

- `direct LAN currently witnessed`
- `direct WAN currently witnessed`
- `relay-carried route currently witnessed`
- `transport reachable but current route unproved`
- `no active transfer route`

The operator must be able to answer: **what route is carrying bytes right now?**

## 2) Witness stack

Possible witness classes include:

- peer-list relay indicator
- negotiated socket witness
- matched local subnet witness
- observed relay endpoint witness
- successful direct transfer witness
- failed direct attempt with relay takeover
- stale configuration-only belief
- no recent witness

Each witness row must show freshness, confidence, and whether it supports directness, relay use, or only possibility.

## 3) Route-switch timeline

Show route transitions such as:

- `tracker introduced -> direct WAN`
- `direct WAN failed -> relay-carried`
- `LAN discovery -> direct LAN`
- `predefined host dialed -> no active transfer`
- `relay-carried -> direct WAN restored`

Each transition row must show cause if known:

- NAT / firewall refusal
- listener unavailable
- relay required
- network changed
- interface audience changed
- cause unknown

## 4) Performance and privacy ceilings

Publish separate ceilings for:

- speed expectation
- latency expectation
- third-party byte carriage
- metadata disclosure already incurred
- route persistence confidence

Examples:

- a direct route may still have metadata exposure from tracker introduction
- a relay route may preserve content confidentiality while losing no-third-party-carriage claims
- a current direct route does not prove the next session will also be direct

## 5) Blocked stronger sentence

Allowed examples:

- `Current transfer is relayed; content remains peer-encrypted.`
- `Direct WAN route is currently witnessed after tracker introduction.`
- `No recent route witness exists despite allowed direct policies.`

Blocked examples:

- `This peer never used relay.`
- `No infrastructure ever learned about this share.`
- `Direct route is guaranteed from now on.`
- `Current slow speed is caused only by relay.`

## Main actions

Examples:

- `Open discovery branch review`
- `Export route proof`
- `Tighten fallback ladder`
- `Inspect service-contact exposure`
