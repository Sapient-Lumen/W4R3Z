# Ingress mutation contract sheet page: auto-map basis, port audience, and lease truth interface spec

## Purpose

Before an operator enables, disables, or audits automatic port mapping, they need one ordinary page that answers:

> what inbound lane is being requested, on which port, by what mechanism, with what audience widening, and with what current proof of mapping state?

This page exists so listening port, manual forwarding, automatic mapping, relay fallback, and router-side mutation do not remain scattered trivia.

## Core decision

Every serious ingress-widening or ingress-auditing surface must open one first-class **Ingress mutation contract sheet**.

The sheet owns:

- current listening-port basis
- requested ingress policy
- automatic-mapping posture
- mapping-state truth
- widened audience ceiling
- strongest safe sentence
- stronger rejected sentence

## Fixed page order

1. ingress claim header
2. port and mechanism ledger
3. audience-widening card
4. lease-truth card
5. next-safe action rail

### 1) Ingress claim header

Show at minimum:

- subject / seat / runtime scope
- current ingress class (`manual only`, `auto-map allowed`, `auto-map requested`, `mapping observed`, `unknown`)
- strongest safe sentence
- stronger rejected sentence

Example safe sentence:

- `This seat may request automatic mapping for listening port 51413, but live router acceptance has not yet been freshly proven.`

### 2) Port and mechanism ledger

Render rows for each serious ingress mechanism:

- listening port
- manual forwarding expectation
- automatic UPnP / NAT-PMP request posture
- relay fallback if direct ingress fails
- proxy constraints that would nullify or narrow inbound directness

Each row shows:

- current state
- source plane (`share`, `seat`, `config`, `runtime observation`, `external proof`, `unknown`)
- intended effect
- proof freshness

### 3) Audience-widening card

This card is mandatory.
Show:

- who may newly reach the seat if mapping succeeds
- whether widening is LAN-only, known-peer-only, internet-capable, or unknown
- whether discovery still depends on helper lanes separate from ingress itself
- strongest safe sentence after success

### 4) Lease-truth card

Show mapping-state truth as one of:

- `not requested`
- `request allowed but not attempted in this session`
- `request attempted; result unknown`
- `mapping observed`
- `mapping suspected stale`
- `mapping removal requested; removal not yet proven`

Each state row carries:

- observation time
- proving mechanism
- claim ceiling
- next proof path

### 5) Next-safe action rail

Only show actions that preserve meaning, such as:

- `Review auto port-map change`
- `Inspect route provenance`
- `Test direct inbound proof`
- `Record external router witness`
- `Disable automatic mapping`

## Rules

### Rule 1 — automatic mapping never appears as a lone checkbox truth

The same surface that lets the operator request mapping must also show port, audience, mechanism, and proof ceiling.

### Rule 2 — mechanism and proof stay separate

`enabled` does not equal `mapped`, and `mapped once` does not equal `mapped now`.

### Rule 3 — ingress widening never hides helper dependence

The page must still disclose whether discovery and transfer rely on tracker, relay, proxy, or predefined-host lanes even if direct ingress succeeds.

### Rule 4 — stronger rejected sentence is mandatory

At least one tempting overclaim must remain visible.

Example rejected sentence:

- `This seat is definitely reachable directly from all intended peers.`

## Acceptance criteria

A later operator can:

- tell which listening port is in play
- tell whether automatic mapping is only allowed, already attempted, or freshly proven
- tell what audience may have widened if it succeeds
- tell which other route helpers still matter
- tell what proof is still missing for a stronger claim
