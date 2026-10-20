# ADR 0338: Preserve bounded exchanged-projection descriptor writes

- Status: accepted and implemented; production descriptor/remount qualification pending
- Date: 2026-09-08

## Context

Tree-v2 replaces a writable projection by materializing a verified target in a
same-parent private directory and invoking Linux `RENAME_EXCHANGE`. Before the
exchange it scanned the visible tree a second time, so a pathname mutation
observed before that scan could be published instead of overwritten.

That was not sufficient for an ordinary Unix writer which opened a file before
the scan and wrote it after the scan. The exchange moves the old directory to
the private staging pathname. The old implementation validated only the newly
visible tree and then removed staging, so a held descriptor could write the
now-staged inode after the final scan and have its edit silently deleted.

Two related complications matter:

* sparse/recipient-local projection rules deliberately leave unselected paths
  outside the signed manifest, so selected-manifest scanning cannot notice a
  changed excluded path; and
* a projection-policy change legitimately changes which paths are selected.
  Treating any marker mismatch as a policy transition would let a missing,
  corrupt, or unrelated marker hide a selected deletion.

## Decision

1. Immediately after `RENAME_EXCHANGE`, validate the newly visible target and
   the obsolete staged tree before staging removal. The obsolete tree is
   scanned against the exact prior signed manifest. A change returns
   `protocol_error`, keeps both trees and the signed pending workspace, and
   requires an explicit forward recovery; it is never silently discarded.
2. Compare preserved unselected paths in both directions. The comparison
   covers relative path, file type, owner mode, byte size, and regular-file
   digest; it also restores unselected directory modes while constructing the
   replacement. Thus an excluded-path mutation made through a held descriptor
   is retained rather than being masked by selected-manifest equality.
3. An established worktree must carry either the canonical current projection
   marker, or a canonical *prior* policy marker bound to the authenticated
   active manifest in the signed workspace. Missing, malformed, unrelated, or
   markerless established trees fail before staging or exchange. The prior
   policy is used only for the exact policy-transition delta: a missing path
   is preserved only when it was unselected under that authenticated prior
   policy and selected under the current one.
4. Recovery applies the same old-stage and marker checks before deleting a
   staged projection. An old tree with a local edit stays present until the
   operator/publisher merges it through an ordinary forward transition.
5. Direct tests use test-only seams immediately before `RENAME_EXCHANGE` and
   immediately after it but before either side is validated. They write
   through a descriptor held from before the scan and cover selected,
   excluded, and post-exchange selected paths; retention through recovery;
   selected deletion under marker mismatch; missing-marker refusal before
   effect; and canonical sparse-policy widening.

## Consequences

The direct silent-loss windows between the final pre-exchange scan and the
immediate post-exchange old-tree validation are closed in deterministic
construction tests for ordinary writes observed by that validation. This is a
refusal-and-preservation guarantee, not a
promise that a local edit automatically becomes published or that it is safe
to remove the retained stage manually.

The boundary is deliberately bounded. A writer can still mutate the old inode
after final obsolete-tree validation begins and before or during staging
removal. Writable memory mappings, hostile same-UID writers which manipulate
the projection marker, remount/restart behavior with open descriptors, and a
first-ever recovery of an old markerless projection are not covered. The
markerless case fails closed because the product has no durable proof that a
marker was never established.

ADR 0340 is the next gate: a source-linked Sandwurm/ext4 campaign must hold
real file descriptors across the exchange, force a post-exchange write before
validation, retain the old inode across controlled stop and remount, and prove
cold startup refuses rather than deleting it. That qualification is not
inferred from these deterministic seams.
