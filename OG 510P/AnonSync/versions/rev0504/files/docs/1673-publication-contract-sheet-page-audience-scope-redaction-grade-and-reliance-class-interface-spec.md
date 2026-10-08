# Publication contract sheet page — audience scope, redaction grade, and reliance class

## Purpose

This page is the canonical declaration of who is allowed to see which version of a typed act and how heavily that view may be relied on.
It exists so the product can stop pretending that `shown somewhere`, `published`, and `decision-grade` are the same truth.

The page must answer:

> for this typed act or case object, which audience classes may receive which view, what is redacted for each of them, and what exact reliance class is honest for that audience?

## Mandatory audience classes

At minimum the page must expose these audience classes separately:

- internal operator
- principal / issuer
- directly affected participant
- delegated representative
- linked-device same-principal viewer
- external reviewer
- adjudicator / auditor
- public-summary viewer
- untrusted storage host

The implementation may add more classes, but it may not collapse them into one generic `viewer`.

## Mandatory blocks

### A. Audience-auth block

- viewer class
- why this viewer is eligible
- whether eligibility is direct, delegated, mirrored, derived, or adjudicated
- whether the viewer is entitled to semantic content, metadata only, existence only, or encrypted storage only
- whether the viewer may onward-share this view

### B. Redaction block

- redaction profile name
- actor identifiers shown
- evidence shown
- amounts or quotas shown
- timestamps shown
- fields intentionally hidden
- whether hidden fields are omitted, masked, bucketed, or replaced with explanatory text

### C. Reliance block

- operational-awareness class
- workflow-permitted class
- participant-decision class
- external-reference class
- adjudicator-grade class
- strongest sentence the viewer may rely on
- stronger sentence still blocked for this viewer

### D. Publication-lifecycle block

- draft state
- proposed state
- issued state
- published state
- retracted state
- superseded state
- disputed-publication state
- exact event that promotes or narrows a viewer's reliance class

### E. Lineage block

- source object for this publication
- who approved this publication surface
- why this viewer got this exact version
- which stronger fields were withheld
- supersession rule
- retraction rule
- evidence horizon after which reliance weakens

## Required comparisons

The page must keep these comparisons explicit:

- `visible` vs `published`
- `published` vs `reliance-grade`
- `same bytes shown` vs `same rights to rely`
- `linked device mirror` vs `separately entitled viewer`
- `encrypted storage present` vs `semantic access granted`

## Required badges

- `internal-only`
- `participant-visible`
- `redacted-external`
- `public-summary`
- `adjudicator-grade`
- `metadata-only`
- `encrypted-host-only`
- `retracted-publication`
- `superseded-publication`
- `reliance-blocked`

## Failure modes the page must prevent

- treating any UI-visible row or notification as if it were automatically a publishable claim
- treating linked-device visibility as equivalent to a separately adjudicated publication right
- treating a redacted view as if it necessarily supports the same reliance as the full view
- allowing encrypted or unreadable storage presence to impersonate semantic publication
- forgetting that a publication may remain operationally useful while being too weak for stronger decision claims

## Stronger-sentence guard

The page may say `the participant can see a redacted settlement proposal and may rely on it for response timing, but only the adjudicator-grade view may support final residue allocation`.
It may not say `published to all relevant viewers` unless the exact audience rows say that stronger sentence is true.
