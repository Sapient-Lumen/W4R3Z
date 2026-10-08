# Cross-root rehome, move, and missing-path repair interface spec

## Purpose

The archive already has reconnect/repair, target preflight, state-root doctrine, and path reconciliation.
What it still lacked was one explicit interface contract for **moving a live bind across filesystem roots or recovering from path disappearance without folklore**:

> when a synced subject is renamed, moved, remounted, or lost, what page tells the operator whether this is a same-root rename, a true rehome across roots, a missing-path recovery, or a bind that can no longer honestly claim continuity?

Current Resilio docs keep this seam concrete.
Move/rename support still has root/platform limits, cross-partition moves can still fall back to disconnect/reconnect, Linux still distinguishes moving files inside the parent from moving the share itself, and `Folder not found` remains a recognizable recovery state.
AnonSync should expose that as one reviewed rehome grammar instead of several troubleshooting rituals.

## Core decision

Every non-trivial bind move must pass through a **rehome review**.
The review classifies the path event before any continuity claim is made.

The operator should never have to guess whether the product means:

- same bind, same root, new name
- same bind, new root, continuity preserved
- bind went missing and needs repair
- bind cannot keep continuity under the proposed move

## Classification classes

The rehome preflight must classify at least these cases:

1. **Rename only** — same root, same watch world, path label changed
2. **Same-root move** — bind stays in the same continuity world
3. **Cross-root rehome** — target root/substrate differs and requires reviewed continuity
4. **Missing-path recovery** — current bind target disappeared or no longer resolves
5. **Blocked move** — proposal would cross into a path world that cannot preserve the current bind honestly

## The fixed review order

Every rehome or missing-path case should render sections in this order:

1. **Current bind and requested location**
2. **Filesystem-root and watch-world delta**
3. **Continuity evidence**
4. **Admissible repair or rehome actions**
5. **Consequences for peers, derivatives, and receipts**
6. **Receipt promise**

## 1) Current bind and requested location

Show:

- subject label and handle
- current bound path
- requested new path or missing-path observation
- acting seat and runtime profile
- whether the trigger is rename, move, mount change, disappearance, or manual rehome request

The operator should immediately be able to answer:

> what path are we leaving, what path are we aiming at, and why are we here?

## 2) Filesystem-root and watch-world delta

This section should classify:

- same root vs new root
- same notification substrate vs degraded/new watch world
- same namespace visibility vs changed mount/permission world
- same path semantics vs changed support tier

Good status labels include:

- `same-root, continuity strong`
- `cross-root, reviewed rehome required`
- `target visible but watch quality degraded`
- `missing path, source evidence intact`
- `path world incompatible with current bind`

A rehome is not only about a string path.
It is also about the local world that makes the bind truthful.

## 3) Continuity evidence

Show the evidence that continuity can or cannot be preserved:

- lineage markers
- last-known custody records
- same-byte overlap / compare signals
- state-root continuity
- watch-world equivalence or degradation
- source/child lineage dependencies

This prevents a tempting but false equation of `looks like the same folder` with `is the same trustworthy bind`.

## 4) Admissible repair or rehome actions

The primary next actions should be explicit:

- `Accept rename in place`
- `Rehome with preserved continuity`
- `Repair missing path to reviewed target`
- `Open compare-before-rebind`
- `Detach and preserve locally`
- `Blocked until seat/root issue is fixed`

The product should not suggest `disconnect and reconnect` as a semantic answer when the real question is continuity classification.

## 5) Consequences for peers, derivatives, and receipts

Show fallout on:

- currently visible peers and their expectations
- same-machine children bound to the source path
- publication / future-arrival defaults that reference the old path root
- preservation and retained-copy receipts
- any currently draining or narrowing route/path cleanup work

A path move is never purely local if other continuity-bearing objects still point at the old bind.

## 6) Receipt promise

The resulting receipt must prove:

- classification class
- old path and new path
- whether continuity was preserved, guarded, or refused
- watch-world/support-tier changes
- dependent subjects or follow-up repairs created

That receipt should later answer:

> was this a simple rename, a reviewed rehome, or a break followed by repair?

## What must never happen automatically

The product must never automatically:

- treat cross-root rehome as though it were a harmless rename
- claim path continuity when the watch world degraded materially without saying so
- present a missing-path situation as `folder not found` without the best supported repair shape
- create duplicate target paths to dodge the real continuity question

## Why this is worth the trouble

Path movement is where sync tools often slide back into filesystem folklore.
AnonSync can do better by making rehome and missing-path repair read as continuity decisions with proofs, not as a trail of support advice after a path error.
