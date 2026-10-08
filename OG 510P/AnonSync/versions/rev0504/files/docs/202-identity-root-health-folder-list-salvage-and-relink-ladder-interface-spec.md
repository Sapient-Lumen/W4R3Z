# Identity-root health, folder-list salvage, and relink ladder interface spec

## Purpose

The archive already had compromise response, seat-switch attribution, and repair-ladder language.
What it still lacked was one explicit contract for a harsher control-plane failure:

> when the local identity root is missing or corrupted and the folder list disappears, what page proves whether the operator can salvage control-plane continuity, what data still survives on disk, and when a reset or reinstall is actually necessary?

Current official Resilio docs make this seam sharper than a generic `relink device` suggestion would.
Their current core warnings still say `Failed to sync list of folders` can mean hidden `.SyncUser###` state in the storage folder is missing, its `.sync` subfolder is missing, or `identity.dat` is missing or damaged.
The same guidance still sends recovery toward `Unlink`, creating a new identity, and relinking devices.
A related current error page still says `SE_SM_NO_IDENTITY` usually means the current identity is missing or corrupt after crashes, bad shutdown, system update, or restore from backup; it advises `Unlink`, recreate identity, and, if the `My devices` page is blank, reinstall the app.

That is practical support advice.
It is still not a good public identity-root recovery contract.

## Core decision

AnonSync should make **identity-root health** first-class and **salvage-oriented**.

Every identity-root incident must declare:

- what exact identity/control-plane objects are missing, unreadable, mismatched, or stale
- whether local subject bindings on disk still appear recoverable
- whether membership and trust continuity can be preserved
- what the least-destructive control-plane repair is
- when full reset or reinstall is truly necessary

If an operator still has to jump straight from `folder list failed` to `unlink` or `reinstall`, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal eight truths AnonSync should not clone:

- identity-root corruption is still described through hidden storage artifacts rather than one visible health page
- the symptom can be `failed to sync list of folders`, which sounds like content trouble even though the damage is really at the control plane
- `unlink and recreate identity` is a very strong action yet is still given as a default fix path
- a blank `My devices` view can escalate all the way to `reinstall`, which broadens the blast radius without one salvage review
- crashes, improper shutdown, system update, and restore-from-backup are all cited as causes, meaning the event class is broader than one rare corruption bug
- files on disk may still exist even while the control plane cannot describe them correctly
- relinking can restore some convenience while also changing continuity semantics
- identity-root repair deserves explicit proof about what survived rather than one binary `works / does not work` result

AnonSync should therefore keep one stronger rule:

> every identity-root incident must publish a salvage ladder before any identity-reset action: what survives, what can be reconstructed, and what continuity claim would be lost by resetting.

## Fixed review order

Every non-trivial identity-root incident should render the same sections in the same order:

1. **Identity-root evidence now**
2. **Salvage ladder**
3. **Continuity and trust impact**
4. **Receipt and replay promise**

### 1) Identity-root evidence now

This section should show:

- current execution seat
- identity-root path
- missing or unreadable control-plane objects
- whether the subject registry is intact, partial, stale, or unreadable
- whether local path binds are discoverable independently of the damaged identity root
- strongest evidence for the diagnosis

The operator must be able to answer: **what part of the local identity/control plane is actually broken?**

### 2) Salvage ladder

This section should show ordered candidate steps such as:

- reopen or rescan identity root
- restore identity-root snapshot from recent verified backup
- reconstruct subject registry from surviving local receipts/path binds
- relink to a known trusted successor while preserving local bytes
- create a new local identity with continuity explicitly broken
- reinstall runtime after exporting all remaining evidence

Each step must declare:

- prerequisite evidence
- continuity class
- local-byte risk
- membership/trust impact
- whether it is reversible

The operator must be able to answer: **what is the least-destructive way back to a working control plane?**

### 3) Continuity and trust impact

This section should show:

- whether current local identity continuity is preserved, degraded, or broken
- whether existing trust approvals remain valid
- whether linked peers will see a successor, a repaired same identity root, or a completely new identity
- whether any local subject claims will need re-approval or re-attestation

The operator must be able to answer: **what relationship to peers survives if I take this recovery step?**

### 4) Receipt and replay promise

This section should show:

- chosen salvage or reset action
- recovered or lost control-plane objects
- continuity result
- whether relinking or reapproval is still pending
- durable recovery receipt and sealed evidence pointers

The operator must be able to answer: **what exactly did the system recover, and what identity/trust continuity remains afterwards?**

## Main surface

The local web shell should expose an **Identity health** page whenever any of these fail:

- identity-root parse
- local membership ledger load
- subject registry load
- trust-material read
- local seat continuity proof

That page must not be a thin wrapper around `Start over`.
It should immediately classify:

- `recoverable from local identity snapshot`
- `control-plane partial; local bytes still discoverable`
- `trust continuity uncertain; relink review required`
- `control-plane empty and evidence weak; full reset may be necessary`

## Object model implications

AnonSync should add or strengthen these objects:

- `identity_root_health_case`
- `subject_registry_snapshot`
- `control_plane_salvage_review`
- `identity_reset_review`
- `relink_continuity_case`
- `identity_health_receipt`

Suggested fields for `identity_root_health_case`:

- `seat_id`
- `identity_root_path`
- `missing_objects[]`
- `damaged_objects[]`
- `surviving_subject_receipts[]`
- `surviving_membership_receipts[]`
- `continuity_confidence`
- `recommended_salvage_steps[]`

## Cross-link with compromise and seat-switch models

This spec intentionally differs from earlier ones:

- **compromise response** asks whether trust should be rotated on purpose
- **runtime seat switch** asks whether a different principal/storage root explains the empty world
- **identity-root health** asks whether the same seat and same intent now lack a readable control plane

The page should show those alternatives side by side so operators do not confuse:
- damaged identity root
- intentional seat switch
- compromise rotation
- ordinary first-run

## Failure and edge cases

### Blank device list but local subjects still on disk

The interface should classify this as:
`control plane missing; local data candidates found`
not
`no data present`

### Restored-from-backup drift

If control-plane objects were restored from an old backup while subjects changed later, the system must show:
- backup age
- likely stale objects
- which subjects need receipt refresh or peer attestation

### Unreadable identity root with intact state snapshots

If automatic snapshots exist, the ladder should strongly prefer `restore snapshot` over `new identity`.

### Reset that would sever approvals

A reset review must explicitly say when the action will invalidate prior approvals, successor expectations, or linked-device posture.

## Event language

Event stream language should use explicit phrases:

- `identity-root object missing`
- `subject registry unreadable`
- `local bytes discoverable despite control-plane loss`
- `salvage restored same continuity class`
- `identity reset created new local lineage`

Avoid vague lines like:
- `profile error`
- `settings failed`
- `linking issue`

## The non-clone reason

This is another clean example of why AnonSync should not merely copy Resilio's surface.
Current Resilio docs still send identity-root failure toward hidden-folder diagnosis, unlink, and sometimes reinstall, even though local bytes may still exist and continuity questions are the real problem.
AnonSync should instead publish one visible salvage ladder that separates local-byte survival, control-plane survival, and trust continuity before any reset is allowed.
