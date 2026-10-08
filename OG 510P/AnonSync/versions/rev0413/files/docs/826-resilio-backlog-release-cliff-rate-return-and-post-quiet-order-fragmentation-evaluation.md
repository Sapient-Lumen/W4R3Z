# Resilio backlog-release cliffs, return-cap ambiguity, and post-quiet order fragmentation evaluation

## Purpose

The archive already has strong page families for:

- quiescence review
- quiet windows
- quiet cohorts
- quiet-break provenance
- residual allowance classification
- download-queue truth
- resume catch-up truth

What it still lacked was one ordinary operator answer that current Resilio docs still do not own tightly enough:

> once quiet ends, **what resumes first, at what cap, and how bursty will the deferred backlog release actually be?**

Current official Resilio docs are candid that quiet windows, full-bandwidth return, and priority rules are real.
The next problem is that post-quiet release shape is still reconstructed from several documents.
That is a stronger reason not to clone them than a dislike of wording.

## What current Resilio still gets right

Current official docs still deserve credit for preserving the ingredients of resumed catch-up instead of pretending that `resume` is one self-explanatory event.

The load-bearing truths they still publish include:

- the current `Running Sync on schedule` article still says empty cells mean full bandwidth available, unchecked upload or download means full bandwidth for that direction, and scheduled `Paused` still leaves specific residual behaviors alive
- the current `File download priority` article still says per-share priority and global `folder_defaults.transfer_priority` can both shape order
- that same priority article still says a share with manually set priority stops inheriting later global changes even if the operator later sets it back to `None`
- that same priority article still says only up to 50,000 active files are prioritized, higher-priority arrivals suspend lower-priority work, some internal exceptions remain, non-splittable files do not fully obey strict prioritization, and the visible queue may still appear alphabetical rather than true execution order
- the current `Power user preferences` article still publishes `folder_defaults.transfer_priority` as a standing default plane
- the maintained v3 line still runs through `3.1.2.1076`

That is good candor.
Resilio is still honestly preserving the facts that quiet expiry, returned cap, inherited order, queue caps, and actual execution order are not the same truth.

## What current Resilio still should not be cloned

### 1. A quiet-window ending still has no product-owned release plan

Once an operator reaches the end of a quiet window, the next serious question is no longer `was I paused?`
It becomes:

- does this subject snap back to full bandwidth right away or to some narrower cap?
- which backlog class actually moves first now?
- is the visible queue order authoritative enough to trust?
- which queue exceptions make the simple priority promise false right now?
- how bursty will catch-up be if we open the floodgates now?

Current Resilio docs still expose ingredients of those answers.
They still do not give one product-owned object for **backlog release planning**.

### 2. The operator still has to merge cap-return truth with ordering truth

Current docs explain schedule cells and priority separately.
That means the operator still has to remember, from several pages, that:

- an ended quiet window may mean instant full-bandwidth return
- order may come from per-share priority or a standing global default
- manually pinned shares stop inheriting later global changes
- only part of the queue is prioritized
- visible queue rows may not match actual execution order

A serious sync product should not require the operator to splice those truths mentally just to predict the first catch-up wave.

### 3. Priority promises are still too easy to overread after quiet

Current docs are honest that priorities have limits.
But they still leave the operator to remember that:

- only the active queue is prioritized
- the active queue has a cap
- large or non-splittable transfers may not behave the way a neat priority story suggests
- queue rebuilds can change the currently effective order

Without a reviewed order surface, `we have priority configured` can overclaim what the resumed backlog will really do.

### 4. There is still no durable receipt for return cap, release shape, and flood risk

Current docs explain controls and queue behavior.
They still do not emit one durable reviewed receipt that says:

- which quiet or rate posture just ended
- what cap actually returned
- what backlog order is authoritative now
- which exceptions or rebuild conditions still distort that order
- what strongest sentence is still safe about the catch-up wave

That is still too much memory burden for maintenance exits, controlled cutovers, and post-quiet operational promises.

## Why this matters for AnonSync

AnonSync should not clone a contract where quiet is reviewed but resumed catch-up is improvised.

The product now needs one stable answer to four follow-up questions:

- **release truth** — what exactly reopened, and at what cap?
- **order truth** — what will actually move first, and which source is authoritative?
- **exception truth** — what caps, transfer classes, or rebuild events still distort that order?
- **language truth** — what sentence is safe now, and what stronger `resume will clear cleanly` sentence is still forbidden?

That is a real product seam, not support prose.

## Replacement pages in this revision

This revision adds four fixed pages:

- `827` — Backlog release plan page
- `828` — Backlog order review page
- `829` — Backlog release timeline page
- `830` — Backlog release receipt page

Together they make `when quiet ends, what resumes first and how violent is the release?` explicit before AnonSync lets schedule expiry, resume, or priority policy become folklore.

## Concrete product stance

Borrow from Resilio:

- candid admission that quiet expiry can mean full-bandwidth return
- candid admission that backlog order may be shaped by both per-share and standing global priority
- candid admission that queue caps, preemption, and transfer-class exceptions distort neat priority stories
- candid admission that visible queue order may not be authoritative

Do not clone from Resilio:

- leaving cap return and order truth in separate help pages
- forcing the operator to remember inheritance and override freeze during maintenance exit
- letting alphabetical or browse order masquerade as current execution order during catch-up
- leaving no durable receipt of returned cap, actual order, flood-risk verdict, and reopen boundary

## Evaluation summary

Resilio still deserves credit for publishing the ingredients of backlog release honestly.
But the current product/docs path still leaves a missing object:

> there is no first-class reviewed answer to `quiet ended — what exactly is about to flood back, in what order, and how much of that story is still provisional?`

AnonSync should therefore make **backlog release planning and post-quiet order review** first-class product objects.
Every serious maintenance exit, quiet-window expiry, and deferred catch-up situation should publish release trigger, return cap, authoritative order, queue exceptions, flood-risk verdict, strongest safe sentence, and reopen boundary before the product treats resumed motion as understood.
