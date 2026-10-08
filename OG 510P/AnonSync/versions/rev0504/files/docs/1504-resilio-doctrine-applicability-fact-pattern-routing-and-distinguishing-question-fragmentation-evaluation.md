# Resilio doctrine applicability, fact-pattern routing, and distinguishing-question fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- resolve a contested completion claim
- promote a ruling into precedent
- distinguish or overrule doctrine later

What it still lacked was the next ordinary operator answer:

> given this fresh case, which doctrine actually governs it, which lookalike routes remain plausible, and what one more fact would collapse the ambiguity fastest?

That is the seam this pass locks.
Published doctrine is not self-applying.
Search is not the same as applicability.
Warning titles are not the same as fact-pattern matches.
A useful operator product must help route the case, not merely list possible articles.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose many useful routing breadcrumbs, but mostly as separate pages and surfaces:

- `How do I perform a search in Sync?` still says Sync can search folders and shared files, connected devices, and users in UI.
- `Sync Main View (Desktop)` still exposes search, peer counts, statuses, notifications, and a 30-day History lane.
- `My files don't sync` still tells operators to inspect peers, Status warnings, History, and peer queues before choosing a next step.
- `Errors & Troubleshooting` and `Errors and warnings` still organize symptom families mainly as article lists.
- `Peers aren't connecting` still routes one family through multicast, NIC, router, firewall, relay, and predefined-host checks.
- `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` still describes a selective-sync / source-availability ghost-file style route.
- `"Time difference" error` still describes timestamp/timezone skew as another distinct route.
- `Database error` still escalates through restart, reconnect, and all-peer re-add.
- `Some internal tasks are taking time to complete` still says the issue may self-recover and may merely reflect temporary load.
- `Core warnings` still clusters many unrelated warning families under one surface.
- `Collecting debug logs manually` still says direct technical support is unavailable for Sync v3 and routes users toward forum/Help Center.

## What current Resilio still gets right

### 1) It preserves many real routing breadcrumbs

Resilio does not leave the operator completely blind.
Search, warning links, peer counts, history, and queue inspection are real breadcrumbs.
That is worth borrowing.

### 2) It keeps different symptom families distinct

Connectivity, ghost-file/source absence, time skew, database corruption, and temporary internal backlog are not flattened into one pseudo-cause.
That honesty matters.

### 3) It makes escalation visible

When local interpretation is not enough, Resilio does say when logs or deeper troubleshooting are needed.
That is better than an opaque failure.

## Where current Resilio still fragments the operator answer

### A) Search finds pages, but does not publish applicability weight

Literal search can help the operator find relevant folders, files, devices, users, or pages.
What it still does not do is answer whether one doctrine actually governs the current case better than the lookalikes.

### B) Symptom families still require manual article comparison

`My files don't sync` is an umbrella symptom.
So are some warning and history surfaces.
Current Resilio still leaves the operator to compare several candidate warning articles and troubleshooting trees manually.

### C) The next best distinguishing question is not first-class

A strong operator product should tell the operator what one more fact would most reduce ambiguity:

- are peers connected or not?
- is the clock wrong?
- is there a source peer for the missing bytes?
- is the problem local database state?
- is the system simply under temporary heavy load?

Current Resilio offers the ingredients, but not a canonical ranked discriminator object.

### D) Route reversals are still mostly informal

An operator can first suspect connectivity, then later discover time skew or ghost-file conditions.
What current Resilio still does not give is one durable route-reversal record that preserves why the earlier route looked plausible and what fact overturned it.

## Hard product decision unlocked by this pass

AnonSync should not let doctrine application live in article search, warning memory, or support escalation folklore.
It should compile every serious fresh case into a first-class **doctrine applicability** object that separately expresses:

- observed symptom family
- material facts already known
- candidate precedents
- disqualifiers already present
- unresolved differentiators
- next best distinguishing question
- currently governing doctrine if any
- strongest blocked sentence while ambiguity remains

## Replacement line for AnonSync

Borrow from Resilio:

- search affordances that expose useful breadcrumbs
- symptom-specific warning pages that keep problem families distinct
- explicit troubleshooting hints about peers, history, warnings, and queues

Do not clone from Resilio:

- any workflow where search results masquerade as doctrine application
- any contract where the operator must compare warning pages manually to decide which route applies
- any interface where the next best distinguishing question is not product-owned
- any product shape where route reversals vanish into support folklore instead of becoming durable doctrine-application history

AnonSync should instead ship explicit pages for:

- doctrine applicability contract sheet
- fact-pattern routing review
- applicability proof
- applicability timeline
- applicability lineage receipt
