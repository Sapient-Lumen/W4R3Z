# Resilio warning taxonomy, blocker scope, and recovery rung evaluation

## Why this pass exists

The archive already had:

- attention delivery and carrier truth
- many specific recovery pages
- contention, freshness, route, and continuity review objects
- external-recipe translation for off-product work

Those were necessary, but another current Resilio pass shows a still-missing seam.
The problem is no longer only `can the product alert me`.
It is now:

- what exact *kind* of warning is this?
- is it a degraded observer, a blocked subject, a chronology failure, a hidden-work backlog, or a continuity break?
- what exact seat / subject / path / byte family is affected?
- which next step is the safest rung rather than the loudest recipe?
- what does acknowledgement actually change, and what does it leave true?

That is where current official Resilio docs stay useful yet still become too article-shaped.

## What current Resilio still gets right

Current official material is still admirably candid that warnings correspond to real technical state.

Examples the docs still openly describe include:

- **core warnings** that distinguish tracker loss, low space in the default-folder-location disk, identity/list-of-folders failure, and license-sharing failure
- **hidden-work backlog** where `Some internal tasks are taking time to complete` can still mean scanning, hashing, block checking, deduplication, merge, transfer, or writing rather than a hard stall
- **watcher exhaustion** on Linux, where file-change notifications stop and discovery falls back to manual or periodic rescan until the inotify limit is raised and Sync restarted
- **ghost-file / no-source** warnings where peers were told about files that later ceased to exist as full bytes anywhere, and the product exposes filenames plus an `Ignore All` path
- **database error** where synchronization is suspended only for the corrupted subject while others may continue, with a restart → disconnect/reconnect → re-add ladder
- **service-files-missing** where `.sync` loss or corruption suspends the subject entirely and the suggested repair explicitly creates a new synchronization instance
- **folder-not-found** and **folder-not-empty** warnings that still admit materially different outcomes such as same-lineage reconnect, risky merge into pre-existing bytes, or peer-relationship loss on full re-add
- **time difference** warnings that still distinguish per-peer chronology failure and even explain the 600-second boundary

That candor matters.
Resilio is not pretending every warning is the same.

## Where the current page shape still fails

The ordinary operator answer is still reconstructed across too many article types, warning rows, and related-article hops.

### 1. Warning class is still too implicit

Current docs still force the operator to infer whether the warning is fundamentally about:

- observer degradation
- source absence
- hidden-work delay
- local-state corruption
- chronology invalidation
- merge-risk path choice
- identity failure
- capability / license governance

That classification is usually implied by prose, not owned by one stable page family.

### 2. Scope is still too scattered

The warning strings are real, but the blast radius still has to be reconstructed.
The operator must piece together whether the issue affects:

- one file or filename set
- one subject only
- one seat only
- linked-device identity
- future fetchability
- continuity-bearing hidden state
- global defaults such as the default-folder-location disk

That is too much inference for ordinary operational work.

### 3. Safe next step is still article-dependent

Current docs often provide a repair, but not one reviewed rung ladder.
The operator still has to infer whether the least-destructive next move is:

- wait
- inspect affected items
- rescan
- restore path binding
- reconnect same destination
- re-add everywhere
- adjust clock / timezone
- raise watcher limit and restart
- hide the warning only
- escalate with logs

That ranking still lives in separate articles and support habits.

### 4. Acknowledgement semantics are still weak

Some current warnings can be clicked for more detail.
Some can be hidden or ignored.
Some can be disabled through advanced settings.
But the ordinary operator still lacks one stable answer to:

- what exactly did `Ignore All` or dismissal do?
- what underlying state remains true?
- what future evidence would make the warning come back?
- was the warning solved, suppressed, or merely accepted with residue?

## What AnonSync should do instead

AnonSync should keep the candor and reject the article sprawl.

The product should split this seam into four page families:

1. **Warning page**
   - what class of warning this is
   - strongest honest severity
   - why the product emitted it now
   - whether the right first move is inspect, wait, or intervene

2. **Blocker scope**
   - exact blast radius across seat / subject / files / hidden state / identity
   - what continues normally
   - what is suspended, degraded, or uncertain

3. **Recovery rung**
   - least-destructive next step
   - proof required before escalating to broader repair
   - explicit distinction between acknowledgement, same-lineage repair, and recreate-successor repair

4. **Warning history**
   - issue first seen / last seen / last acknowledged
   - suppression or acceptance posture
   - what changed since prior occurrences
   - what proof would clear or reopen it honestly

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that warnings correspond to real degraded states, but not for the way ordinary answers to `what kind of warning is this`, `how wide is it`, `what exact next rung is safest`, and `what did acknowledgement really change` still sprawl across core-warning rows, one-off warning articles, troubleshooting pages, and advanced toggles instead of one stable page family.

## New replacement pages added in this revision

- `447` Warning page
- `448` Blocker scope
- `449` Recovery rung
- `450` Warning history
