# Promotion-lineage receipt page — gate basis, override authority, and blocked stronger sentences

## Purpose

This receipt is the concise audit artifact for the promotion verdict.
It exists so a later reviewer can see, in one place, whether the stronger sentence was still blocked, merely review-ready, auto-armed, promoted, override-promoted, or later demoted.

## Mandatory receipt fields

- case identifier
- stronger sentence under review
- source lower-sentence receipt identifier
- promotion rule version
- current promotion rung
- smallest honest current sentence
- strongest sentence actually authorized
- strongest blocked stronger sentence
- current blockers, if any
- automation state
- manual decision authority, if relevant
- override authority, reason, and expiry, if relevant
- debt, probation, or residue surviving the decision
- next strengthening trigger
- next weakening trigger

## Required compact summaries

The receipt must be able to summarize outcomes like:

- `stable-earned but stronger sentence still blocked because named promotion authority is missing`
- `manual-review ready; automation disabled because confidence floor is unmet`
- `stronger sentence auto-promoted under rule version R7 with no override debt`
- `stronger sentence override-promoted until 2026-03-25T12:00Z with probation and re-review preserved`
- `previously promoted stronger sentence later demoted after delayed-rescan warning surfaced`

## Receipt invariants

- the receipt never upgrades `stable-earned` into `promotion-authorized` by omission
- the receipt never hides whether automation was armed or merely allowed in principle
- the receipt never hides whether override was used
- the receipt never hides what stronger sentence remained blocked
- the receipt always preserves the next known demotion trigger

## Stronger-sentence ceiling

This receipt may support the sentence `this stronger row was or was not authorized under the current gate rule`.
It may not support any stronger downstream irreversible sentence unless the gate for that stronger row separately agrees.
