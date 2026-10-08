# Artifact issuance receipt page: family, ceiling, expiry, and successor boundary interface spec

## Purpose

This receipt exists because portable authority artifacts are easy to misremember later.
Operators need one durable object that says exactly what was issued, with what ceiling, and whether it created or replaced an epoch.

## Core decision

Every exported invite, key, link, QR-backed artifact, or successor artifact must emit an **Artifact issuance receipt**.

## Required receipt fields

### A. Identity

- receipt id
- issued-at timestamp
- issuing seat
- reviewed surface
- carrier options offered

### B. Artifact family

- artifact family
- native / derived / successor status
- direct subject or seat-family scope

### C. Ceiling and path

- strongest embedded ceiling
- approval requirement
- onward-share ceiling
- recipient binding class

### D. Lifetime

- expiry class
- expiry instant if fixed
- use/click budget if relevant
- exhaustion behavior

### E. Continuity

- same-epoch or successor-epoch verdict
- prior artifact / epoch reference when relevant
- fork-risk verdict at issuance time
- retirement plan reference when relevant

### F. Language guard

Store together:

- strongest safe sentence
- stronger forbidden sentence

## Example safe sentences

- `As issued, this artifact could only begin a reviewed subject-access claim; it did not itself prove writer access had been granted.`
- `As issued, this successor artifact created a new access epoch while older artifacts still required explicit retirement.`
- `As issued, this artifact was bound only loosely to an intended recipient and should be treated as bearer-style until consumed.`

## Anti-confusion rules

### Rule 1 — carrier is not the family

The receipt must preserve the artifact family separately from whether it was shown as QR, copied as text, or sent by another lane.

### Rule 2 — ceiling is not result

If later approval was required, the receipt may not sound as though final access had already been granted.

### Rule 3 — successor boundaries must survive memory drift

If the issuance created a successor epoch, the receipt must keep the old/new boundary visible.

### Rule 4 — lifetime semantics must survive

Expiry, exhaustion, and freshness limits must remain visible even after the operator forgets the issuing dialog.

## Compact row contract

A compact receipt row should preserve:

1. artifact family
2. scope phrase
3. ceiling phrase
4. lifetime phrase
5. epoch phrase
6. strongest safe sentence fragment

Example:

```text
subject-access artifact · design subtree · writer ceiling after approval · expires in 3 days / 1 remaining claim · successor epoch / old artifact still live pending retirement · safe to say this was an approval-bearing invite, not an immediate grant
```

## Acceptance criteria

A later operator can:

- reconstruct what was issued
- distinguish artifact family from export carrier
- tell whether approval was still required
- see expiry and exhaustion truth
- see whether the issuance created a successor boundary or stayed in the same epoch