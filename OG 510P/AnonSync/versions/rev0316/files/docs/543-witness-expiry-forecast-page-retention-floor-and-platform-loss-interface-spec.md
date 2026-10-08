# Witness expiry forecast page: retention floor, platform loss, and survival ladder interface spec

## Purpose

This page answers one ordinary operator question:

> what specific recovery evidence is at risk next, why, and what is the least-destructive way to preserve it before it decays?

The page exists because recovery failure is often not a sudden mystery.
It is a forecastable horizon event caused by time, policy, platform reach, cleanup, or storage class.

## Core decision

Every recovery-aware sync product must own one first-class **Witness expiry forecast** page.
That page owns:

- upcoming byte-witness expiry
- upcoming event-witness expiry
- platform or surface loss
- cleanup / uninstall residue danger
- preservation ladder and urgency class

The operator must not discover evidence decay only after the best witness has already disappeared or become unreachable.

## Page layout

The page always renders the same regions in the same order:

1. forecast strip
2. at-risk witness list
3. cliff-detail card
4. preservation ladder
5. residue-vs-loss card
6. commitment preview
7. historical forecast receipts

### 1) Forecast strip

Show:

- subject path
- highest-urgency cliff
- time-to-cliff band (`now`, `hours`, `day`, `days`, `weeks`, `unknown`)
- witness type at risk
- strongest safe preservation action

### 2) At-risk witness list

Each row shows one at-risk witness with:

- seat label
- evidence type (`byte`, `event`, `join`, `access-surface`)
- risk source (`ttl-expiry`, `size-exclusion`, `surface-loss`, `cleanup`, `uninstall`, `manual-prune`, `policy-change`, `unknown`)
- likely consequence
- urgency
- reversible / irreversible classification

### 3) Cliff-detail card

Show:

- what exactly will be lost at the cliff
- what weaker witness remains afterward
- what stronger claim will become forbidden afterward
- whether the cliff is policy-derived, heuristic, or already overdue

### 4) Preservation ladder

Show the least-destructive ladder in order, for example:

1. inspect on reachable surface now
2. export byte witness side-by-side
3. preserve event witness / receipt
4. extend retention through reviewed mutation
5. move to longer-lived witness host
6. accept loss and downgrade future claims

### 5) Residue-vs-loss card

Show:

- whether hidden residue may outlive app removal or UI visibility
- whether loss is true deletion versus surface inaccessibility
- whether cleanup would destroy the easiest witness or merely hide it from current tooling
- whether future support / forensic access would still exist

### 6) Commitment preview

Show exactly what a chosen preservation action would change:

- bytes kept or exported
- event witness retained or not
- storage cost
- future claim floor improvement
- new residue introduced

## Non-negotiable rules

### Rule 1 — urgency must be tied to a specific witness

The page may not say `history expiring soon` without naming which witness and which claim would weaken.

### Rule 2 — surface loss is not the same as byte loss

The product must distinguish inaccessible-from-here from destroyed-everywhere.

### Rule 3 — the least-destructive ladder comes first

The product should recommend preservation actions in escalating order of cost and side effect.

## Honest outputs

The page may conclude:

- `Actor evidence will age out in 9 hours; preserve the joined receipt now even though byte witnesses remain longer.`
- `Only one mobile witness remains and its retention floor is near-term; export bytes or move the witness to a longer-lived host.`
- `App removal will not necessarily erase hidden archive residue; choose between deliberate cleanup and explicit preservation rather than assuming uninstall equals erasure.`
