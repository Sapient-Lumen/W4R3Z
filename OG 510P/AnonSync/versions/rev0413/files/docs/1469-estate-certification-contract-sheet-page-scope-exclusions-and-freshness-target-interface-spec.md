# Estate certification contract sheet page: scope, exclusions, and freshness target interface spec

## Purpose

After the archive learned how to settle many parity debts through convergence campaigns, it still needed one ordinary page for the next operator question:

> what exact estate scope are we trying to certify, what is explicitly excluded, and what witness freshness is required before the stronger sentence is allowed?

## Core decision

AnonSync must expose one first-class **Estate certification contract sheet** whenever an operator is trying to say that a meaningful estate, cohort, profile family, or governed surface is now in bounds again.

## Fixed page order

1. **Certification header**
2. **Target-sentence card**
3. **Covered-scope card**
4. **Explicit-exclusions card**
5. **Witness-and-freshness card**
6. **Decision sentence**

### 1) Certification header

Show:

- estate certification id
- linked baseline / profile / policy family
- linked convergence campaign ids
- certification owner
- created time
- next decision gate
- current certification status
- strongest currently safe sentence

Supported `current_certification_status` values:

- `drafting`
- `evidence-collecting`
- `awaiting-review`
- `certified-bounded-scope`
- `certified-family-scope`
- `blocked`
- `expired`
- `revoked`
- `retired`

Hard rule:

A certification effort may not be represented only as a vague `all clear` note once it is being used to upgrade estate-level confidence.

### 2) Target-sentence card

This card states what stronger sentence the certification is trying to earn.
Required rows:

- intended certified sentence
- current weaker safe sentence
- target certification scope
- minimum witness classes required
- freshness window required before certification
- broader blocked sentence if this scope is still too narrow

Supported `target_certification_scope` values:

- `single-policy-family`
- `single-linked-estate`
- `selected-bounded-subset`
- `single-world-only`
- `mixed-explicit-subset`

Hard rule:

The card must explicitly say what scope is being certified.
`estate healthy` is illegal without an enumerated scope boundary.

### 3) Covered-scope card

This card defines what is inside the certificate.
Required rows:

- included subject count
- included subject ids or cohorts
- inclusion rule
- included worlds or surfaces
- proof horizon for covered scope
- required completeness level

Supported `inclusion_rule` values:

- `all-known-subjects-in-family`
- `all-known-subjects-in-world`
- `all-subjects-settled-by-linked-campaigns`
- `explicit-bounded-selection`
- `manually-certified-subset`

Hard rule:

Coverage must be enumerable.
A certification target may not rely on `roughly all the important ones`.

### 4) Explicit-exclusions card

This card defines what is outside the certificate and why.
Required rows:

- excluded subject ids or cohorts
- exclusion class per item
- whether exclusion is allowed or blocking
- owner
- expiry or rereview date
- path to inclusion, successor certification, or reopen

Supported `exclusion_class` values:

- `not-yet-settled`
- `different-world`
- `unsupported-surface`
- `stale-witness`
- `temporary-waiver`
- `intentionally-out-of-scope`
- `reopened-problem`

Hard rule:

Every exclusion must remain visible next to the intended stronger sentence.
No silent scope trimming.

### 5) Witness-and-freshness card

This card defines what proof is acceptable.
Required rows:

- witness families required
- minimum freshness window
- oldest acceptable evidence age
- whether passive quiet time is sufficient
- revocation triggers armed at certification time
- downgrade sentence if freshness expires

Supported `witness_family` values:

- `settlement-proof`
- `attestation-proof`
- `live-health-proof`
- `topology-proof`
- `permission-or-rights-proof`
- `operator-reviewed-exception-proof`

Hard rule:

Freshness is part of the certification target, not a later footnote.

### 6) Decision sentence

Format:

> `This certification may target [intended certified sentence] for [target certification scope] only if [required witness families] are fresh through [freshness window] and the following exclusions remain explicitly bounded: [excluded cohorts]. Until then, the strongest safe sentence remains [current weaker safe sentence].`

## Required interactions

### A) `Narrow certification scope`

Lets the operator shrink the target scope without losing the excluded subjects.

### B) `Promote exclusion to blocker`

Turns a tolerated exclusion into a hard block for the stronger sentence.

### C) `Require fresh witness`

Raises the proof bar before certification can proceed.

### D) `Split separate certificate`

Moves a different world or lane into its own certification object instead of smuggling it into this one.

## Explicit anti-goals

Do not:

- let campaigns closing automatically mint an estate certificate
- let exclusions disappear into prose
- let freshness remain implied
- let `green enough` substitute for a scoped target sentence

## Why this page exists

Because once cleanup waves succeed, the next risk is not failure.
It is an oversized success claim.
