# Resilio indirection-object platform split and target non-transitivity evaluation

## Why this seam matters now

Earlier archive work already noticed unsupported links and filesystem-shape risk.
This revision promotes that hint into its own family because current official Resilio docs are still unusually candid about a deeper truth:

> a path row that looks like an ordinary file or folder can actually be an indirection object, and the contract differs by platform family, by entry class, and by whether you mean the object itself or the bytes behind its target.

That is exactly the kind of seam AnonSync must own directly rather than inherit as folklore.

## Current official Resilio candor

Current official Resilio docs still say:

- on Windows, Sync does not support soft links, junctions, hard links, or symbolic links
- use of those entries may lead to `.Conflict` files for each affected file or folder
- on Unix, symbolic links may be synchronized as links
- but the target folders referenced by those links are not synchronized unless added separately
- conflict guidance still names linked junctions as a concrete cause of `.Conflict` artifacts
- the active Sync v3 line is still visible through `3.1.2.1076`

That is strong candor.
Resilio is not pretending these edge classes do not exist.

## Why not clone the contract

The non-clone problem is not honesty.
The non-clone problem is that one ordinary operator answer still has to be reconstructed from more than one place:

- what class of entry was actually found
- whether this seat preserves the object or rejects it
- whether the target bytes are already in scope
- whether following the target would widen the graph
- whether the likely outcome is preservation, flattening, block, or `.Conflict` residue

A serious sync product should not make operators infer that by stitching together a link article and a conflict article.

## Product lesson for AnonSync

AnonSync should treat these as first-class **indirection objects**, not merely as odd path names.
Every indirection object should expose two separate truths at once:

1. **entry-object truth** — what happens to the link/junction object itself on this seat family
2. **target-transitivity truth** — whether the bytes behind the target are already included, explicitly excluded, or require a separate admission act

These truths should never collapse into one vague sentence like `supported`, `unsupported`, or `syncs as link`.

## Required replacement pages

This revision therefore adds four page families:

- `697` **Indirection posture**
- `698` **Indirection action review**
- `699` **Target transitivity proof**
- `700` **Indirection receipt**

## Tightened design rule

> if a row is actually an indirection object, the product must separately publish object fate and target scope before any preservation, flattening, follow-target, or repair action can be described as safe.

## Non-clone conclusion

Keep the Resilio candor.
Refuse the page contract.
A path row should not look ordinary while its object fate, target scope, and conflict hazard are still support-article knowledge.
