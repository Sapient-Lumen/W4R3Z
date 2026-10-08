# Resilio appeal, precedent, and doctrine fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- receive a contested completion claim
- adjudicate counterevidence
- issue a verdict and, if needed, spawn rework

What it still lacked was the next ordinary operator answer:

> when a new dispute looks similar to an older one, which earlier ruling should bind this case, when is the case distinguishable, and when did a later fix or version change make the old guidance only persuasive or even superseded?

That is the seam this pass locks.
A verdict is not yet doctrine merely because it happened once.
Symptom articles are not the same as precedent.
Version drift can weaken guidance without erasing history.
A later operator needs a durable doctrine object, not memory of which article felt closest.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose many useful doctrine fragments, but mostly as separate articles and channels:

- `My files don't sync` still says Status warnings usually link to KB explanations and that operators may need to inspect warnings, History, peer state, and queues before choosing a fix.
- `Errors & Troubleshooting` and `Core warnings` still organize issue interpretation as clusters of separate warning articles.
- `"Time difference" error` still says bad time or timezone can distort ordering and even produce empty file lists on mobile.
- `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` still says a peer may announce files that later no source peer actually holds.
- `Database error` still offers a narrow repair ladder from restart to reconnect to all-peer re-add.
- `Service files missing / Cannot identify destination folder` still says the error may come from corrupted internal files or two instances touching the same folder and routes toward remove-and-add-back repair.
- `Agent run out of system notify watchers` still ties one warning to watcher exhaustion and periodic rescanning semantics.
- `Resilio Sync 3.0 change log` still shows that warning meaning and UI handling drift by version, including a fixed non-clickable `Can't download file` status and later improved warning text when a license cannot be applied.
- `Collecting debug logs manually` and `Collecting crash reports, mini-dumps and core dumps` still say direct technical support is unavailable for Sync v3 and route users toward the community forum and Help Center.

## What current Resilio still gets right

### 1) It preserves narrow symptom honesty

Resilio does not pretend every issue means the same thing.
Time skew, ghost-file announcements, watcher exhaustion, database corruption, and service-file corruption are treated as distinct problem families.
That is worth borrowing.

### 2) It keeps version drift visible in at least one channel

The change logs do admit that warning behavior, text, and UI affordances can change over time.
That honesty matters.

### 3) It still provides recoverable breadcrumbs

Warning pages, troubleshooting pages, and log-capture pages are real breadcrumbs for operators.
They are better than silence.

## Where current Resilio still fragments the operator answer

### A) There is no canonical precedent object

Resilio gives the operator warning articles, troubleshooting trees, logs, and change logs.
What it still does not give is one first-class object answering:

- which past ruling is being invoked for the current case
- whether that ruling is binding, presumptive, persuasive, or only informative
- what version window and world scope the ruling actually covered
- what distinguishing facts make the old ruling inapplicable here
- whether a later fix or version change overruled or sunset the old doctrine

### B) Doctrine weight is left to operator memory

A warning article may explain one issue.
A change log may later narrow, fix, or alter the meaning of that warning.
A support page may route users to forum or Help Center.
The operator must still remember how those parts fit together.

### C) Similar-looking cases can hide different world scopes

Time drift on mobile, watcher exhaustion on Linux, service-world corruption on Windows, and ghost-file behavior in selective-sync topologies are not the same class of ruling.
Current Resilio surfaces them separately, but it does not give one review object for distinguishing or relating them.

### D) Appeals and overruling are implicit rather than durable

Operators can read a newer article or a newer change log and infer that older advice is weaker.
What Resilio still does not give is one durable operator-facing record that a prior ruling has been upheld, narrowed, overruled, or sunset.

## Hard product decision unlocked by this pass

AnonSync should not let dispute consistency live in article memory, tribal recall, or changelog archaeology.
It should promote any materially reusable dispute verdict into a first-class **precedent docket** that separately expresses:

- source ruling
- analogy class
- binding weight
- version window
- world scope
- distinguishing facts
- appeal / overrule path
- sunset or supersession state

## Replacement line for AnonSync

Borrow from Resilio:

- explicit symptom families
- articleized explanations that name concrete failure modes
- version honesty when warning behavior or meaning changes

Do not clone from Resilio:

- any workflow where the operator must infer doctrine weight from scattered KB pages and change logs
- any contract where a later fix silently weakens old guidance without a visible overrule path
- any interface where similar cases cannot be explicitly marked as binding, persuasive, distinguishable, or superseded
- any product shape where forum or help-center routing becomes the only practical doctrine memory for v3 operators

AnonSync should instead ship explicit pages for:

- precedent docket contract sheet
- appeal and distinguish review
- precedent proof
- precedent timeline
- precedent lineage receipt
