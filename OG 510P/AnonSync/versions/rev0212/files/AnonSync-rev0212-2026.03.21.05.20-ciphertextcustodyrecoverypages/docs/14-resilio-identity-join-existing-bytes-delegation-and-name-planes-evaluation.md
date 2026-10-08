# Resilio identity-join, existing-bytes intake, delegation, and name-planes evaluation

## Bottom line

A further current-doc pass keeps strengthening the same conclusion.
Resilio Sync still deserves respect on four more operator-important lines:

- convenient linking across your own devices
- realistic intake of already-existing local bytes without unconditional re-download
- mutable folder permissions and onward-share control for Advanced folders
- flexible naming for local UI and outbound share artifacts

But the same docs also keep showing why AnonSync should not clone the exact page contracts.
The weakness is not the feature family.
The weakness is that the ordinary operator answer still tends to live inside takeover warnings, disconnect/connect ritual, rights caveat clusters, or multiple simultaneous names with unclear scope.

## What current Resilio docs still get very right

### 1) Linking your own devices is still a real convenience feature

Resilio is right that `my devices` linking is not a side trick.
For personal sync, people do want a low-friction way to make later folders appear across their own seats and to treat those seats as one practical constellation.
That instinct is still good.

### 2) Pre-existing bytes should be reusable, not treated as pollution

Resilio is also right that connecting a share to an already-populated folder is ordinary work.
The docs still plainly say equal hashes do not need re-sync, later timestamps can win when contents differ, and the rest of the tree can merge.
That is exactly the right product instinct.

### 3) Mutable delegation is useful

Resilio is right that rights are not one-time issuance forever.
Current docs still show on-the-fly permission changes for Advanced folders and keep Owner as a meaningful higher delegation class.
That is real operator value.

### 4) More than one useful name can exist at once

Resilio is also right that operators sometimes need a local display label, a different invite label, and a stable on-disk path.
Pretending those are always the same thing would be weaker than reality.

## Why this still is not a clone vote

### 1) Identity linking still carries takeover semantics too easily

The current linking docs still say that if you link two already-running instances with different certificates, one device can lose its certificate and take over the other identity; Advanced folders are removed from the app on the replaced side, and on iOS they are removed from the app and deleted from the filesystem.
A related current v3 FAQ/update cluster still says linked devices should all be updated to v3 to avoid license conflicts and that Business installations cannot be updated to v3.
That means `link device` still risks being a control-plane migration question, not merely a relationship question.

AnonSync should keep the convenience but refuse the page contract where safe join, takeover, cohort mismatch, and successor import are too easy to confuse.

### 2) Existing-bytes intake still depends on ritual and duplicate repair

Current docs still say that with linked devices in `Selective Sync` or `Synced`, arriving folders go into the default folder, same-name collisions produce an indexed duplicate, and the repair path is often `Disconnect` then `Connect` and manually choose the intended path.
The pre-populated-folder docs are candid, but the workflow still depends on remembering when to disconnect first, when `Disconnected` mode is needed, and when non-empty target confirmation is really a merge/risk question.

AnonSync should keep preseed reuse and merge honesty while refusing any contract where path continuity and byte-equivalence are reconstructed from repeated connect/disconnect ritual.

### 3) Delegation truth is still split across folder class, relationship class, and special caveats

Current docs still say:

- on-the-fly permission changes are for Advanced folders only
- Standard folders do not have Owner and need remove/re-add for permission change
- linked devices under one identity all act as Owners
- local shares cannot receive Owner
- Read Only edits suspend further sync for that peer unless `Overwrite any changed files` changes behavior

That is useful power, but the operator still has to reconstruct the rights ceiling from folder type, peer relation, and special-case behavior.

AnonSync should keep mutable delegation while refusing the contract where a disabled option or support caveat is the primary explanation of why a right cannot be granted or why a read-only seat drifted.

### 4) Name planes are still practical but under-declared

Current docs still say a custom share name can exist only in local UI, not rename the disk folder, not propagate to linked devices, and yet a different label can be inserted into a link or QR code during sharing.
That is helpful flexibility.
It is also exactly why one generic `folder name` field is too weak.

AnonSync should keep multi-plane naming while refusing the contract where local label, disk path basename, and outbound artifact alias can drift without one ordinary page declaring the scope.

## The sharper AnonSync line

The third-wave Resilio answer is now:

> borrow the convenience families, not the ordinary-page ambiguities.

More concretely:

- borrow **own-device linking convenience**
- borrow **preseed / merge / non-redownload intake**
- borrow **mutable rights and onward delegation**
- borrow **multi-plane naming where it serves real work**
- refuse any page contract where those ideas still depend on takeover warnings, reconnect ritual, caveat-cluster rights reasoning, or unlabeled name-plane drift

## Replacement-page obligations created by this pass

If AnonSync is serious about not cloning, it now owes four more ordinary pages.

### 1) Identity join

One page should answer:

- is this seat empty, populated, or already authoritative for different subjects?
- is the requested action a safe join, a reviewed successor import, or a blocked takeover risk?
- what control-plane objects would be displaced?
- what bytes survive even if local app-visible continuity changes?

That is the role of `277`.

### 2) Existing-bytes intake

One page should answer:

- what target path or existing directory is being proposed?
- are the local bytes empty, unrelated, mergeable, equivalent, or duplicate-risk material?
- what reuse proof exists already and what still requires hash/scan work?
- is the outcome attach, merge, reuse, sibling duplicate, or blocked repair?

That is the role of `278`.

### 3) Delegation

One page should answer:

- what right does this member have now?
- what stronger right is the ceiling here, and why?
- what onward-share or revoke power comes with that right?
- what happened if a read-only or narrowed seat diverged locally?

That is the role of `279`.

### 4) Name planes

One page should answer:

- what is the stable subject title?
- what is the local label here?
- what is the on-disk basename here?
- what label will a new outbound artifact or invite show?

That is the role of `280`.

## Result

This further pass makes the archive stricter in the right way.
It does not weaken the case for learning from Resilio.
It makes the case more precise.

Resilio still has very good ideas in current docs.
But those same docs still show enough takeover semantics, reconnect ritual, rights caveat memory, and naming-plane ambiguity to justify another page-contract tranche instead of cloning the interface whole.
