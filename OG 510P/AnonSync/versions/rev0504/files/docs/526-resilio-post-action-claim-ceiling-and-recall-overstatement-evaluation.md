# Resilio post-action claim ceiling and recall overstatement evaluation

## Why this pass exists

The archive already had revocation, delete-scope, compromised-seat, residual-authority, and severance-truth pages.
Those were necessary, but another current Resilio pass shows one more ordinary seam that still deserves first-class product ownership.
The problem is no longer only `what action happened`.
It is now:

- after a disconnect / revoke / remove / unlink / delete gesture, **what sentence is the product actually allowed to say**?
- what narrower statement is true when broader wording such as `gone`, `revoked`, `deleted everywhere`, or `secured` would overclaim?
- what residue classes must remain adjacent to any post-action statement?
- what language must the product actively forbid because the action did not earn that claim?

That is where current official Resilio docs stay useful yet still become too article-shaped.

## What current Resilio still gets right

Current official material is still admirably candid about the claim ceiling of several common actions.

Examples the docs still openly describe include:

- **Peer disconnect is future-updates-only**: current `User Management` docs still say `Disconnect` revokes access to future updates for the selected peer, while all files synchronized so far remain in that peer's folder.
- **Folder disconnect is not byte recall**: current `Disconnecting and Removing Folders` docs still say disconnect stops syncing on one device but leaves the folder in the local file system.
- **Identity-linked remove is not universal erase**: that same article still says remove affects devices linked to your identity, yet the folder may remain on remote devices that are not linked to your personal identity.
- **Placeholder-local eviction is a narrower truth than delete**: current `Synchronization Modes`, `What Is an RSLS File?`, and iOS interface docs still distinguish `Remove from this device` from wider deletion.
- **Global delete still has retained-history consequences**: those same docs still say `Remove from all devices` removes the file from peers and puts it into Archive there.
- **Unlink cannot support a remote-total-control claim**: current identity-linking docs still say you cannot remotely unlink other devices.
- **Serious compromise response admits seat-local verbs are insufficient**: current stolen-device docs still escalate some incidents to identity regeneration, relink, and reshare instead of pretending a narrower action fully solved the problem.

That candor matters.
Resilio is not pretending every successful menu action earns the same post-action sentence.

## Where the current page shape still fails

The ordinary operator answer is still reconstructed across too many articles and too many verbs.

### 1. The product still lacks one owned claim translator

Current docs still let the operator bounce among words like:

- disconnect
- remove
- revoke
- unlink
- remove from this device
- remove from all devices
- stolen-device recovery

Each word is real, but none of them alone tells the operator what sentence is now safe to say to another person.
The interface contract still leaves that translation burden outside the product.

### 2. Action success and statement truth still blur together

A button may succeed while a broader claim remains false.
For example, current docs still make clear that:

- a peer can be disconnected yet still keep landed bytes
- a local folder can be removed from linked seats while external retainers may still exist
- a placeholder can be evicted locally while the subject still exists elsewhere
- a device can be unlinked locally while other devices stay linked
- a compromised-seat response can still require broader rotation before `contained` is an honest sentence

That means `action succeeded` and `broad claim earned` are not the same thing.
Current Resilio help is candid about that, but the product contract still does not own it as one everyday workflow.

### 3. The claim ceiling is still too easy to overstate socially

Operators often need to tell someone else what happened:

- `I removed it`
- `their access is gone`
- `the data is deleted`
- `that device is off the roster`
- `the incident is contained`

Current official docs give the ingredients for a better answer, but the operator still has to build that answer manually from several pages.
That is a reliability problem, not merely a wording preference.

### 4. Receipts still preserve the action better than the statement

Current docs explain how actions behave, but they still do not give one durable statement object that proves:

- requested verb
- effective action class
- strongest safe post-action sentence
- stronger forbidden sentence
- residual-scope basis for the limit
- strongest next escalation if the desired statement was not earned

That is still too much memory burden for an ordinary operational handoff.

## What AnonSync should do instead

AnonSync should keep the candor and reject the overstatement gap.
The product should split this seam into four page families:

1. **Action claim review**
   - requested verb versus effective action class
   - strongest safe sentence after apply
   - stronger forbidden sentences
   - why the claim ceiling stops where it does

2. **Residual claim matrix**
   - local bytes, linked-cohort reach, external retainer possibility, history / archive residue
   - per-plane proof of what still exists or may return
   - claim-by-claim support and contradiction

3. **Safe language substitution**
   - rewrite unsafe phrases into product-earned sentences
   - tune the sentence for operator, teammate, admin, or external recipient audiences
   - keep caveats attached to the sentence instead of in separate help prose

4. **Action statement receipt**
   - requested statement
   - effective statement the product can stand behind
   - forbidden stronger claims
   - residual risk and stronger next action if needed

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that disconnect, revoke, remove, placeholder eviction, unlink, global delete, and compromise rotation have different truth ceilings. But it is not worth cloning the way the operator still has to assemble the safe post-action sentence from user-management notes, disconnect/remove docs, placeholder docs, identity-linking limits, and stolen-device recovery guidance instead of getting one stable claim-owned page family.

## New replacement pages added in this revision

- `527` Action claim review
- `528` Residual claim matrix
- `529` Safe language substitution
- `530` Action statement receipt
