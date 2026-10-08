# Resilio subject-spine, sidecars, and hidden-authority evaluation

## What current official docs still make clear

Another current Resilio pass again strengthens the main archive conclusion rather than weakening it.

Current official docs still show real product substance:

- a live v3 line with `3.1.2.1076`
- explicit admission that every synced folder gets a hidden `.sync` directory and that this directory is critical for syncing
- explicit admission that `.sync` contains several different managed families at once: folder identity, IgnoreList, StreamsList, Archive, and in-flight `.!sync` names
- explicit admission that IgnoreList is a UTF-8 text sidecar, that ignored files are not indexed and not counted in the visible size column, that matching is case-sensitive, and that peers may differ even if that later causes operator confusion
- explicit admission in troubleshooting guidance that ignore disagreement can itself explain sync divergence and that peers effectively need to agree on what should be skipped
- explicit admission that StreamsList is a separate whitelist sidecar for xattrs / alternate streams, that xattrs cannot be ignored through IgnoreList, and that when a filesystem cannot store xattrs properly Sync creates stub material in `.sync/Streams`
- explicit admission that `Service files missing` suspends synchronization for the subject and can come from deleting/corrupting `.sync` or from two Sync instances touching the same subject on one machine or external drive
- explicit admission that one documented repair path is effectively `export what matters, delete .sync, remove/re-add the share`, which recreates a fresh subject instance rather than magically proving preserved continuity
- explicit admission that moving the subject itself is platform-constrained and can break continuity if done across the wrong boundary
- explicit admission that cloning an entire Sync instance by disk copy / Time Machine / cloner is unsupported and can produce multiple strange, non-converging instances

That is not fake candor.
It is very useful operator truth.

## What still should not be cloned

The ordinary operator answer is still fragmented.
Current docs still require cross-reading at least seven places to answer four basic questions:

1. **What inside this folder is really payload, and what is product-owned hidden state?**
2. **Which hidden sidecars are local policy, which are continuity-bearing, and which affect only metadata carriage?**
3. **If hidden state is damaged or duplicated, did continuity survive or am I really creating a new subject epoch?**
4. **Which hidden byte families are safe to inspect, safe to clear, unsafe to edit, or only safe to touch through reviewed product actions?**

Resilio still has strong ideas here.
It still does **not** earn direct interface cloning.

The reason is the same clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary hidden-state answer across FAQ prose, IgnoreList docs, xattr docs, service-file warnings, troubleshooting notes, move/rename caveats, and cloning warnings.
So the product idea stays strong while the page contract still fails.

## Why this matters for AnonSync

AnonSync should borrow four important habits directly:

- **say openly that a sync subject has product-owned state as well as payload bytes**
- **say openly that sidecars can differ in meaning: continuity, local policy, metadata carriage, history, or in-flight residue**
- **say openly when damage forces a recreated subject epoch rather than preserved continuity**
- **say openly which hidden byte families are safe to browse but not safe to mutate by hand**

But AnonSync should refuse four weaker habits:

- learning the subject's managed namespace primarily by looking inside hidden folders
- treating local sidecar text as the main semantic home of exclusion or xattr policy
- burying preserved-versus-recreated continuity behind repair folklore
- requiring raw filesystem spelunking to understand archive, stream stubs, or stuck partials

## Replacement pages added for this seam

This revision therefore adds four narrower replacement pages:

- `417` — Subject spine
- `418` — Sidecar policy
- `419` — Spine integrity
- `420` — Managed hidden bytes

These pages keep the Resilio candor and reject the hidden-folder reconstruction path.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that sync subjects really do carry hidden service state, local policy sidecars, xattr-carriage sidecars, and continuity-bearing identifiers; refuse any interface contract where `what is product-owned here`, `what sidecar controls this`, `did continuity survive`, and `what hidden bytes are safe to touch` still depends on filesystem archaeology across FAQs, troubleshooting articles, and repair notes.
