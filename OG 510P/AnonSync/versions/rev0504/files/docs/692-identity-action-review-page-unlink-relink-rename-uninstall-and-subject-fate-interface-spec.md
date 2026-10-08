# Identity-action review page: unlink, relink, rename, uninstall, and subject fate interface spec

## Purpose

This page exists because identity-looking verbs are not always pure account verbs.
A seat can be asked to:

- unlink from a family
- create a fresh identity
- accept certificate takeover from another running seat
- uninstall after clearing local control

and those actions can change local subject governance or byte survival differently by class and platform.

The page must let an operator answer one blunt question without article archaeology:

> if I continue this identity action here, what local subjects leave governance, what bytes survive on this platform, and what safer preserve-first branch still exists?

## Core decision

AnonSync should make **identity-action review** first-class.
Every identity-changing action must publish, in one stable object:

- requested verb
- target identity outcome
- affected subject classes
- app-removal effect
- local-byte survival by platform
- preserve-first alternatives
- strongest safe sentence

## Fixed review order

Every identity-action review page should render the same sections in the same order:

1. **Verb now**
2. **Subject fallout**
3. **Platform-local byte fate**
4. **Continuity preserved / lost**
5. **Preserve-first alternatives**
6. **Claim ceiling**

### 1) Verb now

Show:

- requested verb: `unlink`, `fresh-identity`, `certificate-takeover`, `uninstall`, `unknown`
- initiating surface
- target seat/identity outcome
- whether the action is reversible, successor-only, or destructive

The operator must be able to answer: **what identity verb is actually being committed?**

### 2) Subject fallout

Show:

- affected subject classes present on this seat
- for each class: `unchanged`, `removed-from-governance`, `will-be-copied-in`, `will-require-manual-reclaim`, `unknown`
- whether the effect is app-only or wider

The operator must be able to answer: **which local subjects are changing governance state because of this verb?**

### 3) Platform-local byte fate

Show:

- current platform class
- local-byte fate: `stay-on-disk`, `app-only-removal`, `platform-delete-cliff`, `unknown`
- strongest platform reason
- whether another seat would be safer for this action

The operator must be able to answer: **what will happen to the local bytes on this platform?**

### 4) Continuity preserved / lost

Show separately:

- preserved continuity: local bytes, subject labels, history witnesses, linked relations, approvals, receipts
- lost continuity: identity lineage, active governance, remembered approvals, on-seat control state

The operator must be able to answer: **what continuity survives, and what definitely does not?**

### 5) Preserve-first alternatives

Offer safer branches, for example:

- `Preserve local bytes first`
- `Create a branch/export before unlink`
- `Move this action to a safer seat`
- `Keep identity unchanged`
- `Abort`

The operator must be able to answer: **what safer sequence is still available before I cross the line?**

### 6) Claim ceiling

Show:

- strongest safe sentence
- stronger forbidden sentence
- evidence timestamp
- main uncertainty if present

Examples:

- `This action changes seat identity and removes Advanced subjects from active governance on this seat, but local bytes remain on disk here.`
- `This action is unsafe on this platform because governed bytes would be deleted locally.`
- `This seat can complete the identity action only after you preserve the listed subjects elsewhere.`

## Main card

The subject/seat workspace should expose an **Identity action** card with:

- verb chip
- subject-fallout chip
- byte-fate chip
- preserve-first chip
- `Inspect identity action`

## Rules

### Rule 1 — identity verbs and subject fallout must stay adjacent

The page may not let `unlink` or `rename` stand alone if local subject governance changes with it.

### Rule 2 — platform-local byte fate must be explicit

The page may not reduce a platform delete cliff to generic removal language.

### Rule 3 — preserve-first alternatives must be real

If a safer export/branch/alternate-seat path exists, the page must show it before destructive commit.

### Rule 4 — one verb may not hide several survival stories

If a later operator could not tell `removed from app`, `still on disk`, and `deleted on this platform` apart from this page alone, the page is not explicit enough.

## Acceptance criteria

A later operator can:

- identify the exact identity verb being committed
- see which local subject classes are affected
- know whether bytes survive on this platform
- choose a preserve-first branch when safer
- quote one honest post-commit sentence without folklore
