# Parity-debt proof page: temporary accepted delta, baseline rebind, and claim ceiling interface spec

## Purpose

After the archive learned how to review aging return debt, it still needed one proof page that records the winning branch honestly.

## Core decision

AnonSync must expose one first-class **Parity-debt proof** page whenever a return delta is reaffirmed, exactly restored, promoted to a successor baseline, or reopened.

## Fixed page order

1. **Proof header**
2. **Winning branch card**
3. **Proof basis card**
4. **Baseline rebind card**
5. **Claim ceiling card**
6. **Proof sentence**

### 1) Proof header

Show:

- proof id
- linked return-delta id
- linked aging review id
- winning branch
- proof time
- approver
- resulting status

### 2) Winning branch card

Required rows:

- previous delta status
- chosen branch
- resulting state
- immediate follow-up obligation
- expiration / retirement behavior

Supported `winning_branch` values:

- `temporary-reaffirmed`
- `exact-restore-completed`
- `successor-baseline-promoted`
- `claim-narrowed-stable`
- `reopened`

### 3) Proof basis card

Required rows:

- observed evidence
- targeted proof steps performed
- unresolved caveats
- why the branch is honest now
- what evidence would overturn it later

Supported `proof_basis_class` values:

- `configuration-and-observation`
- `targeted-reconciliation-proof`
- `merge-audit-proof`
- `rights-and-topology-proof`
- `insufficient-proof-reopen`

Hard rule:

The page must record why this branch is honest, not merely what button was pressed.

### 4) Baseline rebind card

This card explains whether the old baseline survives.
Required rows:

- old baseline sentence
- new baseline sentence if any
- baseline relation
- effective-from time
- subjects affected
- whether old baseline is retired or remains for other subjects

Supported `baseline_relation` values:

- `old-baseline-restored`
- `old-baseline-kept-delta-still-open`
- `successor-baseline-created`
- `baseline-split`
- `baseline-abandoned-reopen`

Hard rule:

A successor baseline must be created explicitly.
A changed active state may not silently inherit baseline authority.

### 5) Claim ceiling card

Required rows:

- strongest safe sentence now
- stronger blocked sentence still not safe
- next proof if stronger sentence should return later
- downgrade trigger

### 6) Proof sentence

Format:

> `This proof records [winning_branch]. The subject is now honest to describe as [strongest safe sentence now]. It is not honest to describe as [stronger blocked sentence still not safe] until [next proof / none if restored].`

## Required interactions

### A) `Retire debt`

Available only for exact restore or successor baseline promotion.

### B) `Keep debt open`

Available only for temporary reaffirmation.
Requires expiry.

### C) `Create successor baseline`

Requires baseline relation and affected-subject scope.

### D) `Send to reopen`

Links proof directly to the reopened object.

## Anti-goals

Do not:

- let proof pages read like success theater
- let `promoted baseline` happen without explicit old/new baseline relation
- let temporary reaffirmation masquerade as closure

## Why this page exists

Because once a changed return matures, the product must say exactly whether the old parity returned, a successor baseline was deliberately adopted, or the debt proved too dishonest to keep.
