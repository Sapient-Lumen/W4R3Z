# Resilio detachment, revocation, roster-residue, and visibility fragmentation evaluation

## What current official docs still make clear

Another current Resilio pass strengthens the archive's clone-veto line rather than weakening it.

Current official docs still say several things that are operationally real and worth borrowing:

- clearing an offline device from **My Devices** does not unlink it; it only hides the record, and if that device comes back online it reappears
- unlinking a device is a local action that severs its links to other peers, and the docs explicitly say you cannot remotely unlink other devices
- disconnecting a folder is a one-device detachment: the folder remains in the file system, placeholders may be removed, and the folder can later be reconnected
- removing a folder is broader for linked devices, but the same content may still exist on remote devices that are not linked to your personal identity
- peer-level `Disconnect` in **User Management** revokes access for that selected peer going forward, but the bytes already synchronized to that peer stay in the folder
- uninstall guidance says unlinking and removing shares first is optional but otherwise the dead installation may continue showing up as an offline peer or device record; uninstall also leaves filesystem content and `.sync`/Archive residue unless cleared manually
- linking two devices that already have different certificates can cause one device to lose its certificate and have Advanced folders removed from the app without ordinary filesystem deletion, except on iOS where those Advanced folders are deleted from the file system

That is real candor.
It is useful product truth.

## What still should not be cloned

The operator is still asked to reconstruct several materially different questions from several different pages:

1. **did I only hide a record, or did I really sever future trust?**
2. **did I only stop future updates, or did I also remove bytes already present?**
3. **is this detachment local-only, linked-family-wide, or still ineffective against unlinked remote peers?**
4. **can this record come back on its own later?**
5. **what residue remains in storage, rosters, and remote possession after this action?**

Current Resilio docs still spread those answers across identity, folder management, user management, and uninstall guidance.

So a user can learn all the pieces and still not get one stable product answer to:

> after I hide, disconnect, remove, revoke, unlink, or uninstall, who still has access, what bytes still exist, which records can reappear, and what stronger cleanup sentence is still blocked?

That page-contract gap is exactly why AnonSync should not clone the behavior.

## Why this matters for AnonSync

AnonSync should borrow four habits directly:

- **say openly whether an action changes only visibility, future authority, byte residency, or all three**
- **say openly whether a remote record can reappear without another explicit approval step**
- **say openly when revocation stops future convergence but cannot retract already-landed bytes**
- **say openly when uninstall or unlink leaves roster or storage residue behind**

But AnonSync should reject five weaker habits:

- `Hide`, `Disconnect`, `Remove`, `Unlink`, and `Uninstall` actions that do not emit one effective detachment sentence
- revocation language that hides the difference between future-update suspension and byte retraction
- linked-family removal language that hides surviving unlinked remote peers
- cleanup flows that treat roster residue and storage residue as the same thing
- stale-record actions that suppress clutter while sounding stronger than the evidence allows

## Replacement pages added for this seam

This revision therefore adds six narrower replacement pages:

- `1247` — Detachment and revocation contract sheet
- `1248` — Offline roster visibility review
- `1249` — Access revocation proof
- `1250` — Installation clearance review
- `1251` — Detachment lineage receipt

These pages keep the Resilio candor and reject the scattered-detachment-contract problem.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that `hide`, `disconnect`, `remove`, `unlink`, `peer disconnect`, and `uninstall` are different truths; refuse any interface contract where the operator must reconstruct visibility change, future-update cutoff, byte residue, roster afterlife, and remote survivor scope from several separate help articles instead of one explicit detachment object.
