# Relationship-versus-seat authority page — linked identity, explicit grant, and derived ceiling interface spec

## Purpose

This page answers one ordinary question when role meaning is ambiguous:

> is this seat authoritative because of who it is related to, because of an explicit grant, because it derives from a stronger source, or because there is no native narrower role available here?

The page exists because role surprises are often basis surprises.
An operator needs one place that separates relationship class from seat authority.

## Core decision

Whenever a subject-seat role could be misunderstood, the product must render one first-class **Relationship-versus-seat authority** page.

The page owns:

- relationship class
- authority basis ladder
- counterfactual role comparison
- proof for any intentional narrowing
- strongest safe sentence now

## Fixed page order

1. basis summary strip
2. relationship class card
3. authority basis ladder
4. counterfactual matrix
5. non-authority proof card
6. receipts

### 1) Basis summary strip

Show:

- subject
- seat
- relationship class: `same-identity-family`, `remote-peer-grant`, `local-derivative`, `opaque-custody`, `unknown`
- current role
- one honest next action

### 2) Relationship class card

This card publishes:

- whether the seat belongs to the same personal constellation
- whether the current role came from a remote party's explicit grant
- whether the seat is a derivative or ceiling-limited child of another seat
- whether multiple bases are active at once

### 3) Authority basis ladder

Render strongest-to-weakest basis rows such as:

- linked-family owner default
- explicit owner/writer/observer grant
- derived narrowing from a source seat
- opaque or custody-only ceiling
- detour artifact standing in for a role request

Each row must show whether it is active, merely possible, or rejected.

### 4) Counterfactual matrix

For each relevant basis, show:

- resulting seat role
- approval/share powers
- continuity sentence
- whether this would still be the same subject lineage
- what stronger or narrower claim would become possible

This matrix exists so the operator can answer: **what would change if this seat were narrow by grant, by self-policy, or by workaround instead?**

### 5) Non-authority proof card

If the seat is currently narrower than the family default, this card must publish:

- proof that the narrowing is intentional
- whether it is native or workaround-based
- whether later operators may honestly call it `observer`, `receive-only`, `derived narrow`, or only a weaker sentence

### 6) Receipts

Receipts must preserve:

- relationship class
- winning authority basis
- rejected bases where relevant
- current claim ceiling

## Public object

### `relationship_seat_authority_explainer`

Fields:

- `relationship_seat_authority_explainer_id`
- `subject_ref`
- `seat_ref`
- `relationship_class`
- `current_role`
- `basis_rows[]`
- `counterfactual_rows[]`
- `narrowing_proof`
- `claim_ceiling`
- `generated_at`

## Non-negotiable rules

### Rule 1 — same person is not the same authority explanation

If the seat is powerful because it is linked, the page must say that explicitly.
It must not pretend that an explicit grant produced the same truth.

### Rule 2 — workaround-based narrowing must remain second-class in language if proof is weaker

If the current narrow posture exists only through a workaround artifact, the page must not over-claim native seat-role semantics.

### Rule 3 — counterfactuals must be honest about lineage

If one alternative would change subject lineage or artifact family, the matrix must say so.

## Honest outputs

The page may conclude:

- `Current authority basis: linked-family owner default. No separate explicit grant is required for this seat to act with owner-grade power.`
- `Current narrower posture is proven by a derived ceiling, not by a direct owner-to-observer grant mutation.`
- `Counterfactual: a native same-subject observer role would preserve lineage more cleanly than the present workaround.`

It may not flatten those truths into `owner`, `my device`, or `read only`.
