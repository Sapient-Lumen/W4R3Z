# Current-sentence lineage receipt page — committed sentence, consumer scope, and rollback exposure

## Purpose

This receipt is the concise audit artifact for the current operative sentence.
It exists so a later reviewer can see, in one place, which sentence was merely authorized, which sentence was actually current, for whom it was current, and what rollback exposure still survived.

## Mandatory receipt fields

- case identifier
- source promotion receipt identifier
- strongest sentence promotion-authorized
- strongest sentence actually current
- currentness rung
- lower sentence still operative for any residual cohort
- required consumer families
- current consumer families
- lagging, stale, or excluded consumer families
- commit lane
- trusted current-since timestamp
- rollback authority
- rollback trigger set
- strongest blocked stronger sentence
- next strengthening trigger
- next weakening trigger

## Required compact summaries

The receipt must be able to summarize outcomes like:

- `stronger sentence authorized but not yet current; lower sentence remains operative for all consumers`
- `stronger sentence current for internal execution cohort only; public consumers still rely on the lower sentence`
- `stronger sentence current for all required consumers under commit rule C4`
- `stronger sentence rollback-armed because one required consumer family is stale`
- `stronger sentence rolled back globally after contradictory subscriber evidence surfaced`
- `prior current sentence superseded by a newer stronger sentence while preserving historical current interval`

## Receipt invariants

- the receipt never upgrades `promotion-authorized` into `current` by omission
- the receipt never hides whether currentness is partial or universal
- the receipt never hides the surviving lower sentence for excluded or lagging consumers
- the receipt never hides rollback exposure
- the receipt always preserves the next known strengthening and weakening triggers

## Stronger-sentence ceiling

This receipt may support the sentence `this stronger row is or is not currently operative for the named consumer scope`.
It may not support any still-stronger downstream irreversible sentence unless the gate for that stronger row separately agrees.

