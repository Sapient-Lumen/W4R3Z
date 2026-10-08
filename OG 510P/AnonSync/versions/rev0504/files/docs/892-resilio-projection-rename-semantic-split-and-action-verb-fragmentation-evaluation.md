# Resilio projection rename semantic split and action-verb fragmentation evaluation

## Why this pass exists

The archive already had broad naming-plane doctrine, local-vs-issued-label doctrine, and one ordinary provenance sheet.
What it still lacked was a narrower pass about a sharper current Resilio seam:

> when an operator presses something that looks like `rename`, what exact plane is that verb actually mutating on this projection?

Current official Resilio docs are now especially useful here because they still show that the answer depends on where the operator is standing:

- desktop `Setting custom name for sync shares` still says a custom share name can be changed in Sync UI only, does not rename the folder on disk, and does not propagate to other peers or linked devices.
- the same desktop article still says the outward label inserted into a link or QR can be changed again while the underlying share name remains unchanged.
- `Can I move or rename a syncing folder?` still says filesystem rename affects only the local device and does not update other devices.
- `Sync interface on Android` still says the share-name pencil renames the subject both in Sync and in the filesystem.
- `Sync Interface on iOS devices` still says the share-name pencil lets you rename the share, but leaves the exact plane effect less explicit than Android.

That is strong candor.
It is also a strong reason not to clone the exact verb contract.

## What current Resilio still gets right

### 1) Different projections can reveal real different mutation powers

Resilio is right not to pretend every surface has the same powers.
A mobile share detail surface may have different available storage/path semantics from a desktop preference sheet.
A product should not flatten that away.

### 2) Local rename, canonical retitle, and outward relabel are genuinely different verbs

Current docs still prove that these are not the same mutation:

- local filesystem rename
- local UI alias change
- outward artifact label insertion
- platform-specific share rename action

That distinction is useful and AnonSync should keep it.

### 3) Projection differences deserve explicit ownership

The useful lesson in Resilio is not `make everything identical`.
The useful lesson is that projections really can differ.
The failure is leaving the operator to discover that only after the click.

## Why AnonSync still should not clone it

### 1) Same-looking affordance can still mean different plane edits

A desktop custom-name edit is UI-only and non-propagating.
An Android rename pencil says it changes Sync and the filesystem.
A filesystem rename in Finder/Explorer is local-only.
An issuance-time label edit mutates only the outgoing artifact.

Those are four materially different verbs that can all look like `rename`.
AnonSync should not make operators memorize projection trivia to know which one they are invoking.

### 2) The plane truth still leaks across tips, FAQs, and platform pages

Current Resilio still requires the operator to remember:

- a desktop tip article for UI-only rename
- a filesystem FAQ for local path rename
- a mobile share-details article for Android rename semantics
- separate sharing notes for recipient-facing artifact labels

The distinctions are real.
The page ownership is the problem.

### 3) Cross-projection predictability is still too weak

A serious action verb should stay semantically predictable even when capabilities differ by platform.
If one projection can only rename a local alias while another renames a real folder path, the product must say so before the act and in the receipt after the act.
Resilio's current docs still make that too easy to learn late.

### 4) Later operators need verb receipts, not memory of which client was used

Once the same ordinary-looking action can hit different planes on different projections, later operators need durable receipts that say:

- which projection executed the action
- which exact planes changed
- which obviously adjacent planes did not change
- what audience actually experienced the change

Anything less becomes click-history folklore.

## Hard decisions now locked for AnonSync

1. **Action verbs are first-class contracts, not button labels.** `Rename` must expand to a typed verb family before apply.
2. **Projection may narrow capability, but may not silently change semantics.** If a projection only supports one plane, it must say so before the action reads as generic rename.
3. **Cross-projection actions always preview affected and untouched planes.** A later operator should not need to know whether Android, desktop, or web initiated the change to interpret it.
4. **Issued artifact relabeling is never hidden under generic rename.** Artifact-label edits stay visibly separate from subject or path rename.
5. **Receipts preserve projection witness and plane delta.** History must say both what changed and which projection's contract was used.
6. **Ambiguous pencils are not acceptable.** When one icon could plausibly mean local alias, path rename, canonical retitle, or artifact relabel, the interface must disambiguate before apply.

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Action verb contract sheet**
- **Rename intent disambiguation**
- **Projection semantic gap review**
- **Cross-projection rename preview**
- **Action lineage receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right that different projections can expose different rename powers. But it still lets one ordinary-looking `rename` answer depend on whether the operator is standing in desktop UI alias controls, filesystem rename, Android share details, or issuance-time share labeling. AnonSync should keep the candor and refuse the projection-dependent verb folklore.
