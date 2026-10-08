# Estate certification lineage receipt page: certified scope, exclusions, and revocation boundary interface spec

## Purpose

After a certification is published, the next operator still needs one durable receipt that says what exact scope is certified, what remains explicitly excluded, how fresh the proof is, and what revokes the certificate.

## Receipt contract

This receipt is the handoff object for estate-level confidence.
It is not a victory memo.
It is a statement of certified scope, excluded scope, freshness horizon, and revocation boundary.

## Fixed page order

1. **Receipt header**
2. **Certified-scope card**
3. **Exclusions card**
4. **Freshness card**
5. **Claim-ceiling-and-revocation card**
6. **Handoff sentence**

### 1) Receipt header

Show:

- certification id
- receipt time
- certifying owner
- certification outcome
- included scope summary
- excluded scope summary

### 2) Certified-scope card

Required rows:

- included subject ids or cohorts
- included worlds or surfaces
- proof completeness for certified scope
- linked campaign ids
- next mandatory review

### 3) Exclusions card

Required rows:

- excluded subject ids or cohorts
- why each is outside the certificate
- whether each exclusion is tolerated or blocking for broader claims
- owner
- expiry
- next action

### 4) Freshness card

Required rows:

- witness families used
- oldest qualifying evidence timestamp
- freshness horizon
- next expiry time
- renewal requirement

### 5) Claim-ceiling-and-revocation card

Required rows:

- strongest safe certified sentence now
- exact scope of that sentence
- broader blocked sentence
- what would unlock it
- revocation triggers
- weaker sentence that survives after revocation or expiry

Hard rule:

The receipt must state the revocation boundary even when the certificate is currently healthy.

### 6) Handoff sentence

Format:

> `This receipt certifies [strongest safe certified sentence now] for [exact scope of that sentence], fresh through [next expiry time]. It remains unsafe to say [broader blocked sentence] because [excluded subjects / missing proof] remain outside the certified scope. This certificate is revoked if [revocation triggers].`

## Explicit anti-goals

Do not:

- turn a bounded certificate into a universal claim
- omit explicit exclusions because they were acceptable at the time
- hide freshness horizon after publication
- issue a receipt without revocation triggers

## Why this page exists

Because the archive should never again need a detective to determine what exactly was certified and what event quietly invalidated that confidence later.
