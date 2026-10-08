# Resilio proxy artifact semantics, local-looking actions, and counterpart ambiguity evaluation

## Why this pass exists

The archive already had strong pages for bind outcome, posture, claim ceiling, quiescence, recovery witness locality, cleanup, and witness visibility.
What it still did not own tightly enough was one ordinary operator question that cuts across many of those seams:

- what kind of thing am I actually looking at in the file list right now
- is this entry a real local byte copy, a placeholder proxy, a conflict derivative, a hidden witness, or critical service state
- what subject does it actually stand for
- what does `delete`, `move`, `rename`, or `open` really mean for **this** artifact class

Current official Resilio docs still make that seam very real.
They are candid that `.rsls` placeholders are zero-byte stand-ins for data that may live elsewhere, that `Remove from this device` is different from all-peer deletion, and that deleting a placeholder with read-write access can remove the file from all peers.
They are also candid that `.Conflict` files are not harmless local clutter and should not simply be deleted, because they correspond to real remote material.

That honesty is useful.
The problem is that the product still leaves one everyday answer too article-shaped:

> `what kind of artifact is this visible entry, what canonical subject does it stand for, and what does a local-looking action actually do?`

## What current Resilio still gets right

Current official docs still publish several truths that are operationally valuable.

- **Placeholders are described as proxies, not fake full copies.** Current `What Is an RSLS File?` docs still say `.rsls` entries are placeholder files created by Selective Sync or Connected mode, that they represent file names without file content as zero-byte files, and that they can later be synced on demand.
- **Local reclaim is distinguished from global deletion.** Those same docs still say `Remove from this device` reverts a local copy to a placeholder while other peers keep their copies, and that deleting a placeholder with read-write access removes it permanently from all peers.
- **Last-full-copy risk is admitted.** Current docs still warn that if every peer reverts a file to a placeholder, the swarm can end up with placeholders only and no actual file.
- **Conflict derivatives are named as dangerous correspondents, not harmless duplicates.** Current `Conflict files in Sync` docs still say a `.Conflict` file appears when multiple versions try to map to one target name and explicitly warn operators not to just delete a `.Conflict` file or folder because it corresponds to the real file or folder on a remote peer.
- **Manual repair is described concretely.** Those same docs still say the safe fix is to move the healthy file out, delete the conflicted entries, eliminate the conflict factor, and then put the healthy file back.
- **The current v3 line is still live.** Official docs still show the v3 line through `3.1.2.1076` dated 31/Oct/2025.

That is strong candor.
Resilio is still willing to admit that visible filesystem entries can be proxies, derivatives, or dangerous correspondents rather than ordinary local files.

## Where current Resilio still stays too article-shaped

### 1. Visible entry class still depends on extension and folklore memory

The ordinary operator should not need to remember from prior help reading that:

- `.rsls` means placeholder proxy
- `.rlsc` means placeholder subfolder
- `.Conflict` means derivative standing in for a remote naming collision
- hidden `.sync` means critical service state, not user content

Current Resilio still tells those truths, but it still makes the operator reconstruct them from several articles rather than one typed artifact contract.

### 2. Local-looking verbs still hide non-local action scope

The visible action can still look deceptively local:

- delete placeholder
- remove from this device
- delete `.Conflict`
- reveal hidden Archive

But the actual effect may be:

- local eviction only
- all-peer deletion
- deletion of a real remote counterpart
- witness inspection only, not restore

AnonSync should not let a normal file-list verb hide that scope jump.

### 3. Counterpart identity is still under-owned

Resilio is candid that a `.Conflict` entry corresponds to a real remote file and that a placeholder stands for content that may live elsewhere.
But the product still does not give one reviewed page that answers:

- what canonical subject this row points at
- whether the row is the subject, a proxy for the subject, or a derivative of a collision
- what peers or witness stores are affected by action on it

### 4. Safe operator language still arrives too late

By the time an operator asks whether deleting a visible entry is `local cleanup`, `global deletion`, or `dangerous proxy manipulation`, they are already in a high-risk step.
That answer should be owned before the action, not reconstructed afterward from placeholder and conflict docs.

## What AnonSync should do instead

AnonSync should classify **artifact class** before executing artifact actions and should make counterpart scope explicit whenever a visible entry is not an ordinary local byte copy.

The product should own four page families:

1. **Proxy artifact review**
   - entry class, canonical subject, and current action scope
   - whether the row is plain local material, proxy, derivative, witness, or service state
   - strongest safe sentence before action

2. **Counterpart map**
   - visible entry versus canonical subject
   - local-only, all-peer, remote-counterpart, and witness-store effects
   - where the real bytes or affected copies actually live

3. **Proxy action substitution**
   - requested local-looking verb versus actual effect
   - safer alternatives when the requested action would overreach
   - mandatory wording rewrite before apply

4. **Proxy artifact receipt**
   - reviewed entry class
   - counterpart scope
   - executed or declined action meaning
   - strongest safe reuse sentence afterward

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that placeholders and conflict files are not ordinary local files. But it is not worth cloning the way current operators still have to infer, from extensions and scattered help articles, whether a visible entry is the subject itself, a proxy, a derivative, or critical hidden state — and what a local-looking delete or move would really do.

## New replacement pages added in this revision

- `557` Proxy artifact review
- `558` Counterpart map
- `559` Proxy action substitution
- `560` Proxy artifact receipt
