# Creditor authority contract sheet page — principal, representative, scope, and expiry

## Purpose

This page is the canonical object for the question:

> who may speak for each creditor, on what basis, with what scope, until when, and with what blocked stronger sentences if that authority is limited or stale?

It exists so the archive never has to smuggle settlement authority through device ownership, peer approval, folder Owner status, or operator folklore.

## Primary questions the page must answer

1. Which verified or contested creditor is this authority sheet attached to?
2. Is the speaker the principal creditor, a delegate, a role-based representative, a residual absorber, or only an observer?
3. What exact actions may that speaker take?
4. When does the authority expire, narrow, or require revalidation?
5. Which release, waiver, probation, or reopen sentences remain blocked because scope is limited?

## Required fields

### A. Source-creditor block

- source creditor claim contract sheet
- source restoration-waterfall or burst-debt case if present
- creditor principal name or cohort label
- current creditor verification class
- current strongest blocked clean-release sentence
- current future-burst posture

### B. Principal-and-interest block

- creditor principal type (`named-person`, `team`, `reserve`, `policy-cohort`, `manual-absorber`, `other`)
- harmed interest being represented
- amount or slice implicated
- whether principal is directly reachable now
- whether the principal itself has already confirmed the authority record

### C. Representative-roster block

For each representative the page must show:

- representative name or role label
- representative class (`self`, `delegated-agent`, `role-based-manager`, `system-policy-absorber`, `observer-only`, `expired-former-holder`)
- authority basis (`self-acting`, `signed-delegation`, `role-policy`, `court-or-governance-order`, `manual-emergency-assignment`, `unknown`)
- authority start time
- authority expiry time or rereview trigger
- current authority status (`valid`, `limited`, `pending-validation`, `expired`, `revoked`, `challenged`)

### D. Scope-and-ceiling block

Each representative must carry typed scope fields:

- may receive repayment acknowledgment (`yes` or `no`)
- may negotiate terms (`yes` or `no`)
- may accept partial settlement (`yes` or `no`)
- may accept settlement only up to cap (`uncapped`, `capped`, `none`)
- may waive residue (`yes`, `no`, `only-with-countersign`)
- may absorb unresolved residue into another bucket (`yes`, `no`)
- may lift probation (`yes`, `no`)
- may reopen or challenge closure (`yes`, `no`, `only-new-evidence`)
- strongest sentence currently allowed for this representative

### E. Validation-evidence block

- proof sources used (`principal-confirmation`, `delegation-instrument`, `role-directory`, `policy-text`, `case-ruling`, `manual-attestation`, `other`)
- freshness horizon for the authority proof
- counterevidence present (`no`, `yes-pending`, `yes-material`)
- identity continuity risk (`none`, `role-exit`, `relink`, `certificate-takeover`, `unknown`)
- exact event that would force revalidation

### F. Consequence block

- settlement actions currently unlocked
- settlement actions still blocked
- whether full release is blocked by scope
- whether waiver is blocked by missing authority
- whether reopen remains preserved despite partial settlement
- strongest blocked sentence that survives

## Required states

The page must keep these states separate:

- `principal-self-authorized`
- `delegate-valid-but-limited`
- `role-based-authority-pending`
- `partial-settlement-only`
- `waiver-not-authorized`
- `probation-lift-not-authorized`
- `expired-or-revoked-authority`
- `authority-challenged`
- `revalidation-required`
- `full-release-authorized`

## Required comparisons

The page must keep these comparisons explicit:

- `can describe harm` vs `can release harm`
- `can accept payment` vs `can waive residue`
- `can negotiate` vs `can close`
- `linked device owner` vs `creditor representative`
- `role still occupied` vs `authority still valid`

## Failure modes the page must prevent

- treating folder Owner status as automatic authority to extinguish a creditor claim
- treating a linked device as if it inherits every settlement power held by the principal
- treating partial-payment acknowledgment as full-release authority
- leaving revocation, role exit, or identity takeover outside the authority story
- allowing waiver language when only capped settlement authority exists

## Stronger-sentence guard

The page may say `delegate may accept reserve repayment but may not waive named-neighbor residue`.
It may not say `creditor fully released` until valid scope explicitly includes that stronger sentence.
