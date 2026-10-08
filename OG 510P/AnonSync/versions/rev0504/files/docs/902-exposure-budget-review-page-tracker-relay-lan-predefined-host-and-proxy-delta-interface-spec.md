# Exposure budget review page: tracker, relay, LAN, predefined-host, and proxy delta interface spec

## Purpose

Changing network reachability is not only a connectivity decision.
It is also an exposure-budget decision.
This page exists to answer:

> what discovery and transfer audiences become newly possible or newly impossible if I accept this route-policy change?

## Core decision

Every serious widening or narrowing of reachability must compile into one first-class **Exposure budget review**.

The review owns:

- requested policy delta
- discovery audience delta
- transfer audience delta
- helper dependence delta
- ingress / observer delta
- strongest safe sentence after apply

## Fixed page order

1. requested route-policy delta
2. discovery audience delta
3. transfer audience delta
4. helper dependence delta
5. decision rail

### 1) Requested route-policy delta

Show:

- toggles or policy objects changing
- source plane of change
- whether this is widening, narrowing, or mixed
- strongest safe sentence if applied

### 2) Discovery audience delta

Render rows for audiences that may newly discover or cease to discover the subject:

- same LAN peers
- previously known external peers
- tracker-mediated peers
- manually specified peers
- proxy-visible routes

Each row shows:

- before
- after
- confidence
- evidence source

### 3) Transfer audience delta

Show who may newly exchange bytes or lose that ability.
Rows at minimum:

- direct LAN path
- direct WAN path
- relayed path
- proxy-constrained path
- predefined-host direct path

### 4) Helper dependence delta

This card explains whether the change:

- removes helper dependence
- adds helper dependence
- keeps dependence but changes fallback order
- leaves ambiguity due to residue or unknown route state

### 5) Decision rail

Possible outcomes:

- `apply widening with receipt`
- `apply narrowing with residue warning`
- `review LAN-only proof first`
- `inspect route provenance first`
- `cancel; exposure delta too broad`

## Rules

### Rule 1 — every reachability change publishes audience delta

The product must not let route changes masquerade as purely internal tuning.

### Rule 2 — helper dependence delta is mandatory

Operators must see whether convenience came from broader helper use.

### Rule 3 — widening and narrowing may coexist

For example, a change may tighten public ingress but widen tracker discovery.
The review must show mixed deltas plainly.

## Acceptance criteria

A later operator can:

- tell whether the policy widened or narrowed exposure
- tell who may newly discover or transfer with the subject
- tell which helpers were added or removed
- tell whether residue still weakens the post-apply claim
- tell which receipt family to inspect afterward
