# Typed artifact card page: scope, ceiling, and target world interface spec

## Purpose

Once an imported artifact has been classified, the operator still needs one stable answer to:

> what exact world does this artifact touch, how far does its authority reach, and what can it never do?

This page turns that answer into one ordinary reusable surface.

## Core decision

Every typed artifact family that can lead to a live join, claim, or custody action must expose one first-class **Typed artifact card**.

That card is the semantic home of:

- artifact identity
- world / subject scope
- authority ceiling
- target world
- expiry / budget / freshness
- non-effects

The product must not make operators open several downstream pages merely to learn what the imported artifact is *for*.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. artifact identity strip
2. scope and target-world card
3. authority ceiling card
4. time / budget / freshness card
5. non-effects card
6. next reviewed route card

### 1) Artifact identity strip

Show:

- canonical artifact family
- stable artifact identifier or fingerprint when safe to expose
- import carrier used
- issuer / source hint when known
- parse confidence

The strip should answer: **what exact typed artifact am I looking at?**

### 2) Scope and target-world card

Show:

- whether the artifact affects one seat, one subject, many future subjects, or one custody node
- target world or family name when known
- whether the artifact creates membership, claims a subject, or lands ciphertext
- strongest target mismatch risk

Examples:

- `joins seat to linked family`
- `claims subject Finance/Quarterly`
- `creates ciphertext-only custody for subject Media/Archive`

The operator should be able to answer: **what does this artifact touch?**

### 3) Authority ceiling card

Show:

- strongest positive power granted
- strongest power explicitly not granted
- whether approval or later target review still gates use
- whether rights are broad, narrow, revocable, or posture-dependent

Example contrasts:

- identity-link: broad family availability, but may trigger takeover review
- subject-claim: narrow subject scope, but permission may still vary
- encrypted-custody: may seed ciphertext, but no ordinary plaintext authority on destination

The operator should be able to answer: **what can this artifact do, and what can it never do?**

### 4) Time / budget / freshness card

Show when known:

- expiry
- use budget
- issuance time
- observed freshness
- whether staleness changes safety or only convenience

Rules:

- unknown expiry must remain visible as unknown
- lack of budget data must not be mistaken for infinite authority
- stale preview must warn when deeper review may have changed since issuance

### 5) Non-effects card

This section is mandatory.
Show explicit non-effects such as:

- does not by itself prove requester identity
- does not by itself choose target path
- does not by itself guarantee empty-seat safety
- does not by itself produce plaintext on ciphertext-only seat
- does not by itself widen authority beyond this family

The operator should be able to answer: **what tempting inference would be false here?**

### 6) Next reviewed route card

Show the strongest honest onward page:

- `Identity join`
- `Claim lane`
- `Encrypted custody setup flow`
- `Unsupported artifact explanation`

Also show why that page, not another one, is the correct next route.

## Acceptance criteria

This spec is satisfied when:

- every typed artifact exposes scope and ceiling before commitment
- the page says what the artifact cannot do, not only what it can do
- family-wide, subject-wide, and ciphertext-custody scopes are visibly different
- the strongest onward review page is explicit and justified
