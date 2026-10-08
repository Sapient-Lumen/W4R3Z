# Resilio visual absence, hide/disconnect/remove/unlink scope evaluation

## Why this pass exists

The archive already had disconnect contracts, hidden-offline rows, compromise rotation, placeholder eviction, and departure semantics.
Those were necessary, but another current Resilio pass shows one still-missing ordinary seam.

The problem is no longer only `what happens when I disconnect`.
It is now:

- when a row disappears, what **actually ceased to exist** versus what merely stopped showing
- when bytes are removed locally, what **authority or remote retention** still remains
- when an operator says `make this gone`, what is the **narrowest believable severance lane**
- when is the honest answer that **seat-local severance is insufficient** and broader identity rotation is still required

That is where current official Resilio docs stay useful yet still become too article-shaped.

## What current Resilio still gets right

Current official material is still admirably candid about severance scope.

Examples the docs still openly describe include:

- **Hiding is not unlinking**: the current `How to clear offline devices?` article still says clearing an offline device only hides it from view, does not unlink it, and the row will reappear if the device comes back online.
- **Disconnect is seat-local**: the current `Disconnecting and Removing Folders` article still says disconnect only affects one device and that the folder remains in the file system.
- **Remove is identity-scoped, not universal**: that same article still says remove affects devices linked with your personal identity, yet may still leave the folder available on remote devices not linked to that identity.
- **Placeholder-local eviction is a different class**: current `Synchronization Modes` and `What Is an RSLS File?` docs still say `Remove from this device` only reverts a file or subtree to placeholders locally.
- **Global placeholder deletion is explicitly broader**: those same docs still say `Remove from all devices` deletes the file or subtree from all peers and archives it there.
- **Unlink is local-only**: current identity-linking docs still say you can unlink this device, but you cannot remotely unlink other devices.
- **Broad compromise response is acknowledged when needed**: the current stolen-device article still says the serious response path can require removing shares, unlinking trusted devices from the current identity, removing synced data from the storage folder, reinstalling, regenerating identity, relinking, and resharing.

That candor matters.
Resilio is not pretending every disappearance verb means the same thing.

## Where the current page shape still fails

The ordinary operator answer is still reconstructed across too many articles and too many departure scales.

### 1. Visual absence still overstates severance

Current docs still let several materially different situations produce a subject that looks absent or diminished:

- hidden offline device rows
- disconnected pathless subjects
- placeholder-only local presence
- removed-from-linked-identity subjects
- locally unlinked seats
- rebuilt post-rotation identities

Those are not the same state.
Yet the product contract still leaves the operator to assemble the distinction from multiple help pages.

### 2. Residual authority still hides behind local cleanup verbs

Current docs are honest that:

- a hidden device can return
- a disconnected subject still leaves bytes in the local file system
- a removed linked subject may still exist on remote non-linked retainers
- a local placeholder reversion still leaves the file elsewhere
- a local unlink does not remotely kill another seat

But there is still no ordinary page that says, in one place:

- what exact thing stopped existing
- what exact thing is still able to return
- what exact thing is merely outside current view
- what exact thing still requires broader rotation to contain

### 3. The narrower-cutoff ladder is still archaeological

The operator still has to infer whether the right action is:

- hide the row
- disconnect locally
- remove from linked seats
- delete the subject everywhere
- unlink the local seat
- rotate identity and rebuild the trusted cohort

Those are not variants of one button.
They are different severance ladders with different truth claims and different residual risk.

### 4. Receipts are still weak on what remains

Current docs explain behaviors in prose, but they still do not give one product-owned receipt that proves:

- the chosen severance class
- local row effect
- local byte effect
- linked-cohort effect
- external-retainer possibility
- return contract
- whether broader rotation is still pending

That is still too much memory burden for a routine operator question.

## What AnonSync should do instead

AnonSync should keep the candor and reject the departure sprawl.
The product should split this seam into four page families:

1. **Severance review**
   - requested disappearance verb
   - narrowest believable severance lane
   - what remains visible, reconnectable, or archived
   - stronger alternatives when the chosen action is insufficient

2. **Absence versus authority**
   - hidden row versus disconnected subject versus retired subject
   - residual byte possession
   - residual authority and reappearance triggers
   - strongest current claim about what still exists elsewhere

3. **Severance scope graph**
   - seat-local consequences
   - identity-linked cohort consequences
   - external-retainer possibilities
   - byte residue and archive consequences

4. **Severance receipt**
   - requested action versus effective action
   - scope actually touched
   - return contract
   - residual risk and pending stronger containment

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that hiding, disconnecting, removing, placeholder eviction, unlinking, and identity rebuild are materially different. But it is not worth cloning the way ordinary answers to `is this actually gone`, `who can still bring it back`, `what still exists elsewhere`, and `when is broader rotation still required` still sprawl across offline-device notes, disconnect/remove docs, placeholder docs, identity-linking docs, and stolen-device recovery guidance instead of one stable severance page family.

## New replacement pages added in this revision

- `522` Severance review
- `523` Absence versus authority
- `524` Severance scope graph
- `525` Severance receipt
