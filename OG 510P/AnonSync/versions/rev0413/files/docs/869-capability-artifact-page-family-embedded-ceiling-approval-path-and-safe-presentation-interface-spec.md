# Capability artifact page: family, embedded ceiling, approval path, and safe presentation interface spec

## Purpose

This page answers one ordinary question:

> what kind of authority artifact is this, what power is embedded in it already, and what still requires later approval or review?

The page exists because operators should not need folklore about prefixes, URL fragments, or delivery carrier to understand an authority object.

## Core decision

Every authority-bearing token or exportable invite object must render one first-class **Capability artifact** page.
That page owns:

- artifact family
- embedded capability ceiling
- approval path
- continuity scope
- safe-display rules
- strongest safe sentence

## Fixed page order

1. artifact strip
2. family card
3. capability ceiling card
4. approval path card
5. continuity scope card
6. safe presentation card
7. receipt / lineage rail

### 1) Artifact strip

Show:

- artifact family
- candidate subject or seat family
- current carrier
- freshness state
- strongest next-safe action

Artifact families must include at minimum:

- `seat-link`
- `subject-access`
- `subject-observer`
- `subject-writer`
- `subject-owner-like`
- `opaque-custody`
- `ciphertext-custody`
- `unknown / untrusted`

### 2) Family card

Publish:

- whether the artifact targets one subject, a future subject family, or a seat-link relationship
- whether the artifact is direct authority or merely an approval-seeking claim
- whether the artifact can be re-shared or only consumed
- whether the artifact is native, imported, derived, or superseded

### 3) Capability ceiling card

Show the strongest authority this artifact could ever yield if all later approvals succeed.
Examples:

- observe only
- read current and future bytes
- write upstream
- share onward
- hold ciphertext only
- join a linked seat family

The page must also show stronger forbidden interpretations.

### 4) Approval path card

Show one explicit path:

- `self-sufficient bearer artifact`
- `requires review by eligible approver`
- `requires seat-link acceptance`
- `requires stronger proof before evaluation`
- `blocked / invalid / stale`

Also show whether later approval may narrow the artifact below its ceiling.

### 5) Continuity scope card

Publish:

- current subject scope
- future-arrival scope
- descendant scope
- whether consuming this artifact preserves current continuity, joins an existing lineage, or begins a successor epoch

### 6) Safe presentation card

Because many artifacts are portable secrets or live invitations, the page must control how they are shown:

- fully hidden by default
- redacted preview allowed?
- exportable as text / QR / local handoff?
- may be copied again after issuance?
- screenshot-safe or not?

The page must distinguish `inspect artifact` from `reveal secret`.

### 7) Receipt / lineage rail

Show linked issuance receipt, supersession receipt, or intake receipt when available.

## Rules

### Rule 1 — artifact family must not be inferred from carrier alone

A browser-opened thing may still be a subject invite, a seat-link claim, or an invalid artifact.
Carrier alone is never enough.

### Rule 2 — ceiling must not impersonate result

An artifact that can produce writer access after approval must not be described as if writer access already exists.

### Rule 3 — seat-link and subject-access stay separate

An artifact that joins a seat family must not be shown with the same grammar as an artifact that grants one subject.

### Rule 4 — inspect and reveal are separate actions

The page must permit semantic inspection without forcing full secret exposure.

## Acceptance criteria

A later operator can:

- tell what artifact family is in play
- tell what authority ceiling is embedded versus still pending review
- distinguish carrier from meaning
- inspect the artifact safely without overexposing secrets
- reopen the right continuity or approval workflow from this page