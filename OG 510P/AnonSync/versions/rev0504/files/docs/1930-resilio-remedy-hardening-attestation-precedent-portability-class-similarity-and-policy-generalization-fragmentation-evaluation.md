# Resilio remedy hardening attestation precedent portability, class similarity, and policy-generalization fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for being unusually candid that one successful path is not the same thing as one universal path.
That is useful.

The strongest present ingredients are:

- current `Comprehensive guide to syncing (Desktop-Desktop)` docs still say there are two distinct configuration approaches — linking devices with one identity for automated folder sharing, or manually sharing each folder individually
- current `User Management` docs still say that when you share data across your own linked devices all of your devices act as Owners
- current `What's the difference between Standard and Advanced folders?` docs still say Standard and Advanced folders are architecturally different, Standard peers can share the key they have without limitation, and on-the-fly permission changes are only available for Advanced folders
- current `Running Sync in configuration mode` docs still say config mode can set up only Standard folders, not Advanced
- current `Folder Preferences` docs still say important behavior remains folder-by-folder and desktop-only
- current `How to create a Read Only folder while syncing across linked devices?` docs still say linked devices normally auto-receive Owner access, and a read-only result on a linked device requires a manual Standard-folder Read Only key detour
- current `How do I upgrade my Standard (1.4, or classic) folders to Advanced (2.x) folders?` docs still say there is no upgrade path because of significant architectural differences; you must remove Standard folders and re-add them as Advanced
- current `Resilio Sync 3.0 change log` still records UI, warning, status, and interaction fixes, which matters because a path that looked smooth this month is not automatically a precedent contract

## Where the current contract still fragments

The problem is not that Resilio lacks reusable mechanics.
The problem is that it still does not produce one first-class, case-scoped **precedent portability and policy-generalization** object.

Today an operator can often infer only weaker truths such as:

- this exact folder-type and topology combination worked once
- this workaround produced a read-only result on one linked-device pattern
- this config recipe applies only to Standard folders
- this permission mutation path exists only for Advanced folders
- this preference knob exists only on desktop and only per folder
- this migration from Standard to Advanced is not an upgrade but a remove-and-re-add replacement
- this UI or warning behavior looked acceptable in the current version

Those are useful clues.
They are not the same as an explicit answer to `may this closed case now be reused as a default rule, a support recipe, or a policy for future cases, for which topology classes, under which invariants, with which excluded differences, and until what sunset or counterexample?`

## Why that matters for AnonSync

AnonSync needs a stronger sentence than `this case is closed and no one is currently objecting`.
It needs to support claims such as:

- the source case closed cleanly, but it remains case-specific and must not be generalized
- the case is portable only to a named topology class with the same authority model, evidence planes, and share-lane constraints
- the remedy recipe is safe as a pilot for one cohort, but not yet policy for the whole estate
- one counterexample in a different topology narrows the rule back down to case-specific only
- the strongest honest sentence is `portable for named cohort under named invariants until review date`, not `this is now our rule`

AnonSync therefore needs first-class objects for **source closure quality, candidate target class, similarity basis, excluded differences, pilot reuse count, counterexample register, ratification owner, policy scope, sunset date, portability ceiling, and blocked stronger policy sentence** rather than leaving operators to promote one successful case into folklore.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `does this successful path deserve to become a reusable rule?` — only by making the operator combine several partially overlapping mechanics:

- linked-device versus manual-share topology
- Standard versus Advanced architecture
- config-mode Standard-only setup
- desktop-only per-folder preferences
- linked-device Owner semantics
- read-only manual detours
- remove-and-re-add migration boundaries
- current-version UI and warning behavior

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **precedent portability and policy generalization** directly.
Its interface family should let the product separate at least these truths:

- case closed, case-specific only
- portability proposed, similarity review pending
- portable for named topology class only
- pilot reuse allowed for named cohort only
- counterexample open, rule narrowed
- policy ratified for named scope only
- precedent sunset due
- precedent revoked or superseded
- broader policy sentence blocked
