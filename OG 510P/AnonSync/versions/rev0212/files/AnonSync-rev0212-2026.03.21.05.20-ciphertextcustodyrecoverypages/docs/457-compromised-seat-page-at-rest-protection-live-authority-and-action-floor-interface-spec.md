# Compromised seat page: at-rest protection, live authority, and action floor interface spec

## Purpose

This page answers:

> what exactly makes this seat dangerous right now, and what is the safest immediate action floor?

The page exists because `offline`, `lost`, `stolen`, `unencrypted`, `linked`, and `owner` are not the same contract.

## Core rule

Every suspected or confirmed seat-compromise case must expose one first-class **Compromised seat** page before irreversible action.
That page owns:

- seat posture
- at-rest protection status
- strongest current authority claim
- first safe action floor
- strongest residual risk if the seat returns online

## Primary layout

The page always renders the same regions:

1. seat verdict
2. protection posture card
3. live-authority card
4. action-floor card
5. receipt and next reviews

### 1) Seat verdict

Show:

- seat label and seat lineage class
- incident posture: `suspected`, `probable`, `confirmed`
- custody posture: `present`, `missing`, `stolen`, `untrusted holder`, `unknown`
- strongest honest summary
- one safest next action floor

### 2) Protection posture card

Show:

- current at-rest protection verdict: `encrypted`, `unencrypted`, `unknown`, `mixed proof`
- evidence source or attestation used for that verdict
- what the verdict lowers or does not lower
- whether local possession still matters even if bytes are unreadable at rest

The operator must be able to answer: **is this seat's local storage itself the main problem, or is the remaining risk somewhere else?**

### 3) Live-authority card

Show:

- strongest current authority class: `none proven`, `local possession only`, `future updates possible`, `write authority`, `owner-class authority`, `unknown`
- whether the seat belongs to a linked cohort or holds separate shared grants only
- whether already-issued grants, linked-owner rights, or local decrypted copies widen the risk
- what the seat could still do if it returns online unchanged

The operator must be able to answer: **what can this seat still do right now or on next return?**

### 4) Action-floor card

Show:

- safest immediate action: `monitor only`, `freeze minimally`, `disconnect selected subjects`, `open containment lane`, `rotate cohort now`
- why broader actions are or are not justified yet
- what this first action does **not** solve
- explicit impossible actions such as `remote unlink unavailable` if that is the current truth

The operator must be able to answer: **what is the narrowest honest thing I can do now without lying to myself?**

### 5) Receipt and next reviews

Link directly to:

- Containment lane
- Rotation rebuild
- Residual authority

After apply, emit a receipt that preserves:

- protection posture used
- strongest live-authority claim
- chosen action floor
- residual-risk summary

## Honest outputs

This page may conclude:

- `encrypted missing seat; monitor and gather proof`
- `unencrypted linked owner seat; cohort-wide containment review required`
- `separate-grant seat; subject-local disconnect may be sufficient`
- `risk unclear; do not claim safety merely because seat is offline`

It may not collapse these into one generic `device issue` verdict.

## Rules

### Rule 1 — offline is not a safety verdict

The page must never let last-seen time impersonate cutoff.

### Rule 2 — protection posture must sit next to authority posture

A seat can be encrypted yet still require grant review; or unencrypted yet hold only local bytes. Those are different truths and must remain adjacent.

### Rule 3 — impossibility must be explicit

If the system cannot remotely sever a linked seat or cannot prove immediate cutoff, that limitation must be shown as first-class state.

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- whether the seat is protected at rest
- what the seat could still do if it comes online
- whether the seat's danger is local possession, live authority, or both
- what the safest immediate action floor is
- which stronger actions remain to be reviewed next

