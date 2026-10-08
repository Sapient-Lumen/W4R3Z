# Estate certification proof page: certified scope, freshness, and revocation triggers interface spec

## Purpose

After a certification is shaped, the product needs one durable page that proves what scope is truly certified right now.
This is the page that decides whether the archive has earned a real stronger sentence, for what scope, and for how long.

## Page promise

This page must answer:

> what exact scope is certified now, what evidence supports it, how fresh is that evidence, what exclusions remain, and what event revokes this certificate later?

## Fixed page order

1. **Certification outcome header**
2. **Certified-scope proof card**
3. **Witness-freshness card**
4. **Claim-and-ceiling card**
5. **Revocation-watch card**
6. **Outcome sentence**

### 1) Certification outcome header

Show:

- certification id
- certification time
- certifying owner
- certified scope size
- excluded scope size
- current certification outcome

Supported `current_certification_outcome` values:

- `certified-bounded-scope`
- `certified-family-scope`
- `not-yet-certified`
- `expired`
- `revoked`
- `retired`

Hard rule:

A certification cannot be green if its freshness window has already expired.

### 2) Certified-scope proof card

Required rows:

- included subjects or cohorts
- excluded subjects or cohorts
- included worlds or surfaces
- excluded worlds or surfaces
- proof completeness for included scope
- proof ceiling for broader scope

Hard rule:

The card must enumerate what is inside and outside the certificate.
A universal sentence is illegal when exclusions remain.

### 3) Witness-freshness card

Required rows:

- witness families used
- freshest timestamp per family
- oldest qualifying timestamp across required families
- certification freshness window
- next freshness expiry time
- whether passive quiet time is carrying any family

Hard rule:

The oldest qualifying witness controls certification freshness unless a stronger family-specific rule says otherwise.

### 4) Claim-and-ceiling card

Required rows:

- strongest safe certified sentence now
- exact scope of that sentence
- broader blocked sentence
- what would unlock the broader sentence
- surviving weaker sentence after expiry or revocation
- downgrade path

Hard rule:

The broader blocked sentence must stay visible even when the bounded certificate is strong.

### 5) Revocation-watch card

Required rows:

- armed revocation triggers
- trigger class per item
- automatic downgrade on trigger
- re-certification requirement
- owner of watch response
- whether trigger affects all scope or bounded subset only

Supported `revocation_trigger_class` values:

- `freshness-expired`
- `new-exclusion-created`
- `subject-reopened`
- `world-fork-detected`
- `rights-drift-detected`
- `attestation-withdrawn`
- `topology-changed-beyond-proof`

Hard rule:

A certificate without explicit revocation triggers is incomplete.

### 6) Outcome sentence

Format:

> `This proof certifies [strongest safe certified sentence now] for [exact scope of that sentence] using [witness families used], fresh through [next freshness expiry time]. It remains unsafe to say [broader blocked sentence] because [excluded scope / missing proof]. This certificate is revoked if [armed revocation triggers].`

## Required interactions

### A) `Publish certificate`

Issues the certificate only for the proved scope.

### B) `Revoke certificate now`

Withdraws the stronger sentence immediately when a revocation trigger is observed.

### C) `Renew freshness`

Updates freshness only when the required witness families are truly renewed.

### D) `Downgrade to weaker sentence`

Preserves a smaller safe claim after expiry or revocation.

## Explicit anti-goals

Do not:

- let certification survive stale evidence silently
- let one witness family cover for another missing family without saying so
- let exclusions disappear from the proof once certification turns green
- let revocation become tribal knowledge instead of product state

## Why this page exists

Because a certificate is only useful if the next operator can tell exactly what it covers and exactly how it dies.
