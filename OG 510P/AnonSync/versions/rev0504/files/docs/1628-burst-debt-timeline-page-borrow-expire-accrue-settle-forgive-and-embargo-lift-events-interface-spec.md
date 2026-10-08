# Burst debt timeline page — borrow, expire, accrue, settle, forgive, and embargo-lift events

## Purpose

This page is the chronology view for the full afterlife of a burst exception once debt, embargo, and restoration readiness matter.
It must let operators answer:

> when did the urgent exception begin, when did debt become explicit, when did settlement or forgiveness occur, and when was the claimant actually allowed to return to ordinary standing?

## Mandatory event types

### A. Exception-origin events

- burst requested
- burst authorized
- burst activated
- burst renewed
- burst expired
- burst withdrawn

### B. Debt-formation events

- debt opened
- creditor set fixed
- debt amount revised
- overdue threshold crossed
- repeated-burst warning opened
- new-burst embargo activated

### C. Settlement-path events

- immediate payback completed
- staged settlement plan opened
- staged milestone missed
- staged milestone completed
- debt converted into narrowed future award
- forgiveness requested
- forgiveness granted
- forgiveness denied

### D. Restoration events

- reserve restored
- harmed claimant relieved
- embargo downgraded to manual-review-only
- embargo lifted
- ordinary entitlement restored
- regression reopened debt

## Required timeline annotations

Each event must carry:

- actor
- authority quality
- prior state
- resulting state
- creditor or claimant consequence
- strongest sentence gained or still blocked

## Required overlays

The page must support overlays for:

- active live consumption vs debt state
- reserve floor vs restored floor
- harmed-claimant set over time
- embargo posture over time
- recurrence count within policy window

## Failure modes the page must prevent

- showing only active urgency and hiding the longer debt tail
- making restored reserve look like restored claimant relief when those happen at different times
- allowing forgiveness to look identical to settlement
- allowing a lifted embargo to appear earlier than the evidence actually supports

## Stronger-sentence guard

The page may say `urgent exception ended on this date`.
It may not say `normal standing returned on this date` unless the timeline separately shows debt retirement or typed forgiveness plus the actual embargo-lift event.