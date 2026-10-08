# Resilio remedy-execution runway, priority, and source-readiness fragmentation evaluation

## What current Resilio gets right

Current official Resilio docs are candid that repair execution is governed by operational reality rather than by optimistic labels.
That candor is useful.

The strongest ingredients from the present contract are:

- download priority can be set per share or globally, and higher-priority files can suspend lower-priority downloads
- pause and scheduler make it explicit that stopping bandwidth does not stop every other state transition such as deletions, rescans, or indexing
- Selective Sync and Connected modes make source presence and placeholder-only visibility explicit instead of pretending every visible file is immediately recoverable
- no-source warnings openly admit that visible files can degrade into ghost files that nobody actually has anymore
- free-space thresholds and patched-file temporary-space requirements make storage headroom explicit
- internal-task and watcher warnings admit that indexing, hashing, merging, and discovery can delay when a supposedly available repair actually becomes executable

## Where the current contract still fragments

The problem is not that Resilio lacks knobs.
The problem is that it still lacks a first-class, case-scoped remedy-runway object.

Today the operator can often infer only weaker facts such as:

- this share has a higher download priority than other shares
- a scheduler window currently allows transfer bandwidth
- some peers can see placeholders for the needed file set
- a source peer was online recently, or might come back later
- disk thresholds are not red yet on this machine
- warning absence suggests, but does not prove, that discovery and merge are keeping up

Those are useful operational clues.
They are not a remedy execution contract.

## Why that matters for AnonSync

AnonSync needs to support stronger claims than `repair material is preserved and someone could try restoring it later`.
It needs to support claims such as:

- the case has an executable cure runway right now for the required cohort, within the promised response window
- the case has preserved repair material but lacks live source presence, so remedy remains blocked even though bytes survive somewhere
- the cure lane exists only if ordinary workload is paused or manually deprioritized, so the honest sentence is manual-only rather than ready-now
- storage headroom is too thin for patched or temporary repair writes, so the stronger clean-remedy sentence remains blocked
- queue saturation, background merge, or watcher lag means `priority set` is still weaker than `repair work is actually making timely forward progress`

AnonSync therefore needs a first-class object for **runway** rather than merely borrowing priority, pause, or placeholder vocabulary.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `can this case actually be cured now, with the needed source presence, headroom, and priority, inside the required response window?` — only by making the operator combine several operational surfaces:

- download-priority settings
- pause or scheduler rules
- placeholder and sync-mode semantics
- no-source warnings
- free-space thresholds
- internal-task and watcher warnings

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model the following as separate public truths:

- preserved repair substrate
- enforced preservation hold
- requested cure execution
- cure runway partial
- cure runway ready for named cohorts
- cure runway blocked by source absence
- cure runway blocked by headroom or queue debt
- cure runway expired or missed

That is why this tranche adds five more first-class pages: **Remedy-runway contract sheet**, **Remedy-runway review**, **Remedy-runway proof**, **Remedy-runway timeline**, and **Remedy-runway lineage receipt**.
