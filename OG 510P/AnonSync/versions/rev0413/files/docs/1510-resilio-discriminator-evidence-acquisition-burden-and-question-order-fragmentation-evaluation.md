# Resilio discriminator evidence acquisition, burden, and question-order fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- publish doctrine
- compare fresh fact patterns against candidate doctrine
- publish the next best distinguishing question when routing stayed ambiguous

What it still lacked was the next ordinary operator answer:

> which fact should we actually go get next, which evidence channel is cheapest, what capture is intrusive or restart-bound, and when is the stronger sentence still not worth the burden?

That is the seam this pass locks.
A product that can name the next question but cannot manage the evidence burden is still incomplete.
Question order is product truth, not support folklore.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose many useful evidence prompts, but mostly as separate pages and support-style instructions:

- `Sync Main View (Desktop)` still exposes search, peer counts, statuses, notifications, and a 30-day History lane.
- `My files don't sync` still tells operators to inspect peers, Status warnings, History, and peer queues before escalating.
- `Comprehensive guide to syncing (Desktop-Desktop)` still says `Pending approval` without a received request points to network-connectivity trouble and still lets the approver inspect requester name, IP, fingerprint, and request date.
- `"Time difference" error` still gives a specific discriminator: compare UTC time and timezone across peers because bad clock or timezone can change file ordering and even produce empty mobile file lists.
- `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` still gives another discriminator: selective-sync ghost-file conditions and source-availability ambiguity.
- `Some internal tasks are taking time to complete` still says heavy internal work may explain the state, which means waiting and observing can itself be a valid evidence step.
- `Collecting debug logs automatically` still requires enabling debug logging, restarting Sync, reproducing the issue, waiting at least 15 minutes, and supplying timestamps, peer role, and affected shares/files.
- `Collecting debug logs manually` still requires enablement, restart, reproduction, and locating logs in platform-specific storage paths.
- `Collecting crash reports, mini-dumps and core dumps` and `Collecting core dump on NAS devices` still show that some evidence is much more intrusive than ordinary observation.
- `Errors & Troubleshooting` still organizes many symptom families as article lists, which helps discovery but not evidence-order planning.

## What current Resilio still gets right

### 1) It preserves cheap first checks

Resilio does not always jump straight to logs.
Peer state, warnings, history, clock sanity, and queues are still named as earlier checks.
That is worth borrowing.

### 2) It acknowledges that some evidence is expensive

Restart-bound debug logging, reproduction windows, and core dumps are meaningfully heavier than reading a warning, checking time, or inspecting a peer list.
That honesty matters.

### 3) It sometimes names the exact extra fact that would distinguish lookalikes

Ghost-file conditions, time skew, approval-request absence, and heavy internal work are real discriminators.
Those are useful ingredients.

## Where current Resilio still fragments the operator answer

### A) Evidence order still lives across many symptom pages

Different pages tell the operator to check different things first.
What current Resilio still does not give is one product-owned ranked evidence plan that says why this next fact is better than the alternatives.

### B) Burden is implied, not normalized

A restart plus reproduction plus 15-minute log window is clearly heavier than reading a warning.
A core-dump workflow is heavier again.
Current Resilio shows those burdens, but still does not normalize them into one explicit burden ladder.

### C) Cheap discriminators and intrusive capture are not unified

A strong operator product should let the user see:

- which cheap fact would collapse the ambiguity fastest
- which medium-cost capture is justified next
- which expensive capture is still not justified
- what stronger sentence remains blocked if we decline the heavier capture

Current Resilio offers the ingredients, but not one canonical decision object.

### D) Failure-to-capture is not yet product truth

Sometimes the user cannot restart, cannot reproduce on demand, cannot access the service storage path, or cannot gather logs from all peers.
Current Resilio instructions acknowledge pieces of that reality, but still do not make `capture unavailable` a first-class operator outcome with a weakened safe sentence.

## Hard product decision unlocked by this pass

AnonSync should not let evidence acquisition live in article hopping, support macros, or remembered troubleshooting lore.
It should compile every serious ambiguous case into a first-class **discriminator acquisition** object that separately expresses:

- open fact gaps
- candidate questions
- decision value of each question
- burden, restart cost, and privacy or operational intrusion
- who can answer or capture it
- fallback evidence if the best channel is unavailable
- currently justified ask
- stronger sentence still blocked if no more evidence is gathered

## Replacement line for AnonSync

Borrow from Resilio:

- cheap observational breadcrumbs like peer counts, warnings, history, approval details, and clock checks
- candid instructions for when logs, profiler data, or crash artifacts are truly needed
- symptom-specific guidance that preserves different discriminators

Do not clone from Resilio:

- any workflow where question order is reconstructed from several KB pages manually
- any contract where heavy capture can be requested without publishing its burden and decision value
- any interface where `get logs` is treated as a generic escalation rather than a typed evidence move
- any product shape where inability to capture the best evidence is left as chat residue rather than a durable weakened-claim state

AnonSync should instead ship explicit pages for:

- discriminator acquisition contract sheet
- evidence-priority and burden review
- fact-capture proof
- acquisition timeline
- acquisition lineage receipt
