# Detection grade page: notification coverage, rescan fallback, and freshness ceiling interface spec

## Purpose

This page answers:

> what exact change-detection coverage exists for this path right now, what fallback is carrying freshness when notifications fail, and what ceiling should operators believe when they read `up to date`?

The page exists because a reachable path with rescan-only detection is not the same contract as a live-watched path.

## Core rule

Every path with degraded, uncertain, or protocol-limited change detection must compile to one first-class **Detection grade** page before the product claims freshness confidence.
That page owns:

- notification coverage
- rescan policy and cadence
- restart dependency if present
- freshness ceiling
- detection receipt

## Primary layout

The page always renders the same regions:

1. detection verdict
2. notification-coverage card
3. fallback / cadence card
4. freshness-ceiling card
5. receipt and follow-on links

### 1) Detection verdict

Show:

- verdict label: `live-watched`, `watch-partial`, `rescan-grade`, `restart-sensitive`, `unknown`
- strongest honest one-line summary
- proof basis
- one safest next action

### 2) Notification-coverage card

Show:

- whether filesystem notifications are expected to work here
- whether they are presently observed working
- strongest downgrade cause (`SMB<3`, `UNC workaround`, `watcher exhaustion`, `unknown remote fs`, `config choice`)
- lock or subtree caveats that could still hide updates

The operator must be able to answer: **are live notifications actually carrying freshness here?**

### 3) Fallback / cadence card

Show:

- scheduled rescan interval
- whether restart can discover changes that live watching missed
- manual rescan availability
- whether rescan is disabled
- strongest implication for publication delay

The operator must be able to answer: **what is catching changes when live watching does not?**

### 4) Freshness-ceiling card

Show:

- freshest believable claim (`immediate`, `next rescan`, `after restart`, `unknown`)
- path or subject scope of that claim
- last supporting evidence timestamp
- strongest unresolved doubt

The operator must be able to answer: **how fresh can `up to date` honestly mean on this path?**

### 5) Receipt and follow-on links

Link to:

- Network path class
- Protocol discipline
- Network subject admission

After any accepted action, emit a receipt that preserves:

- detection grade before and after
- rescan cadence reviewed
- restart dependency acknowledged or removed
- resulting freshness ceiling
- remaining caveats

## Honest outputs

This page may conclude:

- `rescan-grade only · SMB notifications unavailable on this path`
- `UNC service workaround active · updates may appear only after rescan or restart`
- `live-watched local path · immediate freshness claim acceptable`
- `detection basis unknown · do not trust fresh verdict without probe`

It may not collapse these into one generic `Sync may take some time` note.

## Rules

### Rule 1 — detection grade must sit next to freshness claims

Do not let the client say `up to date` without being able to reveal whether that verdict is live-watched or rescan-grade.

### Rule 2 — fallback is part of the contract

Rescan cadence, restart dependency, and manual rescan availability are not troubleshooting trivia.
They are part of the subject's public freshness contract.

### Rule 3 — disabled rescan must widen honesty

If rescans are disabled on a path that lacks reliable notifications, the product must downgrade freshness claims immediately.

### Rule 4 — unknown coverage blocks confidence

If the product cannot prove notification coverage or fallback policy, it must publish `unknown` instead of optimistic freshness.

## Event language

Use explicit phrases such as:

- `live notifications absent; next believable publication point is scheduled rescan`
- `restart-sensitive freshness on UNC-under-service path`
- `manual rescan widened evidence; live watcher still unproven`
- `freshness ceiling unknown because detection basis cannot be established`

Avoid vague lines such as:

- `may sync later`
- `check again soon`
- `updates delayed`

## Non-clone reason

Current official Resilio docs are usefully candid that SMB/NFS/UNC and similar paths can lose live notifications and fall back to rescan or restart.
But the operator still has to stitch together that truth from generic freshness notes and service troubleshooting.
AnonSync should instead expose one Detection grade page where coverage, fallback, freshness ceiling, and proof basis stay adjacent.
