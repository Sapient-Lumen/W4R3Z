# Resilio completion, freshness, peer horizon, and hidden-lag fragmentation evaluation

## Decision for AnonSync

Borrow Resilio's candor that completion claims are always relative to a horizon and to background work.
Do **not** clone the present Resilio contract for `done`, `synced`, `green`, `last transferred`, or `peer count`.

## Why this pass matters

Current official Resilio materials still make one ordinary operator question — `is this actually complete and fresh, relative to whom, and with what remaining debt?` — depend on several pages instead of one owned interface family.

The useful truths are real:

- the desktop main view still says a green checkmark means files are synced with **all connected peers**, not necessarily all known peers or all intended peers
- the same desktop main view still says `X of Y peers` means online peers out of total peers including offline, and that peers offline for 7 days get disconnected according to a power-user-configurable rule
- troubleshooting still tells the operator to inspect peer lists, queue state, warnings, and history separately when `not all files are synced`
- background-ops docs still say hidden work such as hashing, merging, scanning, dedup-copy, reading, and writing can be active even when the user only sees a generic warning that internal tasks are taking time
- change-detection docs still say visibility of new work depends on filesystem notifications, periodic rescans every 600 seconds by default, or manual rescan
- historic-but-still-live UI lineage in the changelog still shows surrogate columns such as `Date synced` and `Last transferred`, which are observability aids rather than durable completion proofs

## The non-clone problem

Those truths are useful.
The page shape is not.

Present-day Resilio still externalizes too much meaning into documentation archaeology:

- `green` speaks only about connected peers
- `X of Y` speaks about peer horizon, but with expiration and offline aging rules hidden elsewhere
- `last transferred` speaks about observed activity, not necessarily freshness against all intended peers
- internal background work can continue under generic warning language
- detection delay can come from notification loss, rescans, storage class, or explicit power-user settings

So one ordinary operator answer still requires reconstructing:

1. the **peer horizon** being claimed
2. the **offline debt** that remains outside the connected set
3. the **detection lag** that may hide unsurfaced local work
4. the **background work debt** that may keep a folder non-final even after transfer quiets down
5. the **proof ceiling** of any `complete` or `fresh` sentence

## AnonSync product stance

AnonSync should instead own completion and freshness as one page family:

- a **Completion boundary contract sheet** that states the exact peer horizon and proof ceiling
- a **Completion claim review** that previews which peers, seats, and offline debt are in or out of the sentence
- a **Freshness proof** that explicitly includes local detection lag and hidden background work
- a **Stale peer debt watch** that tracks who is outside the current completion horizon and why
- a **Completion lineage receipt** that preserves the horizon, proof basis, invalidators, and the stronger rejected sentence

## Hard decisions now locked

1. `Complete` is always **scoped**, never global by implication.
2. `Fresh` is not inferred from transfer quiet or a green icon alone.
3. `Connected-peer completion` and `known-peer completion` are different claims.
4. Offline expiration/hiding policy must never silently shrink the meaning of historical completeness.
5. Hidden background work and detection latency are part of completion truth, not debug trivia.
6. Durable receipts must preserve the strongest safe sentence and the stronger rejected sentence.
