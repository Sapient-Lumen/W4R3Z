---
status: active_bridge
claim_kind: archive_governance
route_role: archive_governance_core
canonical_anchor: false
route_refs:
- archive_governance_core
supersedes: null
depends_on: []
source_refresh_due: '2026-12-31'
case_pressure: rev0304_portfolio_calibration
---

# Term discipline and synonym control

## What this note is for

This archive now has rules for **which questions deserve bytes**, **how large notes should get**, **which note is canonical**, and **when older notes stop being live doctrine**.
What it still needs is one compact rule for **which recurring terms should stay fixed**, **when a new phrase is only an alias rather than a new concept**, and **how to prevent vocabulary drift from becoming hidden archive sprawl**.

Use this note with [`archive-policy.md`](archive-policy.md), [`archive-growth-budgets-and-refactor-triggers.md`](archive-growth-budgets-and-refactor-triggers.md), [`canonical-anchors-and-bridge-note-discipline.md`](canonical-anchors-and-bridge-note-discipline.md), [`note-status-and-supersession-discipline.md`](note-status-and-supersession-discipline.md), and [`preferred-terms-and-alias-map.md`](preferred-terms-and-alias-map.md).

## Default rule

A recurring decision point should usually have **one preferred archive term**.
New wording does not earn new conceptual status merely because it sounds fresher, more elegant, or more rhetorical.
If two phrases point to the same operator step, moral screen, or governance function, the archive should usually keep one as canonical and treat the others as aliases or not use them at all.

The archive's danger is not only duplicated notes.
It is also duplicated concepts hiding under slightly different names.

## What term discipline is trying to prevent

Without term discipline, the archive slowly grows:

- several names for the same decision,
- several slightly different route labels for the same workflow,
- bridge notes that look new only because their wording drifted,
- and front-door summaries that become harder to scan because every revision renames yesterday's live concept.

That kind of drift widens the archive even when file count stays flat.

## Canonical-term rule

For any recurring concept, prefer one term that is:

1. **short enough to route with,**
2. **specific enough not to blur into nearby concepts,**
3. **stable enough to survive several revisions,**
4. **ordinary enough to remain readable,**
5. and **already anchored in one clear parent note** when possible.

Once a term meets those tests, later revisions should normally reuse it rather than mint a stylish near-synonym.

## Alias rule

A new phrase should usually be treated as an **alias only**, not as a fresh archive concept, when it does one of these:

- restates an existing term in more rhetorical language,
- changes emphasis without changing the decision,
- shortens or lengthens the wording without adding a real new distinction,
- or imports outside vocabulary for a concept the archive already names well enough.

When an alias is kept at all, it should usually appear only once near the canonical term and then disappear.
The archive should not maintain several active phrasings for the same judgment unless the distinction is real and repeatedly useful.

## When a new term really earns life

A new term usually earns separate life only if it changes at least one of these:

1. **the decision being made,**
2. **the order of operations,**
3. **the proof burden,**
4. **the route through the archive,**
5. or **the boundary between two concepts that readers were repeatedly confusing.**

If none of those changes, prefer reuse over invention.

## Preferred-term maintenance rule

When a concept becomes recurrent, the archive should keep one preferred term in the note where that concept mainly lives.
That anchor should usually be the place future revisions tighten first when wording starts to drift.
For the archive's short reusable list of already-stabilized recurring terms, use [`preferred-terms-and-alias-map.md`](preferred-terms-and-alias-map.md).

A bridge note may reuse the preferred term.
It should not quietly rename it unless the renaming is part of the bridge's actual job.

## Typical archive examples

These are examples of the kind of discipline this note is trying to preserve:

- keep **dominant breach** rather than cycling among main failure, lead breach, primary break, or chief constitutional defect;
- keep **fastest washout** rather than drifting among rebound channel, reabsorption path, or quickest loss lane;
- keep **opening package** rather than alternating among starter package, first bundle, initial platform, or early move set;
- keep **proof debt** and **evidence debt** distinct rather than letting them collapse into one vague uncertainty bucket;
- keep **canonical anchor** and **active bridge** stable rather than restyling them every few revisions;
- keep **watch posture**, **durability window**, and **reopening trigger** distinct rather than letting all post-launch review language blur together.

The point is not verbal purity.
It is keeping repeated case work and revision work from rediscovering the same concepts under new labels.

## Refactor trigger for vocabulary drift

Treat these as standing triggers:

### 1. Synonym-cluster trigger

If one concept is being named three or more ways across routes, summaries, or nearby notes, pick one preferred term and trim the rest.

### 2. False-newness trigger

If a proposed note or section sounds new mainly because it introduces a different phrase for an existing operator step, the default answer should usually be to edit the current note, not add bytes.

### 3. Route-scan trigger

If front-door route labels are getting longer because each line has to explain several near-synonyms, the archive's vocabulary has become too loose.
Tighten the terms before tightening the route text.

### 4. Case-memo trigger

If future case memos start inventing local labels for archive-standard steps, fold them back to the canonical term instead of letting case language seed doctrine drift.

## Fast use rule

When revising a note or naming a new one:

1. **ask whether the concept already exists under another name,**
2. **find the anchor where the concept mainly lives,**
3. **reuse the preferred term unless a real distinction is missing,**
4. **treat new wording as an alias unless it changes the decision, proof burden, or route,**
5. **trim stray synonyms from front-door routes and bridge notes,**
6. and **only then decide whether any new bytes are still justified.**

## Bottom line

The archive should not let naming drift become hidden sprawl.

The standing bias is:
**one preferred term per recurring concept, aliases only when briefly useful, and new wording only when it changes a real decision or prevents repeated confusion.**
