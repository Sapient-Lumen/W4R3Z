# Resilio remedy hardening attestation downstream reliance, consumption coverage, and revocation-propagation fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for being candid that operational spread is real and that it does not stay confined to one button press on one machine.
That candor matters.

The strongest present ingredients are:

- current `Sync Private Identity & Linking My Devices` docs still say linked devices automatically make all folders available everywhere, remote users may auto-approve all linked devices for future sharing, and approvals can be issued from any linked device where the folder is present
- current `User Management` docs still say Advanced-folder permissions can be changed on the fly without disrupting synchronization, all linked devices under one identity act as Owners, and disconnect stops future updates while already synchronized files remain
- current `Folder Types and Management` docs still say pending folders may auto-connect after prior approval, disconnected folders remain visible for later action, and removing a disconnected folder affects all linked devices
- current `Disconnecting and Removing Folders` docs still say disconnected folders can later reconnect and may come back at a different default path, which means downstream state can reappear rather than vanish cleanly
- current `Running Sync in configuration mode` docs still say configured parameters can be applied on a number of different machines and can create settings in a new storage path
- current `Sync Main View (Desktop)` docs still say operational visibility is bounded by short-history and peer-list horizons
- current `Collecting debug logs automatically` docs still say deeper evidence often requires enable, restart, reproduce, and wait
- current `Service files missing / Cannot identify destination folder` docs still say repair can create a new synchronization instance
- current `Cloning Sync` docs still say unsupported copies can create strange behavior and non-transferring twins

## Where the current contract still fragments

The problem is not that Resilio hides spread.
The problem is that it still does not produce a first-class, case-scoped **downstream reliance and revocation** object.

Today an operator can often infer only weaker truths such as:

- some linked devices probably received the folder
- some peer probably auto-approved later arrivals
- some permissions were broadened or narrowed after the fact
- some disconnected or pending folders may still reconnect later
- some startup config likely spread a setting across a cohort
- some already synchronized bytes remain after disconnect
- some repair created a new instance and current behavior now looks calmer
- some supporting evidence exists, but only if logs were captured in time

Those are useful clues.
They are not the same as an explicit answer to `who actually consumed the relied-upon ruling, which named decisions or artifacts now depend on it, which consumers remain only inferred or unknown, and what retraction, revalidation, or reseal wave must occur if the source receipt is reopened or superseded?`

## Why that matters for AnonSync

AnonSync needs stronger post-finality truth than `the ruling was final enough for somebody`.
It needs to support claims such as:

- the ruling is final for a named automation class, but no consumption has yet been observed
- the ruling has been consumed by named downstream artifacts, but coverage is incomplete because some eligible consumers were never registered
- the ruling was consumed broadly, but a later superseding receipt has already triggered a revocation wave and not all artifacts are yet retracted
- the original receipt remains historically correct, but current outward dependence must move to the successor receipt
- the product cannot honestly say `all dependents are current` because some evidence of downstream consumption is older than the visibility horizon, missing, or instance-ambiguous
- the product can freeze new reliance immediately even though existing dependents still need revalidation or reseal work

AnonSync therefore needs first-class objects for **consumer registry, observed consumption, dependency coverage, unknown-consumer risk, stale derivative detection, revocation owner, revalidation requirement, and revocation-wave completion state** rather than leaving operators to reconstruct spread from linked devices, peer visibility, permission changes, reconnectable folders, startup config, short history, and repair folklore.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `who already depended on this and what now has to be unwound or refreshed?` — only by making the operator combine several partially overlapping operational surfaces:

- linked-device spread and auto-approval memory
- live permission mutation and owner topology
- pending and disconnected folder behavior
- startup config rollout and storage-root creation
- short-horizon UI and peer visibility
- restart-gated support evidence
- fresh-instance repair paths and clone warnings

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **downstream reliance governance** directly.
Its interface family should let the product separate at least these truths:

- audience allowed in principle
- consumer registered but not yet observed consuming
- consumer observed consuming
- dependent artifact derived and still current
- dependent artifact stale after supersession or reopen
- unknown-consumer risk still open
- revocation wave active
- revalidation pending
- reseal complete and downstream current again
- historical receipt preserved but no longer dependency-owning

That is why this revision adds five more first-class pages:
**Remedy-hardening-attestation-reliance contract sheet**, **Remedy-hardening-attestation-reliance review**, **Remedy-hardening-attestation-reliance proof**, **Remedy-hardening-attestation-reliance timeline**, and **Remedy-hardening-attestation-reliance lineage receipt**.

