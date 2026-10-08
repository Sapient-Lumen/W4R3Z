# Restoration waterfall timeline page — partial relief, missed slices, probation, and release events

## Purpose

This page is the chronology view for the full life of a multi-creditor restoration case once debt exists but repair must happen in stages.
It must let operators answer:

> when was each creditor tier opened, when did each relief slice land, when were slices missed or waived, and when did probation finally release or tighten again?

## Mandatory event types

### A. Waterfall-formation events

- debt opened
- waterfall mode chosen
- creditor tiers fixed
- probation opened
- cross-tier waiver requested

### B. Relief-slice events

- reserve slice applied
- named-creditor slice applied
- cohort slice applied
- pro-rata distribution recalculated
- severity ordering revised
- residue converted into narrowed future entitlement

### C. Failure-or-waiver events

- relief slice missed
- active tier regressed
- waiver granted
- waiver denied
- probation tightened
- all new bursts blocked

### D. Release events

- tier 1 cleared
- tier 2 cleared
- tier 3 cleared
- final residue cleared
- probation downgraded to manual-only
- probation lifted
- clean restoration released

## Required timeline annotations

Each event must carry:

- actor
- authority quality
- prior tier state
- resulting tier state
- creditor consequence
- strongest sentence gained or still blocked

## Required overlays

The page must support overlays for:

- relief slices by tier over time
- reserve floor vs restored floor over time
- named-creditor residue over time
- probation posture over time
- recurrence count within policy window

## Failure modes the page must prevent

- showing only the debt-opening moment and hiding the longer partial-repair life
- making one tier-clear event look like global restoration when other tiers remain open
- allowing a waiver to look identical to an ordinary relief slice
- allowing probation lift to appear earlier than the evidence supports

## Stronger-sentence guard

The page may say `tier 1 cleared on this date`.
It may not say `clean restoration released on this date` unless the timeline separately shows the last required tier-clear or typed waiver event plus the actual probation-lift event.