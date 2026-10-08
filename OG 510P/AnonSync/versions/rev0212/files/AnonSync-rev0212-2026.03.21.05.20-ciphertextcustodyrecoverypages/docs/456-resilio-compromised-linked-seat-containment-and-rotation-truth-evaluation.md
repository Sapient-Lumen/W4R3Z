# Resilio compromised linked-seat containment and rotation truth evaluation

## Why this pass exists

The archive already had broad compromise response, trust rotation, seat-lineage review, and warning/blast-radius pages.
Those were necessary, but another current Resilio pass shows a still-missing ordinary seam.
The problem is no longer only `can authority be revoked`.
It is now:

- if one linked seat is stolen or otherwise compromised, what **live authority** does it still carry right now?
- what is the **narrowest believable cutoff** the operator can still perform?
- when do current Resilio rules force a **whole-identity rebuild** instead of a seat-local kill switch?
- after any cutoff, what **already-landed bytes and residual authority** still remain outside the operator's immediate reach?

That is where current official Resilio docs stay useful yet still become too article-shaped.

## What current Resilio still gets right

Current official material is still admirably candid about incident response reality.

Examples the docs still openly describe include:

- **At-rest protection matters immediately**: the stolen-device article still says that if the drive on the stolen device was encrypted, there is nothing to worry about because the data is not accessible without a decryption key.
- **An unencrypted linked seat is dangerous right away**: the same article still says that if the drive was not encrypted, the thief can potentially run Sync on the stolen device and therefore view, modify, or remove data on other linked devices.
- **Linked seats are not low-authority replicas**: current user-management docs still say that when devices are linked under one identity, all of those devices act as Owners.
- **Per-subject disconnect is real but limited**: current user-management docs still say `Disconnect` revokes future updates for the selected peer, yet all files already synchronized so far remain in that peer's folder.
- **There is still no remote unlink for linked seats**: current private-identity docs still say you cannot remotely unlink other devices.
- **The documented stolen-seat response is broad on purpose**: the current stolen-device article still recommends backing up data, removing shares, unlinking the remaining devices from the current identity, removing synced data from the storage folder, reinstalling Sync, regenerating identity, relinking devices, and resharing folders.
- **License re-home is also explicit**: the same article still says that re-adding the Pro license overrides the previous activation, and that if the thief later runs Sync online, the stolen instance reverts to Free.
- **Resilio does at least acknowledge a safer pattern for intentionally untrusted hardware**: the encrypted-folders docs still say that encrypted peers are for untrusted devices because the destination stores only encrypted bytes and cannot decrypt them.

That candor matters.
Resilio is not pretending a stolen linked owner seat is a harmless offline row.

## Where the current page shape still fails

The ordinary operator answer is still reconstructed across too many articles and too many response scales.

### 1. Immediate risk is still article-dependent

The operator still has to reconstruct whether this is basically harmless, locally serious, or constellation-wide by hopping across:

- the stolen-device article for disk-encryption posture
- user-management for owner authority and disconnect semantics
- identity-linking docs for remote-unlink impossibility
- licensing notes for seat-activation recovery
- encrypted-folder docs for the separate untrusted-peer pattern

That is too much reconstruction for one ordinary incident question.

### 2. Narrow cutoff versus broad rebuild is still not one page

Current docs still leave the operator to infer whether the honest next action is:

- disconnecting specific remote peers from specific subjects
- ignoring stale list rows
- unlinking the remaining trusted cohort from the current identity
- regenerating identity material for the whole cohort
- resharing everything under a new authority epoch

Those are not variants of one button.
They are different containment lanes with different blast radii.

### 3. Residual authority still hides in prose

Current docs are honest that already-synchronized files remain after disconnect, and that a stolen unencrypted linked seat may have enough authority to affect other linked devices.
But the product contract still does not give one ordinary page that answers:

- what the suspect seat can still do now
- what already-landed bytes are already outside immediate recall
- what has been cut off only for the future
- what still depends on broader identity rotation instead of seat-local action

That is still too much prose for one trust decision.

### 4. The rotation sequence is still ritual-shaped

The official response is practical, but it is still largely a ritual chain:

- backup
- remove shares
- unlink current identity
- remove synced data from storage
- reinstall
- regenerate identity
- relink
- reshare

Useful support advice is not the same thing as a good everyday page contract.
The operator still has to infer what was preserved, what was intentionally abandoned, and what has not yet been reissued.

## What AnonSync should do instead

AnonSync should keep the candor and reject the ritual sprawl.
The product should split this seam into four page families:

1. **Compromised seat**
   - at-rest protection posture
   - strongest current live-authority claim
   - what the suspect seat can still do if it returns online
   - first safe action floor

2. **Containment lane**
   - narrowest believable cutoff now
   - subject-local disconnect versus cohort-wide identity rotation
   - which actions are impossible, unavailable, or insufficient
   - strongest residual exposure after each lane

3. **Rotation rebuild**
   - trusted-survivor cohort
   - new identity / authority epoch sequence
   - relink / reshare / reissue order
   - what continuity survives versus what is deliberately rebuilt

4. **Residual authority**
   - already-landed bytes and why they remain
   - uncut local possession versus future-update cutoff
   - pending proof of cutoff and pending rotation tasks
   - final receipt of what is still unresolved

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that an unencrypted stolen linked seat is serious, that linked seats under one identity are owners, that remote unlink is unavailable, and that broad rotation may be necessary. But it is not worth cloning the way ordinary answers to `what can this suspect seat still do`, `what is the narrowest believable cutoff`, `when is whole-identity rotation required`, and `what residual authority still remains afterward` still sprawl across a stolen-device note, identity-linking docs, user-management docs, licensing behavior, and encrypted-peer guidance instead of one stable page family.

## New replacement pages added in this revision

- `457` Compromised seat
- `458` Containment lane
- `459` Rotation rebuild
- `460` Residual authority

