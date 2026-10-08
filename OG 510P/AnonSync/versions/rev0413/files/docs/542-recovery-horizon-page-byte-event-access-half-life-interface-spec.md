# Recovery horizon page: byte witness, event witness, and access half-life interface spec

## Purpose

This page answers one ordinary operator question:

> what recovery evidence still exists right now, how long is it likely to remain meaningfully usable, and from which surfaces can I still reach it?

The page exists because `recoverable` is not a boolean.
It decomposes into at least:

- whether prior bytes still exist
- whether event/authorship witness still exists
- whether the present seat or surface can reach either
- whether policy or size ceilings excluded capture in the first place
- when the strongest safe sentence is about to weaken

## Core decision

Every serious sync product must own one first-class **Recovery horizon** page.
That page is the semantic home of:

- byte-witness horizon
- event-witness horizon
- per-seat / per-surface reachability
- policy exclusions
- strongest current recovery sentence
- next impending horizon cliff

The operator must not have to infer recovery durability from hidden archives, generic history tabs, mobile caveats, or uninstall folklore.

## Primary page layout

The page always renders the same regions in the same order:

1. subject strip
2. current-horizon answer card
3. byte-witness horizon table
4. event-witness horizon card
5. access-half-life card
6. policy-exclusion card
7. horizon recommendation card
8. recent horizon receipts
9. expert details drawer

### 1) Subject strip

Show:

- subject path / object label
- current live posture (`healthy`, `missing`, `replaced`, `deleted-live`, `conflicted`, `history-only`)
- strongest horizon verdict (`fully-recoverable`, `recoverable-with-gaps`, `bytes-only-window`, `event-only-window`, `expiring-soon`, `no-known-recovery`)
- safest next action
- next known expiry or access cliff

The strip should answer `what is the current recovery shape and what is about to get worse first?`

### 2) Current-horizon answer card

Show:

- whether recoverable prior bytes are currently known
- whether event / authorship witness is currently known
- whether the acting seat can directly inspect, export, or replay
- the strongest honest sentence the product can make now
- the next weaker sentence that will apply after the nearest cliff

This card should answer `what can I honestly say right now, and what will stop being true next?`

### 3) Byte-witness horizon table

Each row represents one known or plausible byte witness.
Show columns for:

- seat label
- witness class (`prior-version`, `deleted-copy`, `conflict-copy`, `rename-continuity`, `manual-export`, `unknown`)
- access class (`desktop-ui`, `filesystem-only`, `web-surface`, `connector`, `no-current-surface`)
- retention source (`default`, `custom-policy`, `manual-preserve`, `unknown`)
- available-until estimate
- expiry confidence (`exact`, `policy-derived`, `inferred`, `unknown`)
- replay suitability (`live-replay`, `local-restore`, `export-only`, `not-suitable`)

This table should answer `which byte witnesses still exist and how long does each one plausibly remain usable?`

### 4) Event-witness horizon card

Show:

- history/event lanes currently available for this subject
- horizon for actor / chronology evidence
- whether the event lane is complete, partial, adjacent, or absent
- whether bytes outlive event witness or vice versa
- the strongest actor sentence still supported

This card should answer `how long will the explanation remain as strong as the bytes?`

### 5) Access-half-life card

Show:

- whether the current surface can open the witness directly
- whether another seat class or client class is needed
- known platform cliffs (`ios-no-archive-access`, `mobile-short-ttl`, `sd-card-no-archive`, `desktop-only-history`, `hidden-control-folder-only`)
- whether uninstall / app removal / cleanup would strand or reveal the witness differently

This card should answer `does the evidence still exist in practice for this operator, or only in theory on some other surface?`

### 6) Policy-exclusion card

Show:

- whether version capture was disabled, expired, size-blocked, or manually pruned
- whether cleanup or uninstall left hidden residue
- whether policy changed after the event and therefore narrowed later evidence
- one honest language substitution (`not captured`, `expired`, `present but unreachable here`, `residue survives app removal`)

This card should answer `did the evidence vanish, or was it never eligible or no longer reachable?`

### 7) Horizon recommendation card

Show only the strongest honest next action:

- `Recover now before byte witness expires`
- `Join event witness now before authorship window closes`
- `Switch to desktop seat for access`
- `Preserve export because only filesystem reach remains`
- `Review retention mutation before accepting future decay`
- `Stop; no credible recovery horizon remains`

## Non-negotiable rules

### Rule 1 — bytes and events must have separate horizons

The product may not blur byte recoverability with authorship/event retention.

### Rule 2 — access reach must stay explicit

If evidence exists only on disk or only through another seat class, the page must say so directly.

### Rule 3 — strongest sentence must degrade explicitly

When the nearest cliff passes, the product must know and preview the weaker sentence that remains.

## Honest outputs

The page may conclude:

- `Recoverable prior bytes still exist on two desktop witnesses for about 18 days, but actor evidence will age out sooner.`
- `A byte witness likely still survives in hidden control storage, but this surface cannot inspect it; switch hosts or preserve a manual export.`
- `No prior version was ever captured because the object exceeded the versioning ceiling.`
