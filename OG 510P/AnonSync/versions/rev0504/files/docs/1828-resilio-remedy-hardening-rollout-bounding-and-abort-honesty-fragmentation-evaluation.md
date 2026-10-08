# Resilio remedy hardening rollout bounding, pilot scope, and abort honesty fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials are still usefully candid about how much *spread power* exists after a case already looks hardened, retained, and change-gated.
That candor matters.

The strongest present ingredients are:

- current `Comprehensive guide to syncing (Desktop-Desktop)` docs still say every folder added on one linked device automatically becomes available on all other linked devices with full read-write access
- current `User Management` docs still say Advanced-folder permissions can be changed on the fly without disrupting sync, and that disconnect revokes future updates while leaving already synchronized files in place
- current `What's the difference between Standard and Advanced folders?` docs still say Standard folders have no Owner layer and any peer can share the key it has onward without limitation
- current `Sync Share Dialog (Desktop)` docs still say links can be approval-gated, time-limited, and use-limited, but Standard-folder keys themselves do not use that approval mechanism
- current `Synchronization Modes` docs still say linked devices may sit in Disconnected, Selective Sync, or Synced modes, producing materially different rollout surfaces
- current `Sharing a folder locally` docs still say local shares remain deliberately device-local and do not propagate to linked devices, but they inherit source permissions and disappear if the source is removed or disconnected
- current `How to create a Read Only folder while syncing across linked devices?` docs still say linked devices auto-receive Owner access by default and that one-way lanes across linked devices require manual Standard-folder detours

## Where the current contract still fragments

The problem is not that Resilio lacks ways to *limit* spread in practice.
The problem is that it still lacks a first-class, case-scoped **remedy-hardening-rollout** object.

Today the operator can often infer only weaker truths such as:

- this change was approved
- this link will expire eventually
- this invite can only be used a fixed number of times
- this one device stayed disconnected
- this one device uses Selective Sync
- this one local share stayed on a single machine
- this one peer was disconnected after spread began

Those are useful operational clues.
They are not the same as an explicit answer to `may this approved change go live now with a bounded pilot scope, an honest blast-radius cap, and an abort path that still means what operators think it means?`

## Why that matters for AnonSync

AnonSync needs to support stronger post-approval claims than `the change was reviewed and permitted`.
It needs to support claims such as:

- the change is approved, but only a named pilot cohort may receive it yet
- the pilot lane is bounded, but linked-device auto-spread still blocks a stronger rollout sentence
- an abort path exists for future spread, but already-landed copies mean rollback honesty is weaker than operators may assume
- device-local trial lanes exist, yet they are still weaker than a required-cohort bounded rollout contract
- broader expansion is blocked until pilot evidence and post-rollout reseal finish

AnonSync therefore needs a first-class object for **hardening rollout bounding and abort honesty** rather than merely borrowing linked-device, share-link, sync-mode, or disconnect language.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `can this approved change spread now without exceeding the intended blast radius, and if we abort later what exactly can we still honestly unwind?` — only by making the operator combine several operational surfaces:

- linked-device automatic full-RW spread
- live Advanced-folder permission edits
- Standard-folder onward sharing without an Owner layer
- share-link approval, expiry, and use-count settings
- Disconnected versus Selective Sync versus Synced participation
- device-local shares that do not propagate further
- disconnect semantics that stop future updates but leave already synchronized bytes behind
- manual Standard-folder detours for one-way linked-device lanes

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model the following as separate public truths:

- change approved, rollout still ungated
- pilot-only rollout approved
- pilot running inside blast-radius budget
- pilot exceeded scope ceiling
- broader rollout blocked pending pilot proof
- abort still honest for unspread lanes only
- abort requested after spread debt exists
- rollback or compensation now required for already-landed lanes
- post-rollout reseal pending
- recurrence-hardened-retained-change-gated-and-rollout-bounded discharge achieved

That is why this tranche adds five more first-class pages: **Remedy-hardening-rollout contract sheet**, **Remedy-hardening-rollout review**, **Remedy-hardening-rollout proof**, **Remedy-hardening-rollout timeline**, and **Remedy-hardening-rollout lineage receipt**.
