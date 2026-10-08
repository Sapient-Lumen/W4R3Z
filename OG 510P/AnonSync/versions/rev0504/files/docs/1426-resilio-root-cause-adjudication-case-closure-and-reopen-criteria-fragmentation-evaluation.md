# Resilio root-cause adjudication, case closure, and reopen-criteria fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- judge rollout health and promotion confidence
- choose the least-destructive next intervention
- execute that intervention with explicit checkpoints and safe-abort boundaries

What it still lacked was one ordinary operator answer to the next question:

> after we run the fix, what do we now believe actually caused the problem, what did we rule out, what remains unknown, how honest is closure, and what exact evidence should reopen the case later?

Current official Resilio material is useful here, but it still spreads that answer across many different pages:

- `Sync Main View (Desktop)`
- `My files don't sync`
- `Errors and warnings`
- `Core warnings`
- `Database error`
- `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time`
- `Agent run out of system notify watchers`
- `Service files missing / Cannot identify destination folder`
- `SE_SM_NO_IDENTITY`
- `Error 205`
- `Some internal tasks are taking time to complete`
- `Peers aren't connecting`
- `Collecting debug logs automatically`
- `I still have questions, where can I get answers?`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `Sync Main View (Desktop)` still gives the operator a History lane for the last 30 days and search/filter in the control surface. That is helpful evidence access, but not the same as one durable case object.
- `My files don't sync` still tells the operator to inspect Status warnings, click through to KB explanations, search Sync History, and inspect per-share queue state before choosing among many possible explanations. That is already a multi-hypothesis diagnostic workflow.
- `Errors and warnings` still exposes a broad catalog of different warning pages. The catalog itself is useful evidence that one visible symptom family fans out into many different cause families.
- `Core warnings` still mixes network discovery failure, free-space problems, and identity/storage corruption in one warning area, with examples like missing `.SyncUser###`, missing `.sync`, or damaged `identity.dat` under `Failed to sync list of folders`.
- `Database error` still gives multiple possible causes: improper shutdown, damaged disk sectors, virus, or other software touching the files. That is a true cause set, not a single deterministic diagnosis.
- `Cannot download files ... no source peers online for too long time` still explains a real specific cause pattern: selective-sync peers can advertise a file and later retain only a placeholder, producing a ghost-file condition rather than an ordinary connectivity failure.
- `Agent run out of system notify watchers` still ties the symptom to Linux watcher exhaustion and explicitly explains that the product may then learn changes only through manual or periodic rescans.
- `Service files missing / Cannot identify destination folder` still ties one symptom family to corrupted or deleted `.sync`, but also warns that two Sync instances touching the same folder can corrupt internal files, so even one warning may have more than one plausible root cause.
- `SE_SM_NO_IDENTITY` and `Error 205` still both tie the visible failure to identity corruption, but on different mobile paths and with different recovery instructions.
- `Some internal tasks are taking time to complete` still says the condition may be intermittent and self-recovering rather than definitive proof of a broken state.
- `Peers aren't connecting` still ends in a specific support artifact path: collect debug logs from two peers and send them to support.
- `Collecting debug logs automatically` still says direct technical support is unavailable for Sync v3, while technical support is available exclusively for Business customers, and the support form expects details like peer role, timestamps, and affected shares/files.
- `I still have questions, where can I get answers?` still points the operator toward the forum and support rather than one in-product incident reasoning workspace.

So current Resilio still clearly admits serious case-truths:

- one symptom can have several plausible causes
- warnings, history, queues, and logs are different evidence classes
- some conditions are transient enough that closure should stay weaker than `root cause removed`
- some cause families are environment-caused, some state-corruption-caused, some identity-caused, some topology-caused, and some still ambiguous
- support escalation requires a narrative with timestamps and scope, not merely a screenshot

But those truths still do not become one first-class operator-facing **case / hypothesis / closure / reopen object**.

## What Resilio still gets right

### 1) It does not pretend every symptom has one cause

The current docs are surprisingly candid that `database error`, `internal tasks`, `ghost files`, and identity failures are not the same class of problem.
That honesty is worth borrowing.

