# Resilio remedy convergence, offline return, and late-joiner fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials are candid that an authoritative live state among the peers you can see **right now** is not the same thing as safe convergence across the peers who may reappear later.
That candor is useful.

The strongest ingredients from the present contract are:

- current `What if several people make changes to the same file?` docs still say an offline peer that modified a file and later comes back online can take priority over versions proposed by peers that stayed online, overwriting them and archiving the overwritten versions
- current linked-identity docs still say every folder added on one linked device automatically becomes available on all the other linked devices
- current folder-type and synchronization-mode docs still say a folder can sit as pending, disconnected, selective-sync placeholder view, or full synced copy rather than one flat participation class
- current folder-type docs still say previously approved pending folders can auto-connect when one of the approver's devices comes online
- current sharing and permissions docs still say linked devices under one identity all act as Owners, while Read Only participants can drift into suspended local changes that stop further synchronization for those changed files on that peer
- current selective-sync and disconnected-mode docs still say a peer may be visibly present in the cohort without yet holding the full bytes, leaving convergence weaker than ordinary visibility

## Where the current contract still fragments

The problem is not that Resilio hides late-arrival risk.
The problem is that it still lacks a first-class, case-scoped **remedy-convergence** object.

Today the operator can often infer only weaker facts such as:

- the cutover succeeded for the currently connected peers
- the repaired object is visible on a linked device that has not actually fetched the bytes yet
- a pending or disconnected folder exists and may connect later
- a previously approved peer may reconnect automatically
- an offline writer can still come back and overwrite what looked settled
- a read-only participant may hold a suspended local divergence that does not currently propagate but still matters to cohort truth

Those are useful operational clues.
They are not a convergence contract.

## Why that matters for AnonSync

AnonSync needs to support stronger claims than `the cure is now authoritative for active peers`.
It needs to support claims such as:

- the authoritative repair converged for the required present cohort, but returner-safe convergence stays blocked because one offline writer can still arrive with higher precedence
- the repaired object is fully switched for connected full-sync peers, while selective-sync and disconnected peers keep the stronger all-required-cohort convergence sentence blocked
- the visible linked-device roster expanded automatically, so the honest sentence is `late-joiner exposure increased` rather than `convergence stabilized`
- a previously approved pending peer can still auto-connect later, so future-joiner-safe convergence remains blocked
- read-only suspended local edits or placeholder-only peers mean the product must not compress visibility, currentness, and convergence into one success word

AnonSync therefore needs a first-class object for **remedy convergence** rather than merely borrowing linked devices, sync modes, approvals, offline-return overwrite rules, or read-only caveats.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `has the authoritative repair actually converged across the required present, returning, and newly admitted cohorts without late-arrival rebound?` — only by making the operator combine several operational surfaces:

- offline-return overwrite rules
- linked-device automatic availability
- pending and disconnected folder behavior
- selective-sync placeholder behavior
- approval retention and automatic future connection
- read-only suspension and overwrite behavior

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model the following as separate public truths:

- authoritative cutover for active cohort
- connected full-sync convergence
- named required-cohort convergence
- returner-risk pending
- late-joiner exposure increased
- placeholder-only cohort still unconverged
- pending-auto-connect cohort still outside convergence
- convergence blocked by offline writer return risk
- convergence blocked by suspended read-only divergence
- returner-safe convergence
- future-joiner-safe convergence
- convergence verification collapsed

That is why this tranche adds five more first-class pages: **Remedy-convergence contract sheet**, **Remedy-convergence review**, **Remedy-convergence proof**, **Remedy-convergence timeline**, and **Remedy-convergence lineage receipt**.
