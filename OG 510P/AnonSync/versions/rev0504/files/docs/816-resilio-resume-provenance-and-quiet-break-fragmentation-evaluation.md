# Resilio resume-provenance, quiet-break, and reactivation ambiguity evaluation

## Purpose

The archive already has strong page families for:

- local pause truth
- paused-label origin drift
- quiescence review
- quiet cohort agreement
- opportunity / lateness honesty
- re-entry after dormancy

What it still lacked was one ordinary operator answer that current Resilio docs still do not own tightly enough:

> after we earned a reviewed quiet claim, **who broke it, by what authority, and was that break expected or surprising?**

Current official Resilio docs are candid that pause is partial and mostly local.
The next problem is that resume / reactivation authority is still also mostly local, clock-driven, or implicit.
That is a stronger reason not to clone them than a dislike of wording.

## What current Resilio still gets right

Current official docs still deserve credit for preserving the ingredients of reactivation instead of pretending there is one universal freeze / unfreeze bit.

The load-bearing truths they still publish include:

- the current `How to pause syncing` article still says pause stops only bits download/upload, while zero-sized files and deletions still sync and new files are still rescanned and indexed
- that same article still says resuming is done by repeating the same local pause steps, and Global Pause / Resume still lives on the current device window
- the current `Running Sync on schedule` article still says the scheduler is just a grid of local hour rules, where empty cells mean Sync can work at full bandwidth and `Paused` is only a speed-zero local state with residual delete/indexing behavior still alive
- the current `Sync Preferences` article still places Start Sync on startup, Global Pause / Resume, and Scheduler together in ordinary local preferences rather than a reviewed shared maintenance object
- the current `Does Sync work in background?` article still says desktop hidden runtime keeps working, Linux can run headlessly, and Android may still work in background unless task killers or platform constraints stop it
- the still-published historical changelog still records `Sync stopping indexing if folder paused`, which shows this boundary between paused appearance and live behavior has been subtle enough to fail in production
- the maintained v3 line still runs through `3.1.2.1076`

That is good candor.
Resilio is still honestly preserving the facts that reactivation may come from local resume, schedule boundary, ongoing background runtime, or simple absence of a true shared freeze.

## What current Resilio still should not be cloned

### 1. A quiet claim can be earned, but there is still no first-class quiet-break object

Once an operator has a reviewed local or cohort quiet claim, the next serious question is no longer `can I pause something?`
It becomes:

- who broke the quiet claim first
- what exactly counted as the break
- whether the break was expected because the declared window ended
- whether the break was surprising because a seat resumed early or never truly matched
- what sentence remains safe **after** the break

Current Resilio docs still expose ingredients of those answers.
They still do not give one product-owned object for **quiet-break provenance**.

### 2. Resume authority is still reconstructed from local controls and time boundaries

Current docs still make the operator merge several surfaces:

- manual resume / Global Resume on the current device
- scheduled cells whose `Paused` periods end at clock boundaries
- background runtime that stays active when UI is hidden or headless
- startup / runtime preferences that bring the local seat back alive without a cohort receipt
- counterpart seats whose quiet state may never have matched in the first place

That leaves no one reviewed answer to:

> was this break authorized, expected, expired-on-time, surprising, or still ambiguous?

### 3. The product still does not tell the operator whether the old quiet receipt survived, expired, or was actively broken

Current docs explain controls.
They still do not emit one durable reviewed receipt that says:

- prior quiet claim id
- achieved stillness class before break
- breaking seat
- break authority class
- expected vs unexpected verdict
- strongest safe sentence now
- exact condition for issuing a successor quiet claim

That is still too much memory burden for maintenance, evidence, and migration work.

### 4. Quiet tenure is still socially remembered rather than product-owned

For real operations, operators often need to know:

- how long the cohort actually stayed quiet before the break
- whether the break occurred before the maintenance action finished
- whether the break happened inside the declared window or after expiry
- whether coverage collapsed completely or only partially

Current official docs still do not give one page family for **quiet tenure and break chronology**.
The operator still has to remember it.

## Why this matters for AnonSync

AnonSync should not clone a contract where a quiet claim is easier to issue than to invalidate honestly.

The product now needs one stable answer to four follow-up questions:

- **break truth** — what exact event ended or weakened the quiet claim?
- **authority truth** — was that event manual, scheduled, runtime-driven, expiry-driven, or ambiguous?
- **coverage-collapse truth** — did the break affect one seat, the full cohort, or only the strongest sentence?
- **language truth** — what sentence is safe now, and what stronger sentence became forbidden the moment the break occurred?

That is a real product seam, not support prose.

## Replacement pages in this revision

This revision adds four fixed pages:

- `817` — Quiet break page
- `818` — Resume authority review page
- `819` — Quiet break timeline page
- `820` — Quiet break receipt page

Together they make `who broke the quiet claim, by what authority, and what claim survived?` explicit before AnonSync lets `resume`, `window ended`, or `still quiet enough` become durable language.

## Concrete product stance

Borrow from Resilio:

- candid admission that pause and scheduled quiet are partial, local, and origin-bearing
- candid admission that hidden/background runtime may still keep the seat alive
- candid preservation of clock-driven scheduler behavior instead of pretending it is a durable maintenance object
- candid separation of local controls from shared proof

Do not clone from Resilio:

- leaving quiet-break provenance implicit in a remembered click, a clock boundary, or an inferred background return
- forcing the operator to reconstruct whether the break was expected or surprising
- letting an old quiet receipt linger without an explicit supersession / invalidation object
- leaving no durable record of quiet tenure, first break event, and post-break safe sentence

## Evaluation summary

Resilio still deserves credit for preserving the ingredients of reactivation honestly.
But the current product/docs path still leaves a missing object:

> there is no first-class reviewed answer to `who broke this quiet claim, when, and did they have the authority we expected?`

AnonSync should therefore make **resume provenance and quiet-break review** a first-class product object.
Every serious maintenance window, evidence capture, migration cut, or destructive repair should publish prior quiet basis, break authority, break chronology, strongest surviving sentence, and successor-claim boundary before the product treats reactivation as understood.
