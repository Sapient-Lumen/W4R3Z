
# Resilio birth commitments, create-time freezes, and recreate-boundary evaluation

## Why this seam matters

The archive already has strong doctrine for **policy provenance**, **activation latency**, **subject-kind migration**, **identity adoption**, and **typed removal**.
What it still lacked was one direct evaluation for a quieter but equally important operator question:

> when the product says `edit settings`, which settings are actually live-editable, which are birth-time commitments, and when is the honest answer really `create a successor and cut over`?

Current official Resilio docs make this seam sharper than a generic `some settings need restart` warning.
Across the current Sync and Active Everywhere documentation they still say all of the following:

- some major capability differences are still fixed at creation or re-add time rather than live mutation time
- current Sync help still says Standard folders cannot be converted into Advanced folders in place and that on-the-fly permission changes are not possible for Standard folders, so the share must be removed and re-added with a new key
- current Active Everywhere docs still say permission-synchronization settings for Synchronization, Hybrid Work, and File Caching jobs are applied when the job is created and cannot be changed later
- current Linux cache-server docs still say the selected file-access path and cache path cannot be changed later after the job is saved
- that same cache-server guidance still says those paths must exist with stricter preconditions, including the exposed access path being empty
- current migration docs still publish a real successor workflow for moving Sync jobs into File cache or Hybrid work jobs, including deleting the old job from the Management Console, creating a new one, and transplanting database files to preserve continuity
- current cache/gateway restart docs still say changing the mount point remounts it, triggers initial indexing, resets counters, and only then reuses cached bytes as a pre-seeded scenario

That is useful candor.
It is also a good reason not to clone the page contract.

## What Resilio gets right

### 1) It admits that `editable later` is not one universal truth

Current docs do not pretend all settings live on one mutability plane.
Some are ordinary live edits.
Some are next-run edits.
Some are restart-gated.
Some are explicitly fixed at job creation.
Some require remove/re-add or full migration.

### 2) It admits that birth-time choices change what the product is allowed to promise later

Standard-versus-Advanced in Sync is not a cosmetic mode switch.
Neither is permission-sync mode in Active Everywhere.
Neither are cache access paths.
Those choices alter future authority, topology, substrate, and repair cost.

### 3) It admits that `migration` is different from `editing`

The migration guidance is especially valuable because it is explicit that some changes are not mere updates.
The operator is really creating a successor object and carrying continuity across it.

## Why AnonSync still should not clone it

One ordinary operator question is still fragmented:

> can I safely change this in place, or is this a birth-time commitment whose honest path is recreate / reissue / successor cutover?

In current Resilio, that answer can still depend on hopping across:

- Standard-vs-Advanced folder docs
- sync-functionality overview prose
- profiles tables
- permission-sync guidance
- cache-server setup warnings
- migration guides

That is too much archaeology for a question that changes operator risk so directly.

## Hard decisions for AnonSync

1. **Every consequential field gets a mutability class.** The product must say whether the field is `live-editable`, `next-run`, `restart-gated`, `future-only`, `birth-locked`, or `successor-required`.
2. **Birth-time commitments are first-class.** Empty-target requirements, topology commitments, authority substrate, and exposed access roots must be reviewable before creation.
3. **Edit and recreate are different verbs.** The product must never hide successor cutover inside ordinary edit language.
4. **Recreate cost belongs in the review.** Re-index, path emptiness, cached-byte reuse, blast radius, and receipt carryforward must appear before apply.
5. **Receipts preserve the stronger rejected sentence.** If the honest answer was `cannot be changed in place`, the receipt must keep that truth visible.

## Interface family implied by this evaluation

This pass therefore adds five more page-shaped obligations:

1. **Mutability contract sheet**
2. **Birth-commitment review**
3. **Post-create change preview**
4. **Recreate-boundary page**
5. **Mutability lineage receipt**

## Bottom line

The tighter no-clone reason is now this:

> current Resilio docs are good evidence that some important choices really are birth-time commitments and some later changes honestly require successor creation or migration; they are also good evidence that the ordinary operator answer about `can I change this later or not?` still leaks across several documents instead of one stable product-owned contract.
