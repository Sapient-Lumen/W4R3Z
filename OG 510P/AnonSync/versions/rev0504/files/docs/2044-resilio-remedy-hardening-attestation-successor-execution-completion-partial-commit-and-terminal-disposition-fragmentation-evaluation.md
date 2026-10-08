# Resilio remedy-hardening attestation successor execution completion, partial commit, and terminal disposition fragmentation evaluation

## Why this seam matters now

The archive can already say:

- a risky successor-world action was legitimate
- the chosen actuator looked least-broad
- an execution envelope was reviewed
- a preview was bound to commit with freshness discipline
- the run that actually fired can be attributed to some actor, subsystem, lane, and world with an explicit ceiling

That is still weaker than answering a sharper question:

**how far did that attributable run actually get before it finished, stalled, suspended, conflicted, ghosted, or left mixed-state residue?**

That question deserves its own family because `the right run fired`, `the first visible effects happened`, `data started moving`, `warnings are ignorable`, and `the queue is still working on it` are not enough to justify `the reviewed run completed as reviewed for the intended slice`.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about many execution-phase and partial-state behaviors, but it still leaves completion truth spread across unrelated articles:

- linked devices may show folders in disconnected or selective states long before all bytes exist locally
- selective-sync placeholders only hydrate when a peer holding the bytes is online
- pause stops transfer bits but still lets deletions propagate and lets rescanning and indexing continue
- background internal tasks can keep hashing, scanning, merging, deduplicating, reading, writing, and transferring for a long time without one unified terminal-disposition object
- watcher exhaustion can delay updates until a later periodic or manual rescan
- ghost-file warnings can appear after peers announce files that later vanish before download, leaving a visible expectation without a source peer that still has the bytes
- queue prioritization can suspend lower-priority downloads, rebuild the active queue, and treat only up to 50,000 active files as prioritized
- conflict files can surface when competing names or incompatible filesystem realities collide during propagation

That is useful candor, but it means the operator still reconstructs `did this attributable run fully complete, only partially complete, pause in a resumable way, or terminate with residue that blocks stronger completion language?` from several sync-mode, pause, warning, queue, and conflict articles rather than from one typed execution-completion object.

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- a run fired
- some files started transferring
- some metadata merged
- placeholders appeared
- deletes propagated while bytes did not
- hashing, deduplication, scanning, or writes continued in the background
- priority changes suspended some work and rebuilt the queue
- a warning was shown but could be ignored or hidden
- one or more files ended in conflict or ghost state
- the system later presented the outcome as if the reviewed run itself had simply completed cleanly

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **attributable execution legitimacy is weaker than execution completion integrity**
- **a run that definitely started is weaker than a run whose terminal disposition is known**
- **partial transfer, partial merge, partial write, partial hydrate, conflict creation, ghost-file expectation, and reviewed completion are different public truths**
- **`first visible effect`, `active queue moving`, `warning can be hidden`, and `same folder still looks present` may never impersonate `the reviewed run completed as reviewed`**
- **background hashing, scanning, deduplication, queue rebuilds, watcher-exhaustion rescans, placeholder hydration delays, and conflict creation must degrade into completion hazards instead of support folklore**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- execution-run identifier
- source execution-provenance receipt identifier
- reviewed step-set summary
- started-step-set summary
- completed-step-set summary
- suspended or stalled step-set summary
- partial residue summary
- terminal disposition class
- resumability class
- contradiction class
- strongest honest sentence and blocked stronger completion sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **successor execution-completion contract sheet**
- **successor execution-completion review**
- **successor execution-completion proof**
- **successor execution-completion timeline**
- **successor execution-completion lineage receipt**
