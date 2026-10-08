# Burst debt contract sheet page — creditor class, due window, and new-exception embargo

## Purpose

This page is the canonical object for any debt that survives a burst-borrow exception.
It must answer the next operator question after burst authorization and payback begin:

> is the claimant already restored to ordinary good standing, or does unpaid burst debt still bind future eligibility, stronger normalcy claims, or claimant relief?

## Primary questions the page must answer

1. What exception created this debt?
2. Who or what is still owed restoration?
3. What exact debt remains open, and in what class?
4. Does open debt block renewal or any new burst authorization?
5. What proof is required before ordinary entitlement can be spoken again?

## Required fields

### A. Source exception block

- burst exception link
- claimant name
- ordinary award amount
- borrowed extra-room amount
- exception class
- open time and expiry time
- reason for exception

### B. Creditor and harm block

- creditor class (`protected-reserve`, `named-claimants`, `promise-cohort`, `mixed`, `system-wide-headroom`)
- harmed claimant set
- harmed promise or dispatch set
- reserve floor delta
- strongest surviving harmed-neighbor sentence
- debt owner of record

### C. Debt shape block

- debt class (`room-restoration`, `time-priority-restitution`, `narrowed-follow-on-award`, `mixed-restoration`, `manual-writeoff-candidate`)
- principal amount to restore
- aged amount still open
- due window
- overdue threshold
- settlement method allowed
- restructuring allowed (`yes`, `no`, `manual-only`)

### D. Embargo and eligibility block

- new-burst embargo posture (`none`, `same-claimant-blocked`, `all-exceptions-blocked`, `manual-review-only`)
- renewal posture (`allowed-once`, `blocked-while-open`, `executive-only`, `forbidden`)
- ordinary-entitlement sentence ceiling while debt is open
- restoration gate checklist
- strongest blocked stronger sentence

### E. Current settlement state block

- current settlement state
- last settlement witness
- next required action
- next forced review time
- settlement authority needed

## Required states

The page must keep these states separate:

- `no-burst-debt`
- `debt-open-current`
- `debt-open-overdue`
- `debt-partially-settled`
- `debt-restructured`
- `debt-disputed`
- `debt-forgiveness-pending`
- `debt-forgiven-with-consequence`
- `debt-settled-awaiting-verification`
- `restoration-ready`
- `ordinary-good-standing-restored`

## Page obligations

- never let `exception closed` impersonate `debt retired`
- always name the creditor set instead of collapsing all harm into one generic backlog story
- always show embargo posture on the same page as remaining debt
- always show what proof is still missing for restored good standing
- always link backward to burst authorization and forward to settlement review, restoration proof, and receipt

## Stronger-sentence guard

The page may say `burst exception ended but debt remains open`.
It may not say `claimant restored to normal entitlement` until the restoration gate is actually cleared or a typed forgiveness rule explicitly permits the weaker restored sentence that follows.