# Resilio creditor attribution, evidence horizon, and dispute-reopening fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- open burst debt and embargo new bursts while debt remained live
- stage repair through a creditor waterfall and preserve partial-relief truth
- keep probation alive even after some tiers cleared
- refuse to call the claimant cleanly restored while residue or waiver consequence survived

What it still lacked was the next hard operator answer when **the creditor set itself is not cleanly settled**:

> who is actually a valid creditor, on what evidence, for how long, what happens when that evidence ages out or is challenged, and can clean restoration still be released while the creditor set is disputed?

That is the seam this pass locks.
A product that can say `tier 1 cleared` and `probation still active` but cannot say `named harmed claimant remains disputed because archive lacks actor detail and history has aged`, or `only the reserve creditor is verified while neighbor attribution is contested`, is still leaving the decisive fairness truth in operator reconstruction.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real **attribution and aftermath fragments**, but not one operator-facing creditor-claim contract:

- `Sync Main View (Desktop)` still says History shows general syncing activity for the last 30 days.
- `Using Archive for file versioning and restoring deleted files` still says desktop Archive defaults to 30 days, can be tuned by `sync_trash_ttl`, can have versioning size limits, and Archive itself does not provide details on which peer made changes to a file.
- The same Archive article still says an old version is placed into Archive on THIS device only when the file was modified by ANOTHER peer.
- `What if several people make changes to the same file?` still says Sync applies chronological order among online changes but that an offline peer returning later can cause its version to take priority over versions proposed by peers that stayed online, with overwritten versions placed in Archive.
- `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` still says peers can announce files that later have no actual source peer, producing ghost-file warnings.
- `Some internal tasks are taking time to complete` still says hidden work like block checking, dedup copy, hashing, merging, scanning, reading, transferring, and writing may continue for a long time and may recover on their own.
- `How soon does synchronization start?` and `Power user preferences` still say rescans are periodic background work, with `folder_rescan_interval` defaulting to 600 seconds and Archive limits controlled by preferences such as `sync_trash_ttl` and `max_file_size_for_versioning`.

## What current Resilio still gets right

### 1) It admits that evidence is distributed across several planes

History, Archive, runtime state, rescans, and warnings all carry different parts of the story.
That is useful candor.

### 2) It preserves some overwritten-state residue

Archive keeps old versions under defined conditions.
That is materially better than pretending overwritten work never existed.

### 3) It exposes enough fragments for a human investigator to start a dispute review

History, Archive, ghost-file warnings, rescan behavior, and hidden-work explanations are all real clues.
Those ingredients are worth borrowing.

## Where current Resilio still fragments the operator answer

### A) Archive residue is not the same as creditor attribution

Archive may hold an old version, but the Archive article explicitly says Archive itself does not identify which peer made the change.
That means a later operator may have residue without one durable actor-attribution answer.

### B) History freshness is too short for staged-restoration disputes

The main view describes History only as general syncing activity for the last 30 days.
That is useful for recent incidents, but it is not a durable creditor ledger for disputes that survive longer than one month.

### C) Evidence horizons are policy knobs, not first-class fairness objects

Archive TTL and maximum versioned file size can be configured, and rescans are periodic.
Those are real controls, but current docs still do not publish one contract saying `this creditor claim is verified through this horizon`, `this residue is now stale-evidence-risk`, or `clean release is frozen because proof aged out before review completed`.

### D) Offline-return overwrite behavior complicates causal attribution without one typed dispute object

When an offline peer comes back and its version takes priority over online-proposed versions, overwritten files go to Archive.
That is useful residue, but current docs still do not provide one typed operator verdict about which harmed claimant is verified, which is merely plausible, and which needs dispute review.

### E) Ghost-file and hidden-work paths can keep the observable story unsettled

Current docs say peers can advertise files whose source later disappears and that hidden background operations may continue for a long time.
Those are honest caveats, but they still leave the operator without one stable `verified / contested / unverifiable / reopenable` creditor state.

## Resulting product decision

AnonSync should borrow Resilio's evidence fragments and operational candor.
It should **not** clone a product shape where creditor attribution, evidence freshness, claim disputes, and reopen semantics still have to be inferred from History, Archive, rescan timing, ghost-file warnings, and hidden work.

AnonSync should instead expose:

- one first-class **Creditor claim contract sheet**
- one **Creditor dispute review** page
- one **Creditor attribution proof** page
- one **Creditor dispute timeline**
- one durable **Creditor attribution lineage receipt**

## Hard decisions locked by this pass

- **unverified creditor claim is weaker than verified open creditor**
- **clean restoration may not release while a material creditor dispute remains open**
- **evidence aging out downgrades truth into explicit contest or unverifiable residue; it may not silently upgrade the claimant into clean standing**
- **reserve-only provisional relief is allowed while named-neighbor attribution is contested, but harmed-neighbor release sentences stay blocked**
- **undisputed core and disputed residue must be rendered separately instead of forcing all-or-nothing acceptance**
- **reopened evidence after provisional closure can re-freeze release, re-open probation, and re-tighten future-burst posture**
