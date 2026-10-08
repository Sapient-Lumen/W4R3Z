# Resilio copy-like tree identity carry, hidden control state, and unsupported clone evaluation

## What this pass is testing

This pass sharpens one narrower question the archive had only handled indirectly before:

> when a folder looks like ordinary bytes that can be copied, moved, backed up, or re-imported, does the product keep **payload bytes** and **continuity-bearing control state** visibly separate, or does a copy-like action quietly carry live subject identity with it?

Current official Resilio Sync docs make this seam unusually explicit.
They still say every synced folder gets a hidden `.sync` directory that is **critical** for syncing and contains the folder ID plus service files; moving or deleting it breaks synchronization.
They still say Sync recognizes a share by `.sync/ID`, so the same ID cannot be added twice on one device.
They still say `Service files missing / Cannot identify destination folder` can also happen when two Sync instances touch the same folder or the same external drive storage, and the repair path still includes `check Archive`, delete `.sync`, and add the share back.
They still say raw `Cloning Sync` is unsupported.
And a current troubleshooting page still says trying to sync the whole home folder can fail because it contains Sync's own storage folder with a `License` directory inside.

That is strong candor.
The non-clone problem is that ordinary operator intuition is still too copy-shaped.
A folder can look like ordinary bytes while also carrying hidden subject identity, continuity witnesses, and controller residue.
So one operator question still leaks across several pages:

- is this just a byte copy, or is it still the same managed subject because `.sync/ID` came along
- did I copy user data only, or user data plus controller state and hidden authority material
- is the safe next step attach, inspect-only, preserve-then-branch, strip controller state, or block as a foreign carry
- if I sanitize the tree, am I preserving continuity or creating a new local epoch
- what sentence is still honest afterward: `copied bytes`, `same managed subject`, `foreign managed carry`, or `clean branch created`

AnonSync should therefore not treat copy-looking intake as an ordinary path pick.
It should promote it into a first-class page family.

## Tightened non-clone line

Borrow Resilio's candor that hidden control state, unsupported cloning, same-ID detection, and repair boundaries are real.
Do **not** clone a contract where a folder copy still looks like ordinary bytes until support prose, hidden directories, and error strings finally reveal that subject identity came along for the ride.

## Required AnonSync replacement pages from this pass

- **Copied-tree posture**
- **Managed-tree intake review**
- **Control-state detachment**
- **Copy-like intake receipt**

## Replacement obligation in one sentence

Before AnonSync lets an operator attach, import, branch, sanitize, or reuse a copied-looking tree, it should publish whether the tree carries only payload bytes, payload plus hidden subject spine, foreign controller residue, or a contradictory mix that must not be treated as an ordinary folder.
