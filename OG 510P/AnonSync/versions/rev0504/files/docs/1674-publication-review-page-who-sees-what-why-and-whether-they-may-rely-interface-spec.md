# Publication review page — who sees what, why, and whether they may rely

## Purpose

This page is the operator workspace for deciding whether a proposed or existing publication surface is honest for each viewer.
It exists so the archive can distinguish `they can see it` from `they are entitled to rely on it for this action`.

The page must answer:

> given the current act state, viewer eligibility, redaction policy, dispute posture, and publication history, what exact view should each audience receive now and what reliance remains blocked?

## Mandatory review sections

### A. Viewer posture section

- all candidate viewer classes
- current eligibility for each viewer
- whether eligibility is direct, mirrored, delegated, or disputed
- nearest weaker publication sentence already earned
- next stronger publication sentence blocked

### B. View-fidelity section

- full-content view availability
- redacted view availability
- metadata-only view availability
- encrypted-host-only presence if applicable
- withheld fields and exact reason for withholding
- whether the same event appears differently across viewers

### C. Reliance routing section

For each viewer class show:

- current view class
- current reliance class
- strongest sentence that viewer may act on
- stronger sentence still blocked
- whether the viewer may onward-cite or only internally consume
- exact event that would widen or narrow the viewer's reliance permission

### D. Publication-conflict section

- viewer disputes about completeness or accuracy
- overexposure risk route
- underexposure risk route
- retraction route
- supersession route
- emergency protective publication route
- adjudicator escalation route

### E. Outcome section

- strongest publication sentence honest now
- strongest reliance sentence honest now
- stronger publication or reliance sentence still blocked
- next decisive publication event expected
- exact audiences still excluded or narrowed

## Required route labels

- `internal only`
- `participant view`
- `redacted external`
- `public summary`
- `adjudicator full view`
- `metadata only`
- `encrypted host only`
- `retract and republish`
- `supersede with narrower view`
- `reliance blocked`

## Required comparisons

The review must keep these comparisons explicit:

- `can see` vs `may rely`
- `may rely operationally` vs `may rely for irreversible decision`
- `same principal on another device` vs `new audience`
- `unreadable custody` vs `publication`
- `historical trace exists` vs `current publication still stands`

## Failure modes the page must prevent

- mistaking owner, peer, or linked-device visibility for a finished publication contract
- mistaking notification receipt for permission to rely on the underlying claim
- letting a redacted summary silently impersonate the decision-grade full view
- forgetting that superseded or retracted statements may remain visible in trace while no longer safe to rely on
- forgetting that some audiences may deserve existence notice without semantic detail

## Stronger-sentence guard

The review may say `the affected participant may see the redacted notice and may rely on the response deadline, but only the adjudicator may rely on the underlying creditor-evidence attachments`.
It may not say `everyone who needs to know has the full story` until the publication rows actually support that stronger sentence.
