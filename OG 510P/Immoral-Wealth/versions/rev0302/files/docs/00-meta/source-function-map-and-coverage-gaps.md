# Source-function map and coverage-gap discipline

## What this note is for

This archive already has a strong rule for **when a source earns retained bytes** and a strong rule for **when source scratch should be compressed or dropped**.
What it still lacked was a compact way to see **which support functions the current source ledger already covers** so future revisions can tell the difference between:

- a **real evidence gap**,
- a **stale or weak anchor**,
- and mere **pile-on citation growth** inside an already-covered surface.

Without that map, source work gets noisy in two ways at once:

- real gaps can stay hidden because the ledger looks crowded, and
- already-covered surfaces can keep collecting new citations because no one can quickly see that the support function is already present.

Use this note with [`source-refresh-and-citation-compression.md`](source-refresh-and-citation-compression.md), [`archive-policy.md`](archive-policy.md), [`../../SOURCES.md`](../../SOURCES.md), and [`../../SOURCES.json`](../../SOURCES.json).

## Default rule

The archive should track source coverage at the level of **recurring support functions**, not at the level of hundreds of tiny claim tags.

That means the source ledger should say, compactly:

- which live support function a source cluster serves,
- which sources are currently the main anchors inside that function,
- and where the ledger still has a weak, indirect, or missing surface.

The goal is not a perfect ontology.
The goal is to stop the archive from confusing **many sources** with **broad coverage**.

## Function-map rule

`SOURCES.md` and `SOURCES.json` should expose a short **coverage map** for the archive's recurring evidence functions.

That map should usually stay coarse.
It should answer questions like:

- where do we go for broad wealth shares and public / private balance,
- where do we go for lower-half fragility and floor integrity,
- where do we go for housing, land, and washout,
- where do we go for tax, inheritance, and public-revenue design,
- where do we go for labor power, firm power, and market structure,
- where do we go for visibility, stewardship, and anti-capture state capacity.

If the map becomes finer than the archive's recurring decision problems, it has become a taxonomy hobby rather than a support tool.

## Gap rule

A new source should count more strongly when it fills one of these gaps.

### 1. No direct anchor for a live support function

If a live note is leaning on inference, analogy, or a distant proxy because the ledger lacks a direct anchor for that surface, that is a real gap.

### 2. Only one thin or aging anchor on a high-load surface

Some functions carry many live claims.
If one weak, indirect, stale, or fragile source is doing too much work there, a second better anchor may earn retained bytes even without expanding the archive's conceptual range.

### 3. A case-work surface cannot be routed cleanly

If a future case memo cannot quickly tell which source family should lead on a question, the ledger may have enough sources but still lack an honest coverage map.
That is a routing gap, not necessarily a source-count gap.

## Overcoverage rule

A crowded cluster is not automatically strong.
But when a support function already has:

- one strong direct anchor,
- one useful cross-check or complementary surface,
- and no live decision pressure demanding more,

new citations should usually be handled by **refresh, replacement, or better annotation**, not by minting another retained source byte.

## Primary-anchor rule

Each coverage cluster should usually have:

- one or a few clearly usable **main anchors**,
- then a small number of supporting or special-purpose sources.

The map is there to help future revisions find the **first sensible place to look**, not to equalize every source in the ledger.

## Minimal implementation rule

Keep the implementation thin.
The archive usually needs only:

1. a short note like this one,
2. one compact coverage map in `SOURCES.md`,
3. one machine-readable coverage map in `SOURCES.json`.

Do **not** solve the problem by scattering long source-function tours across many doctrine notes.

## Do-not-do list

Do not:

- micro-tag every sentence-sized claim,
- assign five functions to every source just because it is broad,
- treat a source map as a substitute for source precedence in real cases,
- or let the map grow into a second archive parallel to the actual notes.

If a source can plausibly fit two functions, that is fine.
But the coverage map should still help the archive decide **where that source mainly belongs first**.

## Fast use rule

Use this note whenever a revision asks:

- does this proposed source fill a real gap or just thicken a covered surface,
- should the ledger gain a new source ID or just a refreshed anchor,
- does the archive need a new source or only a clearer source route,
- or does a case memo keep stumbling because the ledger's support functions are not exposed compactly enough.

## Bottom line

A tight source ledger should not only be **small**.
It should also make clear **what work each source cluster is there to do**.

The standing bias is:
**map support functions coarsely, add sources only when they fill a real gap or materially strengthen a weak anchor, and prefer route clarity over citation pile-on.**
