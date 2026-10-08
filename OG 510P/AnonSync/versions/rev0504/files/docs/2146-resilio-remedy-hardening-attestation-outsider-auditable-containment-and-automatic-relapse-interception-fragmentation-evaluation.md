# Resilio remedy-hardening attestation outsider auditable containment and automatic relapse interception fragmentation evaluation

## Why this seam matters now

The archive can already say:

- the outsider reached a clean state
- that clean state was portable enough to verify once
- the product can name a watch horizon
- the product can name several reopen channels
- the product can say whether those channels are merely watched or partially contained

That is still weaker than a harder question:

**if relapse begins, what actually stops or narrows stale spread before the outsider, the governed audience, or downstream consumers start relying on stale state again, and what proof survives that containment event later?**

A watched channel is not yet an intercepted channel.
An intercepted channel without proof is not yet auditable containment.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about several partial-containment ingredients, but it still spreads them across separate pages:

- `How to pause syncing` says pause stops only bit uploads/downloads while zero-sized files, deletions, rescans, and indexing still continue
- `Running Sync on schedule` says scheduled `Paused` is also a speed-zero posture with residual delete / rescan / indexing behavior and even asymmetric upload behavior relative to non-paused peers
- `User Management` says Read Only local edits do not propagate back, but they instead suspend future synchronization of the changed files for that peer unless overwrite behavior is chosen
- `Disconnecting and Removing Folders` says disconnect ends future synchronization for that device while the folder remains in the filesystem and stays accessible
- `Using Archive for file versioning and restoring deleted files` says restored older material may replay only if runtime is active and otherwise can be re-archived on later rescan
- `Sharing single file` says removing a file transfer from Sync UI does not remove it from the device
- `Can Resilio team see and block/remove any Sync folders?` says Resilio neither hosts nor can centrally remove shared data; removal can only happen on the users' own devices
- `Sharing a folder locally` says local shares are attached to the parenting share, inherit its limits, remain purely local, and can disappear or require manual reconnect when the source share changes

This is good containment-shaping candor.
It is not yet one first-class answer to **if stale state starts to re-enter, what channel is automatically intercepted, what channel only gets noticed later, how much spread may occur before containment, and what portable evidence proves the interception actually happened?**

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- a channel is watched
- a channel is automatically intercepted
- a channel is only slowed or narrowed
- a channel still leaves local residue or forwarded copies intact
- a channel can only be contained by operator help on every affected device
- a pause, disconnect, or read-only badge therefore counts as durable containment

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **recurrence-safe clean state and recontamination watch are weaker than auditable containment and automatic relapse interception**
- **watched reopen channels are weaker than interceptable reopen channels**
- **automatic interception without portable evidence is weaker than auditable containment**
- **pause, disconnect, read-only suspension, placeholder reversion, and UI removal may never impersonate `containment succeeded`**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- containment plane
- interceptable channel set
- non-interceptable residual channel set
- maximum spread before interception
- residue-after-containment class
- containment evidence artifact set
- strongest honest containment sentence
- blocked stronger containment sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **containment-interception contract sheet**
- **containment-interception review**
- **containment-interception proof**
- **containment-interception timeline**
- **containment-interception lineage receipt**
