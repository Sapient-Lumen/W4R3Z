# Path identity contract sheet page — rendered name, raw form, canonical basis, and peer horizon

## Purpose

Show, in one durable place, the exact path-identity facts the operator may rely on before renaming, adopting, restoring, or approving a cohort-visible name.

This page exists to answer:

- `what name is the operator seeing?`
- `what exact raw form is being compared?`
- `which canonicalization rules are in force?`
- `is this safe only locally, or across the whole peer horizon?`

## Required sections

### 1. Subject header

Must show:

- subject and current parent path
- rendered basename
- operation lane (`rename`, `adopt`, `restore`, `replay`, `ingress`, `repair`, `other`)
- reviewed peer horizon
- current validity verdict (`safe`, `guarded`, `blocked`, `unknown`)

### 2. Name forms block

Render separate rows for:

- **Rendered name**
- **Raw stored form**
- **Canonical comparison form**
- **Peer-rewritten or substituted form** (when applicable)

Each row must publish:

- current value
- provenance
- whether it is stable across the reviewed horizon
- whether it is sufficient for equality decisions by itself

### 3. Canonical basis block

Must show:

- case-sensitivity posture in the reviewed horizon
- Unicode normalization posture
- invalid-symbol / forbidden-suffix posture
- rewrite or substitution posture
- whether these rules are subject-local, seat-local, or horizon-wide

### 4. Equivalence class block

Must classify the candidate as one of:

- `same rendered and same raw form`
- `same rendered but different raw form`
- `different rendered but canonical collision`
- `local-only valid`
- `peer rewrite expected`
- `blocked due to invalid or unsafe form`

### 5. Horizon safety block

Must distinguish:

- safe on current seat only
- safe across current connected peers
- safe across reviewed intended cohort
- unsafe because at least one peer horizon would rewrite, collide, or reject
- unknown because peer/path facts are incomplete

### 6. Strongest safe sentence

Examples:

- `This rename is safe only on the current seat; the reviewed cohort contains a case-insensitive peer that would collide.`
- `These two names render the same to humans but differ at raw Unicode form.`
- `The current policy would rewrite or reject this path on part of the cohort.`

### 7. Blocked stronger sentence

Examples:

- `The filenames are definitely identical because they look the same.`
- `Local filesystem acceptance means cohort-safe identity.`
- `Rendered name alone is enough to prove safe equality.`

## Interaction rules

- copying/exporting a summary must preserve both rendered and canonical basis fields
- any blocked or guarded verdict must link to a dedicated review page
- cohort horizon must stay visible near the primary action
- this page must not hide normalization or substitution rules under advanced disclosure

## Receipt obligations

Any receipt derived from this page must preserve:

- reviewed name forms
- canonical basis
- horizon safety verdict
- strongest safe sentence
- blocked stronger sentence
