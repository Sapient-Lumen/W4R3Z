# Resilio creditor quorum, succession, and conflict-authority fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- distinguish verified creditors from contested residue
- distinguish representatives from principals
- type the scope of each representative
- reopen closure when an apparent releasor turned out to be stale or over-scoped

What it still lacked was the next harder operator answer when **a representative is valid, but one valid representative may still not be enough**:

> is this one signer sufficient, is a countersigner or quorum still required, what happens if co-representatives disagree, and how does successor authority inherit or fail to inherit the predecessor's closure power?

That is the seam this pass locks.
A product that can say `manager valid for this creditor` but cannot say `manager may only countersign after finance signs`, or `either of two delegates may acknowledge payment but both must sign final waiver`, is still overstating finality.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real **identity, owner, and permission-control fragments**, but not one operator-facing collective-release contract:

- `Sync functionality in detail` still says folders have Read Only, Read & Write, and Owner permissions, and that owners can share the folder, change permissions, and revoke access.
- `Sync Private Identity & Linking My Devices` still says each installation gets a unique certificate, linked devices can approve from any linked device, and linked devices automatically receive the folder roster.
- `User Management` still says on-the-fly permission changes are available only for Advanced folders.
- `Sync Share Dialog (Desktop)` still says only peers with Owner access can share Advanced folders, while Standard folders have no Owner permission level and all peers can share onward.
- `What's the difference between Standard and Advanced folders?` still says only Owner can share Advanced folders, while Standard folders allow further sharing without that Owner layer and display linked devices as separate entities rather than one user identity.
- `How to create a Read Only folder while syncing across linked devices?` still says My Devices automatically sync folders to linked devices with Owner permission.
- `Sharing a folder locally` still says there is no way to give local share Owner permissions, local-share access changes may require remove-and-reshare, and local share authority follows source-folder access changes.
- `Disconnecting and Removing Folders` still says removing a folder affects all devices linked with your identity, while remote devices not linked to that identity may still retain availability.

## What current Resilio still gets right

### 1) It is explicit about operational powers

Owner, Read & Write, and Read Only are meaningful operational distinctions.
That is worth borrowing.

### 2) It is candid about authority propagation inside an identity family

Linked devices receiving the same folder roster, approvals from any linked device, and Owner rights following linked-device identity are all honest statements about operational convenience.
That is useful.

### 3) It acknowledges asymmetry between source and derivative control

Advanced vs Standard folders and source share vs local share are not flattened into one simple power story.
That asymmetry is informative.

## Where current Resilio still fragments the operator answer

### A) Owner is a power class, not a sufficient-release coalition rule

Resilio can tell you who may share, revoke, or change access.
It does not tell you whether one Owner is sufficient for final release, whether two departments must countersign, or whether a quorum is needed before harm can be waived.

### B) Linked-device convenience overstates closure sufficiency

Approvals from any linked device and automatic Owner presence across linked devices are great for continuity.
They still do not say whether any one such device or operator is enough to bind the creditor finally.

### C) Split authority is not modeled as split authority

Resilio permissioning is strong at `can share / can write / can revoke`.
It still does not expose typed split authority such as `ops may acknowledge receipt`, `finance must confirm reserve repair`, and `principal must sign final waiver`.

### D) Successor authority is not rendered as a first-class closure problem

If an earlier representative exits, a role changes hands, or a linked-device identity story changes, current docs do not provide one typed page saying which earlier commitments survive, what successor inherits, and whether earlier signatures remain sufficient.

### E) Conflict between valid speakers has no first-class settlement surface

Resilio lets the operator govern sharing and permissions.
It still does not expose an object for `two valid representatives disagree, therefore final closure freezes while narrower acts remain intact`.

## Resulting product decision

AnonSync should borrow Resilio's identity, permission, and owner mechanics where they help route and bound operational control.
It should **not** clone a product shape where one valid representative is casually treated as a sufficient releasor without first-class quorum, countersign, succession, and conflict rules.

AnonSync should instead expose:

- one first-class **Creditor coalition contract sheet**
- one **Creditor coalition review** page
- one **Closure sufficiency proof** page
- one **Creditor coalition timeline**
- one durable **Creditor coalition lineage receipt**

## Hard decisions locked by this pass

- **verified full-scope representative is weaker than sufficient releasor coalition**
- **single-signer, countersigned, quorum, unanimous, and adjudicated closure are distinct public truths**
- **silence, unreachable peers, or passive non-objection may not silently count toward quorum unless the rule explicitly allows it**
- **successor authority inherits only the powers expressly carried forward; predecessor signatures do not automatically grant successor closure rights**
- **conflict among otherwise-valid representatives freezes stronger closure while narrower acts that were independently valid may remain intact**
- **final release, probation lift, and future-burst normalization require the sufficiency rule to be met, not merely one valid signature**
