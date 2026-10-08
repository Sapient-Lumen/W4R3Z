# Resilio remedy-hardening attestation outsider bounded remediation and remedial exposure budget fragmentation evaluation

## Why this seam matters now

The archive can already say:

- the corrected replacement is discoverable
- the corrected replacement explains why it supersedes the stale thing
- a late outsider may trust that successor claim
- a late outsider may even have a usable self-service remediation path

That is still weaker than a harder question:

**if the late outsider remediates from that surface, does the remedy path stay within the reviewed disclosure, authority, forwarding, and retention budget, or did the product buy self-service by quietly widening exposure?**

Actionability is not yet bounded safety.
A remedy path can be self-service and still be too broad.
Without an explicit leak-budget contract, `they can fix themselves from here` quietly expands into folklore about `and this was a safe way to let them do it`.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about several exposure-shaping ingredients, but it still spreads them across separate pages:

- `Sharing single file` says a generated file-transfer link can be made never-expiring, everyone who gets the link can download the files, there is no option to restrict number of uses or devices, recipients can share the files further, and removing the file from Sync UI does not remove it from the device
- `Sync Share Dialog (Desktop)` says folder-share links can be copied into e-mail or messengers, approval can be disabled so syncing starts automatically, approvals can be limited to new peers or required for all peers, and the link can have expiration and click-count limits
- `What's the difference between Standard and Advanced folders?` says only Owners can share Advanced folders onward, while Standard-folder peers can share the key they have without limitation
- `User Management` says all linked devices under one identity act as Owners, Owners can invite new users, and disconnecting a peer stops future updates while already synchronized files remain in the folder
- `Link structure and flow` says links are designed for easy handoff through a landing page into the app or for manual addition, which is reach-friendly but not itself a bounded-exposure verdict

This is good implementation candor.
It is not yet one first-class answer to **if the outsider can remediate, what audience breadth, onward spread, permission widening, and durable residue did that remediation path carry with it?**

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- the outsider can trust the corrected replacement
- the outsider can reach a working remediation carrier
- the remediation carrier is a bearer link anyone can reuse
- the carrier may never expire or may allow broad forwarding
- some permission topology may let the recipient widen access further
- already delivered copies may remain after disconnect or UI removal
- the outsider therefore had a safe remediation path

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **outsider actionable reliance and operator-free remediation are weaker than bounded-exposure remediation and remedial leak-budget truth**
- **a self-service remedy path that quietly broadens audience, resharing, or residue is weaker than a narrower but honestly bounded remedy path**
- **bearer-link convenience, unlimited downloadability, owner-right widening, or local-retention residue may never impersonate `safe outsider self-service remediation`**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- remediation carrier class
- audience breadth class
- onward-reshare class
- permission-widening class
- expiry and click-budget class
- retention-residue class
- strongest honest safe-remedy sentence
- blocked stronger bounded-exposure sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **remediation-exposure contract sheet**
- **remediation-exposure review**
- **remediation-exposure proof**
- **remediation-exposure timeline**
- **remediation-exposure lineage receipt**
