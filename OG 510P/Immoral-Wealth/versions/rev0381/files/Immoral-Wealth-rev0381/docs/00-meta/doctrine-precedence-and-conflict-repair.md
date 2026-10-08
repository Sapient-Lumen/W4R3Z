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

# Doctrine precedence and conflict repair

## What this note is for

The archive now has rules for **which note is canonical**, **which notes are still live**, and **which terms should stay fixed**.
What it still needs is one compact rule for the next problem that appears once an archive becomes dense:
**what to do when two live notes seem to say different things, point to different routes, or imply different burdens of proof.**

Without that rule, later revisions can accidentally create a fake choice between notes when the archive really intends to speak with one voice.
This note therefore governs **live-doctrine precedence and contradiction repair**, not source conflict and not substantive case evidence.
For case-source disagreement, use [`../20-program/source-order-and-conflict-resolution.md`](../20-program/source-order-and-conflict-resolution.md).

Use this note with [`canonical-anchors-and-bridge-note-discipline.md`](canonical-anchors-and-bridge-note-discipline.md), [`note-status-and-supersession-discipline.md`](note-status-and-supersession-discipline.md), [`term-discipline-and-synonym-control.md`](term-discipline-and-synonym-control.md), [`claim-kinds-and-revision-burdens.md`](claim-kinds-and-revision-burdens.md), [`archive-growth-budgets-and-refactor-triggers.md`](archive-growth-budgets-and-refactor-triggers.md), [`doctrine-revision-and-demotion-under-case-pressure.md`](doctrine-revision-and-demotion-under-case-pressure.md), and [`archive-policy.md`](archive-policy.md).

## Default rule

When two archive notes appear to disagree, the archive should usually do **six things in order**:

1. **decide whether the difference is real or only verbal,**
2. **check whether the notes are even carrying the same kind of claim,**
3. **check note status first,**
4. **let the canonical anchor beat a bridge on the same question,**
5. **repair cross-note tension quickly rather than leaving two live answers in circulation,**
6. **and record the repair in the revision receipt or changelog rather than letting readers infer precedence from guesswork.**

The archive should not make readers choose doctrine by file date, file length, or rhetorical force.
It should make precedence explicit and keep unresolved tension rare, visible, and temporary.

## The three ordinary kinds of apparent conflict

### 1. Verbal drift, not real disagreement

Sometimes two notes sound different only because one uses looser language, a shorter summary, an alias the archive should suppress, or a different claim kind that should not be treated as same-level doctrine.
That should usually be handled as a **term cleanup**, not as two doctrines.
Use [`term-discipline-and-synonym-control.md`](term-discipline-and-synonym-control.md) and [`preferred-terms-and-alias-map.md`](preferred-terms-and-alias-map.md).

### 2. Local bridge overreach

Sometimes a bridge note starts sounding broader than its parent anchor and seems to imply a larger rule than it was meant to carry.
That is usually a **bridge-boundary failure**.
The repair is normally to tighten the bridge or fold the stray rule back into the anchor, not to leave two live answers standing.

### 3. Real cross-note tension

Sometimes two genuinely live notes do point toward different judgments, routes, or burdens of proof.
That is the serious case.
When it happens, the archive should repair it directly.
A dense archive may tolerate temporary tension during drafting.
It should not package that tension as if it were normal background texture.

## Precedence order

When real or apparent conflict appears, use this order.

### 1. Note status comes before recency

A **live doctrine** note outranks a superseded stub, redirect, or merely historical support note even if the older file is more familiar or the newer file is more elegant.
Do not treat recency alone as authority.
First ask whether both notes are actually live.
Use [`note-status-and-supersession-discipline.md`](note-status-and-supersession-discipline.md).

### 2. Canonical anchor comes before bridge on the same question

If both notes are live and they speak to the **same recurring decision point**, the cluster's **canonical anchor** should usually control.
A bridge may add order, tie-breaks, watch rules, or governance glue.
It should not silently rewrite the parent rule unless the revision makes that rewrite explicit.

### 3. Narrow bridge can govern its declared downstream question

A bridge still governs its own narrow downstream question once the anchor's upstream question has been settled.
The point is not to flatten the archive into anchors only.
It is to keep bridges from accidentally becoming shadow anchors.

### 4. Cross-cluster tension requires repair, not quiet coexistence

If two anchors from neighboring clusters now point in different directions, the answer is not to say both are true in some vague sense.
The revision should usually do one of three things:

- tighten one anchor,
- add one short cross-reference or limiting sentence,
- or create one compact bridge only if the tension will clearly recur.

If none of those happens, the archive is shipping two live answers.
That should count as a defect, not as richness.

## What a revision should do when it finds a live conflict

A revision that encounters real live-doctrine tension should usually choose one of four repairs.

### 1. Tighten the winning note

If one note is clearly the main anchor and the other merely drifted, edit the winner so readers can see the controlling rule without opening a second file.

### 2. Narrow the losing note

If a bridge or support note overreached, trim it back to its real job.
Often one sentence of scope control is enough.

### 3. Add one explicit handoff sentence

If both notes remain valid but answer adjacent rather than identical questions, make that boundary explicit in both places.
A one-line handoff is often cheaper than a new note.

### 4. Mark and repair quickly if the tension is not yet fully resolved

During a live drafting pass, a small unresolved tension may temporarily remain.
If so, name it in the revision receipt or changelog and repair it soon.
Do not let unresolved doctrinal ambiguity harden into a normal archive condition.

## What should not decide precedence

The archive should **not** decide between live notes by:

- whichever file is newer,
- whichever file is longer,
- whichever file is cited more often,
- whichever file sounds more rhetorically forceful,
- or whichever path a reader happened to open first.

Those are signals of attention, not authority.

## Revision-receipt rule

When a revision materially resolves a live tension between notes, the receipt should usually say so briefly:

- which notes had the tension,
- whether the fix was a scope narrowing, anchor tightening, bridge fold-back, or one-line handoff,
- and whether any note changed status because of the repair.

That gives the archive a memory of why one path now governs without forcing readers to keep both old answers alive.

## False moves this note is meant to stop

### 1. Letting a bridge quietly become a rival anchor

A bridge earns life by solving one repeated operator or routing gap.
It should not slowly become a second main doctrine note by accumulation.

### 2. Treating two live answers as harmless pluralism

This archive is not a literature survey.
When it reaches a stable operational answer, it should not leave two conflicting live readings in place merely because both sound defensible.

### 3. Using recency as a substitute for explicit supersession

A later file does not automatically win.
If it should win, make that explicit by tightening routes, scope, or note status.

### 4. Shipping unresolved tension without naming it

Some drafting tension is unavoidable.
Hidden tension in a packaged revision is not.

## Fast use rule

When two notes seem to disagree:

1. **ask whether the difference is real or only verbal,**
2. **check whether both notes are actually live,**
3. **let the canonical anchor govern the shared upstream question,**
4. **let the bridge govern only its declared downstream question,**
5. **repair cross-cluster tension directly rather than normalizing two live answers,**
6. **and record the repair in the revision receipt or changelog.**

## Bottom line

The archive should not make readers arbitrate doctrine for themselves.
When two live notes seem to disagree, check status, check anchor-versus-bridge role, repair the tension directly, and leave one clear governing path rather than two live answers drifting beside each other.
