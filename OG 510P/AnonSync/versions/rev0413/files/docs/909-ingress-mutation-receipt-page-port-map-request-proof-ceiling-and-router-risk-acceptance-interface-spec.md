# Ingress mutation receipt page: port-map request, proof ceiling, and router-risk acceptance interface spec

## Purpose

After a serious ingress-widening or ingress-narrowing action, later operators need durable truth that does not require rediscovering preferences, config files, or router folklore.

## Core decision

Every serious automatic-mapping or ingress-mutation change must emit one first-class **Ingress mutation receipt**.

The receipt owns:

- resulting ingress policy
- listening port basis
- mapping request / observation status
- accepted router-risk posture
- strongest safe sentence
- stronger rejected sentence
- supersession boundary

## Fixed page order

1. receipt header
2. port and mutation ledger
3. proof-ceiling card
4. accepted-risk card
5. supersession and reopen triggers

### 1) Receipt header

Show:

- receipt id
- seat / runtime / subject scope
- executed time
- resulting ingress class
- strongest safe sentence

### 2) Port and mutation ledger

Render rows for:

- listening port after apply
- automatic mapping requested / blocked / unsupported / disabled
- manual-forwarding expectation
- relay/helper consequence
- current observed mapping status

Each row includes winning source plane and whether the row widened, narrowed, or preserved prior posture.

### 3) Proof-ceiling card

This card is mandatory.
Show:

- whether direct inbound reach is merely more likely, freshly observed, stale, or not proven
- whether router mutation was requested versus externally witnessed
- strongest forbidden sentence

Example forbidden sentence:

- `The router definitely exposes this seat on the internet right now.`

### 4) Accepted-risk card

Show:

- whether router-side-effect warning was reviewed
- compatibility confidence at decision time
- safer alternative declined, if any
- acknowledgement text or class

### 5) Supersession and reopen triggers

Show at minimum:

- what later action supersedes this receipt
- what events weaken its truth (port change, runtime restart, router change, disable request, proxy policy shift)
- whether a mapping-lease watch should now be monitored

## Rules

### Rule 1 — the receipt preserves claim ceiling, not just preference state

A later operator must know what was safe to say, not only what was clicked.

### Rule 2 — risk acceptance remains attached to the receipt

Infrastructure-facing warnings must survive after the modal is gone.

### Rule 3 — supersession is explicit

The receipt must say which later ingress or route change invalidates it.

## Acceptance criteria

A later operator can:

- tell whether automatic router mutation was requested, disabled, or only inferred
- tell which port and mechanism were involved
- tell what proof ceiling remained after apply
- tell what collateral risk warning was accepted
- tell what later event supersedes the receipt
