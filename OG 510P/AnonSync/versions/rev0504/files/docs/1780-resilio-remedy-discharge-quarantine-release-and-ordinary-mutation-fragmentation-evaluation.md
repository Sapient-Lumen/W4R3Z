# Resilio remedy discharge, quarantine release, and ordinary-mutation fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials are candid that a cohort can look converged while still being exposed to broad ordinary permissions, remembered approvals, linked-device spread, or easy resharing.
That candor is useful.

The strongest ingredients from the present contract are:

- current `Sync Private Identity & Linking My Devices` docs still say once a remote user approves one of your devices they can choose to automatically approve all your linked devices for future sharing, and that all folders automatically become available across linked devices
- current `User Management` and `Sync Share Dialog (Desktop)` docs still say permissions can be changed without disrupting synchronization, Owners can share or revoke access, and disconnect revokes future updates while already synchronized files remain
- current `Sync Share Dialog (Desktop)` docs still say Standard folders have no Owner level and all peers can share the folder onward, while Advanced folders restrict sharing to Owners
- current `Synchronization Modes` and `Folder Types and Management` docs still say disconnected, selective-sync, synced, and pending states are materially different participation classes, including pending folders that can auto-connect after prior approval
- current `Is one-way synchronization possible?` docs still say Advanced folders do not support read-only synchronization across linked devices, which means some discharge targets inherently push the operator back toward Standard-folder resharing or other less-fenced ordinary lanes

## Where the current contract still fragments

The problem is not that Resilio hides ordinary-lane reopening risk.
The problem is that it still lacks a first-class, case-scoped **remedy-discharge** object.

Today the operator can often infer only weaker facts such as:

- the repair converged for the cohorts reviewed so far
- permissions were changed back to something broader
- a linked identity still spreads folder visibility and approval convenience across devices
- previously approved peers or pending folders may still connect later without a fresh case-specific discharge review
- Standard-folder resharing or Owner-level sharing rights still make ordinary mutation and onward admission easier than the case posture may intend
- revoking future updates does not claw back bytes already present, so releasing special fences is stronger than simply disconnecting someone

Those are useful operational clues.
They are not a discharge contract.

## Why that matters for AnonSync

AnonSync needs to support stronger claims than `the cure converged and current permissions look calm`.
It needs to support claims such as:

- the repair safely converged, but quarantine discharge remains blocked because remembered approvals still allow future auto-admission without fresh case review
- write rights were restored for one named cohort while onward sharing rights stay fenced, so ordinary mutation is only partially restored
- linked-device owner spread still makes the honest sentence `ordinary-lane release not yet safe` rather than `case discharged`
- Standard-folder resharing semantics would reopen too much admission surface, so the stronger ordinary-policy restoration sentence remains blocked
- disconnected or pending peers remain visible but are still outside discharge, so `converged` must stay weaker than `quarantine released`

AnonSync therefore needs a first-class object for **remedy discharge** rather than merely borrowing sharing roles, approval memory, linked-device convenience, or sync-mode visibility.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `has this repaired case actually been discharged back to ordinary mutation and admission policy without silently reopening the exposure?` — only by making the operator combine several operational surfaces:

- linked-device approval memory
- linked-device automatic availability
- Owner versus Standard-folder resharing semantics
- live permission changes
- pending-folder auto-connect behavior
- disconnect semantics that stop future updates but leave already synchronized bytes behind

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model the following as separate public truths:

- future-joiner-safe convergence pending discharge review
- discharge blocked by remembered approval surface
- discharge blocked by linked-device owner spread
- discharge blocked by broad onward-sharing rights
- discharge blocked by unreviewed pending or disconnected participant
- discharge partial for named writer cohort
- ordinary mutation restored for named cohort
- ordinary mutation restored for required cohort
- ordinary admission restored for required cohort
- quarantine released with rearm conditions
- discharge collapsed and quarantine reclosed
- discharge verification collapsed

That is why this tranche adds five more first-class pages: **Remedy-discharge contract sheet**, **Remedy-discharge review**, **Remedy-discharge proof**, **Remedy-discharge timeline**, and **Remedy-discharge lineage receipt**.
