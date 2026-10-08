# Resilio remedy hardening attestation revocation delivery, acknowledgement, and stale-surface-suppression fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for being candid that spread is real, authority can move quickly, and old state can survive even after one operator action seems to close the story.
That candor matters.

The strongest present ingredients are:

- current `Sync Private Identity & Linking My Devices` docs still say linked devices automatically make all folders available everywhere and approvals can be issued from any linked device where the folder is present
- current `User Management` docs still say permissions can be modified on the fly and all linked devices under one identity act as Owners
- current `Disconnecting and Removing Folders` docs still say disconnect only affects one device while the folder remains in the file system and accessible through a file browser
- current `Folder Types and Management` docs still say pending folders may auto-connect after prior approval and disconnected folders remain visible for later action
- current `Sync Main View (Desktop)` docs still say the ordinary UI evidence horizon is a 30-day History surface and a peer list whose offline peers disconnect after 7 days
- current `Collecting debug logs automatically` docs still say deeper evidence often requires enable, restart, reproduce, and wait
- current `Using Archive for file versioning and restoring deleted files` docs still say older or deleted copies can persist in Archive and only manual restoring is possible
- current `Running Sync in configuration mode` docs still say one configuration can be applied across a number of different machines
- current `Cloning Sync` docs still say unsupported copies can create strange behavior and non-transferring twins

## Where the current contract still fragments

The problem is not that Resilio hides spread or residue.
The problem is that it still does not produce a first-class, case-scoped **revocation delivery and closure** object.

Today an operator can often infer only weaker truths such as:

- a permission was lowered or a folder was disconnected somewhere
- a linked device probably also saw the change because linked devices share ownership authority
- some pending or disconnected instance may reconnect later
- some local bytes still remain on disk after disconnect
- some old version may still exist in Archive
- some event probably appeared in short-horizon History
- some deeper proof may exist, but only if logs were captured after a restart in time
- some cohort probably got configuration changes at next start
- some weird residual state may exist if there was instance cloning or fresh-instance repair

Those are useful clues.
They are not the same as an explicit answer to `did the revocation, revalidation request, or successor-binding actually reach every named dependent, was it acknowledged by the reachable dependents, were stale derivative surfaces suppressed, and which unreachable or unverifiable dependents still keep the old ruling effectively live?`

## Why that matters for AnonSync

AnonSync needs stronger post-revocation truth than `a wave was opened` or `notifications were sent`.
It needs to support claims such as:

- the revocation order exists, but only two of six registered consumers were reachable on a callback path
- all reachable consumers acknowledged receipt, but one stale export remains externally live and cannot yet be suppressed
- new reliance is frozen, three dashboards are hidden, and one downstream receipt is still pending successor reseal
- the original source is historical only for internal consumers, but not yet historical only for external consumers because one delivery channel is unverifiable
- the product cannot honestly say `downstream safe again` because one previously registered consumer has not acknowledged and one disconnected lane may reconnect later
- the product can separately certify `delivered`, `acknowledged`, `suppressed`, `resealed`, and `still residually live` instead of hiding them inside one optimistic badge

AnonSync therefore needs first-class objects for **callback reachability, delivery coverage, acknowledgement coverage, stale-surface suppression, unreachable-dependent risk, escalation owner, closure threshold, and residual-live-surface class** rather than leaving operators to reconstruct closure from permission changes, disconnects, pending folders, short history, archives, startup config, and support capture folklore.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `did the old ruling truly stop being live everywhere that mattered?` — only by making the operator combine several partially overlapping operational surfaces:

- linked-device spread and approval from any linked device
- live permission mutation and owner topology
- disconnect that leaves local bytes present
- pending and disconnected folders that can later reconnect or stay visible
- short-horizon UI surfaces and peer expiry
- Archive residue and manual restore paths
- startup config rollout across multiple machines
- restart-gated debug evidence and clone ambiguity

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **revocation delivery and closure** directly.
Its interface family should let the product separate at least these truths:

- revocation required
- callback path known
- delivery attempted
- delivery confirmed
- acknowledgement received
- successor receipt accepted
- stale surface suppressed
- external stale copy still live
- unreachable dependent risk open
- closure threshold met for named cohort only
- global downstream-safe sentence still blocked
- residual-live-surface debt preserved for later escalation

That is why this revision adds five more first-class pages:
**Remedy-hardening-attestation-revocation-delivery contract sheet**, **Remedy-hardening-attestation-revocation-delivery review**, **Remedy-hardening-attestation-revocation-delivery proof**, **Remedy-hardening-attestation-revocation-delivery timeline**, and **Remedy-hardening-attestation-revocation-delivery lineage receipt**.