### 2) It preserves multiple evidence lanes

Current docs still push the operator toward warnings, history, queue state, log capture, and peer-specific observation.
That evidence diversity is useful.

### 3) It admits some states self-recover

`Some internal tasks are taking time to complete` is especially valuable because it explicitly blocks premature over-closure.

### 4) It often makes the operator name the case when escalating

The debug-log guidance still asks for role, timestamp, shares/files, and issue description.
That is already close to a case object, just not owned by the product.

## Where current Resilio still fragments the operator answer

### A) Cause adjudication is spread across many disconnected articles

A careful operator can infer that:

- missing files may be ignore-list mismatch, xattr mismatch, locks, read-only drift, permission failures, encoding issues, or path-length issues
- one warning family may map to tracker reachability, low storage, or identity/storage corruption
- one download error may actually be a topology/placeholder ghost-file problem
- one service-file symptom may come from deleted metadata or from two instances conflicting
- one `database error` may be environmental rather than product-internal
- one slowdown warning may be transient rather than actionable

But the product never turns that into a first-class hypothesis ledger with supported, ruled-out, and still-open branches.

### B) Closure language remains too loose

Resilio can help a skilled operator act, but it is much weaker at preserving closure truth like:

- `resolved`
- `mitigated`
- `workaround in place`
- `self-recovered`
- `unknown but stable`
- `unresolved awaiting support`
- `reopened after recurrence`

Without those distinctions, symptom disappearance can masquerade as real root-cause removal.

### C) Residual risk and reopen triggers are mostly folklore

Current docs can tell you how to fix or escalate, but not one canonical answer to:

- what residual risk remains after the run
- what specific event should reopen the case
- what evidence would upgrade or downgrade confidence in the current cause claim
- which stronger sentence is still blocked even though the immediate symptom cleared

### D) Escalation artifacts still sit outside the main reasoning surface

Logs, support forms, forum posts, and timestamps are all useful, but they still do not feed one canonical case record that survives handoff or recurrence.

## What AnonSync should borrow

Borrow these truths from current Resilio:

- symptom families should not collapse into one fake root cause
- evidence provenance matters
- self-recovery is a real outcome class
- support escalation needs timestamps, scope, affected subjects, and role context

## What AnonSync should refuse to clone

Do not clone any contract where:

- case reasoning lives only in troubleshooting prose
- supported, refuted, and unresolved causes are not recorded distinctly
- symptom disappearance is allowed to stand in for case closure
- reopen criteria stay implicit or oral
- escalation artifacts do not feed a durable operator-facing case object

## Product decision forced by this comparison

AnonSync should expose one first-class **incident case object** for every material degradation, ambiguous failure, or significant remediation run.

That object should preserve:

- symptom cluster and affected scope
- evidence inventory with freshness
- explicit hypothesis set
- supported, refuted, and unresolved cause branches
- closure class and residual risk
- reopen triggers and reopen severity
- support/escalation artifacts and ownership
- blocked stronger sentence

## The new AnonSync page family this pass requires

This comparison forces five new interface obligations:

1. an **incident case contract sheet** that names symptom cluster, scope, hypotheses, confidence floor, and target sentence
2. a **hypothesis adjudication review** that records supported, refuted, competing, and still-open cause branches
3. a **case closure proof** that distinguishes resolved, mitigated, workaround, self-recovered, unknown-but-stable, unresolved, and reopened states
4. an **incident case timeline** that preserves symptom arrival, evidence acquisition, hypothesis promotion, elimination, closure, and reopen events
5. a **case lineage receipt** that records final cause posture, closure class, residual risk, reopen triggers, and blocked stronger sentence

## Bottom line

Current official Resilio still deserves credit for practical troubleshooting candor and for preserving different evidence lanes.
But the reasoning and closure contract remains too article-fragmented to clone.

The archive should therefore:

- **borrow Resilio's honesty that one symptom can have many causes and that some states self-recover**
- **refuse Resilio's still-scattered case reasoning contract**
- **ship one operator-facing case object with explicit hypotheses, closure classes, residual risk, and reopen rules**
