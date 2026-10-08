# Artifact family router page: link, identity, claim, and custody separation interface spec

## Purpose

`270` already defines one ordinary import lane for handoff health and typed preview.
What still remained under-owned was the stronger verdict that comes immediately after parse:

> what family of authority is this artifact, and which deeper review page is the honest next stop?

This page exists so copied/scanned/opened material is never treated as a generic `key or link` blob.

## Core decision

Every imported artifact that can plausibly represent more than one family of authority must pass through one first-class **Artifact family router** page.

That page owns:

- carrier versus artifact-family separation
- parse confidence
- family-level consequence preview
- admissible deeper routes
- route receipt

It routes onward to deeper pages such as:

- `277` Identity join
- `375` Claim lane
- `492` Encrypted custody setup flow
- another typed intake page when the artifact is unsupported or malformed

## Fixed page order

Every artifact-family router page must render the same sections in the same order:

1. family verdict strip
2. carrier and parse card
3. family cards
4. route consequences card
5. admissible next routes
6. route receipt promise

### 1) Family verdict strip

Show:

- imported carrier (`deep link`, `browser-open`, `paste`, `qr`, `file`, `unknown`)
- best current family verdict
- parse confidence
- strongest honest next action

Allowed family verdicts:

- `identity-link artifact`
- `subject-claim artifact`
- `encrypted-custody artifact`
- `ambiguous family`
- `unsupported artifact`
- `malformed artifact`

The operator must be able to answer: **what kind of authority-bearing object did the product most likely receive?**

### 2) Carrier and parse card

Show:

- current carrier
- whether the carrier is wrapper-only or authority-bearing itself
- canonical artifact identity if known
- fields learned with high confidence
- fields still unknown
- strongest reason for any ambiguity

Rules:

- carrier and artifact family must always be shown as different facts
- `QR` and `browser wrapper` must never be mistaken for distinct governance families when they merely encode another artifact
- parse uncertainty must remain visible rather than collapsing to silent best guess

### 3) Family cards

Render one card per plausible family.
Each card shows:

- family name
- scope (`one seat`, `one subject`, `linked family`, `ciphertext node`, etc.)
- strongest downstream consequence
- strongest blocking caveat
- best supporting evidence

Required family cards:

#### Identity-link card

Show:

- whether linked-family adoption is expected
- whether future-subject fanout is part of the family
- whether local-world takeover or successor review may be required

#### Subject-claim card

Show:

- target subject or subject family when known
- permission / approval posture if known
- whether the result is one subject bind rather than whole-family join

#### Encrypted-custody card

Show:

- whether ciphertext-only custody is implied
- whether manual posture / strict target review is required
- whether ordinary plaintext capability is absent on the destination

The operator must be able to answer: **which family explains the artifact best, and what other plausible families were ruled out?**

### 4) Route consequences card

Before onward routing, show one-row previews for each admissible next route:

- route name
- what new world or subject would be affected
- whether future subjects are implicated
- whether target-path review is required
- whether capability ceilings are created
- whether another receipt will be emitted later

The operator must be able to answer: **what happens if I continue on each plausible route?**

### 5) Admissible next routes

Allowed action rows include:

- `Review identity join`
- `Review subject claim`
- `Review encrypted custody setup`
- `Open unsupported artifact explanation`
- `Stop and clear intake`

The primary action must be the safest truthful route, not the shortest route.

### 6) Route receipt promise

A route receipt must preserve:

- carrier used
- parse confidence
- family verdict
- competing families considered
- route chosen
- onward page entered

The operator must be able to answer later: **what did the product believe this artifact was before I continued?**

## Compact row contract

A trustworthy compact rail should preserve the following order:

1. carrier
2. family verdict
3. strongest consequence
4. strongest caveat
5. next action

Example:

- `Pasted text · Encrypted-custody artifact · Will create ciphertext-only seat if admitted · Target hygiene and recovery posture still unreviewed · Review encrypted custody setup`

## Acceptance criteria

This spec is satisfied when:

- copied/scanned/opened material is never presented as an untyped `key or link`
- carrier and artifact family remain separate facts
- identity-link, subject-claim, and encrypted-custody routes are visibly different before commitment
- the router always leaves a receipt even when the operator stops
