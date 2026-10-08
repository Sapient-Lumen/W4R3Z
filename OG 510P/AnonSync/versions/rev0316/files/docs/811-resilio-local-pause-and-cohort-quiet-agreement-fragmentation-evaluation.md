# Resilio local-pause, global-pause, and cohort-quiet agreement fragmentation evaluation

## Purpose

The archive already had strong page families for:

- quiescence review
- residual activity matrices
- pause-language substitution
- maintenance-grade stillness
- re-entry after dormancy
- opportunity / lateness honesty

What it still lacked was one ordinary operator answer that current Resilio docs still do not own tightly enough:

> did we only quiet **this seat**, or did we actually establish a reviewed quiet window across the seats that matter for the maintenance / evidence / migration job?

Current official Resilio docs are candid that pause is partial.
The next problem is that the controls they document are also overwhelmingly **local**.
That is a stronger reason not to clone them than a simple dislike of wording.

## What current Resilio still gets right

Current official docs still deserve credit for not pretending that all `pause` controls mean one universal freeze.

The load-bearing truths they still publish include:

- the current `How to pause syncing` article still says pause stops only bits download / upload while zero-sized files and deletions still sync and new files are still rescanned and indexed
- that same article still says Global Pause affects all shares on the current Sync window, which is a local device-facing control rather than a reviewed cohort agreement
- the current `Sync Preferences` article still says Global Pause / Resume puts all shares that are not paused individually on pause and still treats Scheduler as another neighboring local control
- the current `Running Sync on schedule` article still says scheduled `Paused` means both upload and download speed are zero, yet zero-sized files and deletions still sync, new files are rescanned and indexed, and paused peers may still upload files to other non-paused peers while not downloading themselves
- the still-published historical changelog still records a fix for `Sync stopping indexing if folder paused`, which shows this seam has been subtle enough to break in production
- the maintained v3 line still runs through `3.1.2.1076`

That is good candor.
Resilio is still honestly warning the operator that one visible `Paused` badge is weaker than full stillness.

## What current Resilio still should not be cloned

### 1. The documented controls are local, but operator intent is often cohort-wide

A maintenance or evidence operator often means one of these stronger questions:

- have **all affected seats** gone quiet yet?
- which peers are still able to send, delete, rescan, or otherwise perturb the subject?
- is this only a local bandwidth pause, or a reviewed quiet window across the participants that matter?
- who still has not acknowledged or matched the requested stillness?

Current Resilio docs still help explain local pause behavior.
They still do not give one product-owned object for **quiet cohort coverage**.

### 2. Global Pause is not the same thing as a shared quiet agreement

The phrase `Global Pause` sounds stronger than the documented contract.
It means all shares on this device except those already individually paused.
That is still a local-seat stop request.
It is not an explicit proof that counterpart seats adopted the same stop class, nor that the affected cohort has matched stillness.

A serious sync product should not let `global` on one seat masquerade as `quiet enough everywhere that matters`.

### 3. Scheduler quiet and manual pause still do not produce counterpart proof

Current Resilio docs still let the operator configure scheduled quiet windows and local pause/resume.
But the documented behavior still leaves at least three missing answers:

- which counterpart seats were expected to match this quiet window
- which ones actually did
- what stronger sentence is safe right now: `I am quiet locally`, `most of the cohort is quiet`, or `maintenance-grade quiet is established`

The operator still has to reconstruct that from memory, side-channel coordination, or future symptoms.

### 4. There is still no durable quiet-window receipt for the affected cohort

Current docs explain controls, but there is still no one reviewed receipt that says:

- target subject and maintenance/evidence intent
- requested quiet cohort
- achieved coverage across seats
- uncovered seats and residual movers
- strongest safe sentence
- reopen boundary once a covered seat resumes or a new seat appears

That is still too much memory burden for serious coordination work.

## Why this matters for AnonSync

AnonSync should not clone a contract where local stillness is easy to request but cohort stillness is easy to assume.

The product now needs one stable answer to four follow-up questions:

- **scope truth** — who needed to be quiet for this job?
- **coverage truth** — who actually matched the requested stillness?
- **residual-mover truth** — which seats can still perturb the subject?
- **language truth** — is the safe sentence `quiet here`, `quiet across covered seats`, or `not yet quiet enough`?

That is a real product seam, not support prose.

## Replacement pages in this revision

This revision adds four fixed pages:

- `812` — Quiet cohort page
- `813` — Quiet agreement review page
- `814` — Quiet window request page
- `815` — Quiet cohort receipt page

Together they make `who is actually quiet enough for this operation?` explicit before AnonSync lets `paused`, `global pause`, or `maintenance window started` become durable language.

## Concrete product stance

Borrow from Resilio:

- candid admission that pause is partial and origin-bearing
- candid admission that indexing, deletion, and some upload behavior may remain live
- candid separation of folder-level, scheduler, and global local controls
- candid preservation of current control origins rather than flattening them into one universal stop

Do not clone from Resilio:

- letting a local `Global Pause` read like a cohort-wide quiet guarantee
- leaving counterpart quiet coverage implicit, social, or purely inferential
- letting maintenance/evidence operators discover uncovered seats only after the subject changes anyway
- leaving no durable receipt of requested cohort, achieved coverage, uncovered seats, and strongest safe sentence

## Evaluation summary

Resilio still deserves credit for telling the truth that pause is partial.
But the current product/docs path still leaves a missing object:

> there is no first-class reviewed answer to `did we establish quiet where this job actually needed it, or did only one seat get quieter?`

AnonSync should therefore make **quiet cohort agreement** a first-class product object.
Every serious maintenance window, evidence capture, migration cut, or destructive repair should publish target cohort, matched seats, residual movers, strongest allowed sentence, and reopen conditions before the product treats local pause as shared stillness.
