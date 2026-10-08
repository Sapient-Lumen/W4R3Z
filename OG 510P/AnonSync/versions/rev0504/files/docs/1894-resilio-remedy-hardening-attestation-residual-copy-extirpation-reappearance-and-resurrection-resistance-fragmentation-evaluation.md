# Resilio remedy hardening attestation residual-copy extirpation, reappearance, and resurrection-resistance fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for admitting that corrective action does not equal forgetting.
That candor matters.

The strongest current ingredients are:

- current `Disconnecting and Removing Folders` docs still say disconnect stops keeping the folder in sync but the folder remains in the file system and can still be accessed through a file browser
- the same docs still say reconnect can later happen from the disconnected state and may propose a different default path, creating a new directory with an added index if a same-name folder already exists
- the same docs still say even after removal from linked devices the folder may still remain available on remote devices not linked to the personal identity
- current `User Management` docs still say revoking a peer suspends future updates while all files synchronized so far remain in the folder
- current `Using Archive for file versioning and restoring deleted files` docs still say older or deleted copies are moved to Archive on other peers, desktops keep them there for 30 days by default, and restoring is manual
- current `Folder Types and Management` docs still say pending folders can auto-connect after prior approval and disconnected folders remain visible for later action
- current `Sync Storage folder` docs still say configuration, auxiliary settings, and shares' database live in ordinary storage paths that vary by runtime context
- current `Running Sync in configuration mode` docs still say the same settings can be applied on a number of different machines and that if no storage path is entered a `.sync` storage folder is created near the launched binary
- current `How to uninstall Sync?` docs still say settings or storage folders may need explicit manual deletion after uninstall
- current `Cloning Sync` docs still say cloning is unsupported and can create strange non-transferring twins

Those are useful truths.
They still do not add up to one typed answer to:

> `after a ruling was revoked or superseded, was the old statement merely hidden, or were the remaining copies actually extirpated strongly enough that reappearance is blocked at the required floor?`

## Where the current contract still fragments

The problem is not that Resilio denies residue.
The problem is that current residue truth is still scattered across folder state, Archive, identity linkage, storage-world guidance, uninstall guidance, and unsupported-clone warnings instead of being owned as one case-scoped forgetting contract.

Today an operator can often infer only weaker truths such as:

- synchronization stopped for this device or peer
- local bytes still remain on disk
- a disconnected lane can later reconnect
- a same-name folder may be re-created on reconnect
- old versions may still exist in hidden Archive
- remote devices outside the linked identity may still retain the folder
- runtime settings and databases still live in storage paths that must be manually removed
- the same configuration may cause future machines to inherit the same risky default
- clone-born or rebuilt instances may preserve or reanimate stale authority in strange ways

Those are important clues.
They are not the same as an explicit answer to `which residual loci still contain the old ruling or its enabling state, which of those loci are merely retained versus scheduled to expire, which were actually erased with evidence, which can still reappear on reconnect or rebuild, and what is the strongest honest forgetting sentence we can say now?`

## Why that matters for AnonSync

AnonSync needs stronger closure language than `delivered`, `acknowledged`, or even `stale surface suppressed`.
It needs to support claims such as:

- the old ruling is hidden from current dashboards, but archived export packets still exist through the stated retention window
- reachable dependents acknowledged the correction, but one disconnected lane can still reconnect and re-materialize the stale state under a new default path
- internal copies were cryptographically or administratively erased for the required cohort, but external unverified copies remain residually possible
- uninstall or decommission was performed, but storage-root deletion evidence is still missing for one service-world host
- manual archive expiration has not yet passed, so `forgotten` language remains blocked even though downstream-safe language for current use is allowed
- the source is historical only for the governed live cohort, but not yet resurrection-resistant for fresh worlds or future reconnects
- the product can certify `hidden`, `disconnected`, `scheduled-to-expire`, `erased with receipt`, `reconnect-revivable`, `clone-risk-open`, and `resurrection-resistant at named floor` separately instead of flattening them into one optimistic all-clear badge

AnonSync therefore needs first-class objects for **residual locus inventory, erase obligation, retention horizon, reconnect reappearance risk, rebuild reappearance risk, clone ambiguity risk, forgetting floor, and resurrection-resistance class** rather than leaving operators to assemble that truth from disconnect menus, Archive defaults, storage paths, uninstall checklists, and unsupported-clone warnings.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `did the old ruling actually stop existing strongly enough that it cannot come back in any governed place that matters?` — only by making the operator combine several partially overlapping operational surfaces:

- disconnect and peer revocation that stop future updates but leave prior files present
- reconnect paths that can revive the same share into a different path
- Archive retention that keeps older copies for a time and supports only manual restore
- linked versus unlinked device boundaries that limit what one removal actually removes
- storage folders that preserve configuration, logs, identity details, and share databases in ordinary filesystem paths
- config mode that can stamp the same defaults onto more machines
- uninstall guidance that still depends on manual deletion of settings or storage paths
- unsupported cloning that explicitly warns of strange twin behavior

That is enough to justify a harder product stance:

> AnonSync is not cloning Resilio because suppression is not forgetting, disconnection is not extirpation, and current residue truth is still reconstructed from several operational articles instead of owned by one stable page family that says what still exists, where it still exists, when it expires, what was actually erased, and whether resurrection is still possible.

