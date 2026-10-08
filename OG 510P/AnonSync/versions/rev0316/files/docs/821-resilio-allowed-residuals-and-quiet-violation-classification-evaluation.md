# Resilio allowed-residuals, quiet-challenge, and break-vs-expected classification evaluation

## Purpose

The archive already has strong page families for:

- quiescence review
- residual activity matrices
- maintenance-grade quiet
- quiet cohort agreement
- quiet-break provenance
- successor quiet claims

What it still lacked was one ordinary operator answer that current Resilio docs still do not own tightly enough:

> after we earned a reviewed quiet claim, an event happened — **did quiet really break, or was this an allowed residual we should have expected?**

Current official Resilio docs are candid that pause is partial.
The next problem is that post-event judgment is still left to operator memory.
That is a stronger reason not to clone them than a mere dislike of wording.

## What current Resilio still gets right

Current official docs still deserve credit for preserving the surviving effects instead of pretending `Paused` means universal stillness.

The load-bearing truths they still publish include:

- the current `How to pause syncing` article still says pause stops only bits download/upload while zero-sized files still sync, file deletion still syncs, and new files are still rescanned and indexed so share size can increase on paused peers
- the current `Running Sync on schedule` article still says scheduled `Paused` means upload/download speed are zero while zero-sized files still sync, deletions still sync, new files are still rescanned and indexed, and paused peers may still upload to other non-paused peers while not downloading themselves
- the current `Sync Preferences` article still presents Global Pause / Resume and Scheduler as ordinary local controls rather than a reviewed maintenance object with a later challenge classifier
- the still-published historical changelog still records `Sync stopping indexing if folder paused`, which shows the seam between visible pause and surviving activity has been subtle enough to fail in production
- the maintained v3 line still runs through `3.1.2.1076`

That is good candor.
Resilio is still honestly warning the operator that visible quiet may coexist with specific surviving event classes.

## What current Resilio still should not be cloned

### 1. A later event still has no product-owned classifier

Once an operator sees a new event during a quiet window, the next serious question is no longer `what does pause mean in theory?`
It becomes:

- was this delete or zero-byte/control event actually expected under the prior quiet receipt?
- did share-size growth come from allowed rescanning/indexing, or did it prove a stronger break?
- is this counterpart upload evidence a real quiet failure, or only proof that the cohort never earned the stronger sentence in the first place?
- what sentence survives now?

Current Resilio docs still expose ingredients of those answers.
They still do not give one product-owned object for **break-vs-expected classification**.

### 2. The operator still has to remember the old matrix when the new event arrives

Current docs explain pause behavior at the moment of setup.
They still do not help later when a real event appears.
The operator still has to remember, from previous article reading, that:

- deletions may still flow
- zero-sized/control-shaped events may still flow
- rescans/indexing may still advance
- some uploads may still happen under scheduled `Paused`

A serious sync product should not require the operator to carry that matrix in their head just to decide whether the quiet claim survived.

### 3. First visible movement can be mistaken for first real break

Current docs still make it easy to overreact to the first observed change.
But the first visible motion is not always the first true quiet break.
It may only be:

- an allowed delete propagation
- an allowed zero-byte/control event
- an allowed indexing/share-size increase
- evidence that the original quiet sentence was narrower than the operator remembered

Without a post-event classifier, `I saw movement` becomes folklore rather than reviewed incident truth.

### 4. There is still no durable receipt for event verdict and claim survival

Current docs explain controls and residual behaviors.
They still do not emit one durable reviewed receipt that says:

- which quiet receipt was challenged
- which event arrived
- whether that event fit the declared residual allowances
- whether the earlier quiet claim remained unchanged, narrowed, or invalidated
- what strongest sentence is still safe now

That is still too much memory burden for maintenance, evidence, and destructive operations.

## Why this matters for AnonSync

AnonSync should not clone a contract where partial quiet is documented but post-quiet judgment is improvised.

The product now needs one stable answer to four follow-up questions:

- **event truth** — what actually happened?
- **fit truth** — did that event fit the allowed residual classes from the earlier receipt?
- **claim truth** — did the earlier quiet claim survive, narrow, or fail?
- **language truth** — what sentence remains safe now, and what stronger sentence became forbidden the moment the event was classified?

That is a real product seam, not support prose.

## Replacement pages in this revision

This revision adds four fixed pages:

- `822` — Quiet event page
- `823` — Residual allowance review page
- `824` — Quiet challenge ledger page
- `825` — Residual classification receipt page

Together they make `did this observed motion actually break the quiet claim?` explicit before AnonSync lets a delete, share-size jump, upload row, or control-shaped event become informal proof that quiet failed.

## Concrete product stance

Borrow from Resilio:

- candid admission that pause and scheduled `Paused` still allow specific residual event classes
- candid admission that indexing/share-size growth can continue under paused-looking states
- candid admission that asymmetric peer behavior can survive a local/scheduled quiet posture
- candid preservation of the difference between visible label and surviving mechanics

Do not clone from Resilio:

- leaving the operator to remember the residual matrix later when an event arrives
- letting the first visible motion masquerade as the first real quiet break
- forcing operators to reconstruct whether an event disproved the quiet claim or merely fit it
- leaving no durable receipt of event verdict, claim survival, and forbidden stronger sentence

## Evaluation summary

Resilio still deserves credit for publishing the surviving effects of pause honestly.
But the current product/docs path still leaves a missing object:

> there is no first-class reviewed answer to `this event happened during quiet — was that expected residue, or did the quiet claim actually fail?`

AnonSync should therefore make **allowed-residual classification and quiet-challenge review** a first-class product object.
Every serious maintenance window, evidence capture, migration cut, or destructive repair should publish challenged quiet receipt, observed event, allowance-fit verdict, strongest surviving sentence, and reopen boundary before the product treats post-quiet motion as understood.
