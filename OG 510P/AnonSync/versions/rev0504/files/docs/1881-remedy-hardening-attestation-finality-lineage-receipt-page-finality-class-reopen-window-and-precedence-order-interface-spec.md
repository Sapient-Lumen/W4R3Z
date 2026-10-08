# Remedy-hardening-attestation-finality lineage receipt page — finality class, reopen window, and precedence order

## Why this receipt exists

Once a challenge has been ruled, later operators must not have to reconstruct from old screenshots, rotated logs, support memory, or current calm whether the ruling stayed reopenable, became final, or was superseded.
They need one durable receipt that says what sentence survived, how final it became, who could rely on it, and what later receipt or contradiction changed precedence.

## Receipt fields

- case identifier
- source challenge receipt identifier
- adjudicated surviving sentence
- current finality class
- current reliance audience class
- decisive witness durability grade
- same-world continuity result
- current reopen window or trigger set
- predecessor receipt identifier
- successor receipt identifier
- current precedence owner
- whether this receipt is historical only
- strongest blocked permanence sentence
- strongest blocked stronger sentence
- next evidence that would reopen the receipt
- next evidence that would strengthen the receipt

## Required receipt sentences

The receipt must be able to say things like:

- `this case was adjudicated, but the ruling remained reopenable through the stated horizon`
- `this receipt became final on the current record for the named audience only`
- `this predecessor-world receipt was superseded by a successor-world receipt and remains historical only`
- `the appeal window lapsed, but broader permanence language remains blocked because decisive evidence is not durable enough`
- `this narrowed sentence is non-reopenable at its floor even though the stronger pre-challenge sentence stays blocked`

## Precedence rules

The receipt must make these rules explicit:

- newer is not automatically stronger unless the receipt explicitly owns precedence
- successor-world repair cannot silently retro-validate predecessor-world certainty
- superseded receipts remain visible and citable as history, but not as current authority unless explicitly lane-limited
- a reopened receipt loses any permanence language until a new ruling class is earned

## Blocking rules

The receipt must never let later operators silently say:

- `case closed forever`
- `same ruling still governs` when a successor receipt displaced it
- `final for everyone` when audience limits remain
- `nothing changed after adjudication` when reopen, supersession, or historical demotion occurred
