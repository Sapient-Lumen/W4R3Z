# Canonical anchors and bridge-note discipline

## What this note is for

This archive now has enough compact bridge and operator notes that a new reader could too easily ask the wrong question:
not **what does the archive think?** but **which nearby note is the real one?**

That is a routing problem, not a theory problem.
The archive therefore needs one compact rule for deciding:

- which note in a cluster is the **canonical anchor**,
- when a smaller note earns life as a **bridge** rather than an anchor rewrite,
- how front-door routes should point through that cluster,
- and when bridge growth should trigger merge, fold-back, or route trimming.

Use this note with [`archive-policy.md`](archive-policy.md), [`archive-growth-budgets-and-refactor-triggers.md`](archive-growth-budgets-and-refactor-triggers.md), [`research-triage-and-closure-rules.md`](research-triage-and-closure-rules.md), [`note-status-and-supersession-discipline.md`](note-status-and-supersession-discipline.md), [`term-discipline-and-synonym-control.md`](term-discipline-and-synonym-control.md), [`case-to-doctrine-promotion-and-quarantine.md`](case-to-doctrine-promotion-and-quarantine.md), and [`../../START_HERE.md`](../../START_HERE.md).

## Default rule

For any recurring decision point, the archive should usually have:

1. **one canonical anchor** that states the main judgment rule,
2. **zero or a few compact bridges** that solve repeated routing or operator gaps,
3. and **one short canonical path** that tells readers what to read first and what only to read if needed.

The archive should not make readers infer authority from file length, recency, or accidental proximity.
It should make the authority structure explicit.

## What counts as an anchor

A note should count as the **canonical anchor** for a cluster when it does most of the following:

- states the main minimum rule,
- carries the repeated-use distinction that later files depend on,
- can still orient a reader even if nearby bridges are not read,
- survives beyond one narrow workflow,
- and is the note most future revisions would tighten first before adding more satellites.

An anchor is not merely the longest note.
It is the note that would still have to exist if the cluster were compressed tomorrow.

## What counts as a bridge

A note should count as a **bridge** only when it does one narrow job that the anchor should not keep re-explaining.
Usually that means one of four things:

### 1. Decision-order bridge

It tells a reader in what order to apply several already-live rules.

### 2. Tie-break bridge

It tells a reader how to choose among several plausible paths that remain after the anchor has already done its work.

### 3. Watch / reroute bridge

It tells a reader what to do after a package, verdict, or softer reading is already in motion.

### 4. Archive-governance bridge

It compresses repeated archive-maintenance choices such as source refresh, route trimming, byte budgets, or note closure.

If a note cannot be described that narrowly, it is often trying to become a second anchor and should usually be folded back into the main anchor instead.

## What every bridge should make explicit

A bridge note should say, briefly:

- its **parent anchor**,
- the **upstream question** that should already be settled before using it,
- the **downstream decision** it helps finish,
- and what it is **not** trying to restate.

That declaration matters because a bridge earns its bytes by cutting rereading, not by becoming a second place where the whole doctrine lives.

## Canonical-path rule

Each live cluster should have one short reading path of the form:

**anchor first -> bridge if needed -> next decision note**

Not:

**anchor -> neighboring note -> nearby note -> companion note -> another plausible note just in case**

A path is canonical when it lets a reader finish the decision with the fewest notes that still preserve judgment quality.

## Front-door routing rule

`START_HERE.md`, `README.md`, and other top-level routes should normally point to:

- the **anchor** for a question,
- the one bridge that most often follows it,
- and only then a deeper index if a reader wants the whole neighborhood.

Top-level routes should not try to prove completeness by naming every nearby satellite.
Completeness belongs in `ARCHIVE_INDEX.md`, not in the front door.

## When bridge growth becomes a problem

Treat these as refactor triggers.

### 1. Three-bridge trigger

If one anchor has three or more active bridges around the same decision point, ask whether one bridge should be folded back, merged with another, or replaced by a single canonical path note.

### 2. Sideways-reading trigger

If readers must move sideways across several nearby notes before they can act, the cluster is under-routed.
Either add one path note or trim the satellites.

### 3. Repeated-setup trigger

If several bridges keep restating the same setup, minimum rule, or caveat, the anchor is probably under-tightened or the bridges are overreaching.

### 4. Front-door spillover trigger

If `START_HERE.md` or `README.md` keeps growing because a cluster has too many legitimate satellites, compress the route around the cluster rather than letting the front door become a shadow index.

## How to decide between tightening and adding

Before adding a bridge, ask:

1. **Could the anchor absorb this in one short section without becoming harder to use?**
2. **Would a new bridge cut repeated rereading across many future revisions or cases?**
3. **Can the new bridge name one clear parent anchor and one clear next note?**
4. **After adding it, can some route or repeated explanation get shorter?**

If the answer to the first question is yes and the others are weak, tighten the anchor.
If the answer to the second through fourth is yes, a bridge may earn its place.

## Supersession and fold-back rule

A bridge should not become immortal just because it once solved a real gap. Its wording should also stay subordinate to the anchor's preferred terminology rather than spinning up a rival vocabulary; use [`term-discipline-and-synonym-control.md`](term-discipline-and-synonym-control.md) when bridge language starts to drift.
Fold it back, merge it, or demote it when:

- the parent anchor now states the rule cleanly enough on its own,
- the bridge is mostly routing prose rather than judgment,
- the cluster can now be read faster without it,
- or later bridges made its distinction redundant.

The archive should preserve durable judgment, not the history of every routing fix. When a bridge is no longer live, use [`note-status-and-supersession-discipline.md`](note-status-and-supersession-discipline.md) to decide whether it should remain as support, shrink into a redirect, or disappear from active routing.

## Fast use rule

When a reader or reviser encounters a cluster of nearby notes:

1. **name the decision point,**
2. **identify the canonical anchor,**
3. **read that first,**
4. **use only the bridge that finishes the immediate next decision,**
5. **trim or merge when bridges start forcing sideways rereading.**

## Bottom line

The archive should have one obvious place where a question mainly lives, and only a few clearly subordinate places where repeated operator gaps are solved.

The standing bias is:
**one anchor per recurring decision point, bridges only when they cut repeated rereading, and route trimming whenever satellites start to behave like a second archive.**
