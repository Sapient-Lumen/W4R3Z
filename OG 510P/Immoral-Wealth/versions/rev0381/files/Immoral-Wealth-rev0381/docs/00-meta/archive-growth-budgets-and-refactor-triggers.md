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

# Archive growth budgets and refactor triggers

## What this note is for

This archive already has a rule for **which questions deserve new bytes**.
What it still needs is a compact rule for **how many bytes different kinds of notes should get**, **when a revision should tighten instead of branch**, and **when existing files should be merged, split, or compressed** before the archive quietly turns into a route maze.

Use this note with [`archive-policy.md`](archive-policy.md), [`research-triage-and-closure-rules.md`](research-triage-and-closure-rules.md), [`canonical-anchors-and-bridge-note-discipline.md`](canonical-anchors-and-bridge-note-discipline.md), [`note-status-and-supersession-discipline.md`](note-status-and-supersession-discipline.md), and [`term-discipline-and-synonym-control.md`](term-discipline-and-synonym-control.md).

## Default growth rule

Every revision should try these moves in order:

1. **tighten an existing file,**
2. **add at most one compact bridge note if tightening is not enough,**
3. **trim routes or dedupe around the change,**
4. **and only then allow a wider branch.**

A revision does not earn new bytes merely because a distinction is true.
It earns new bytes only when the archive becomes easier to use, easier to govern, or less likely to repeat itself badly.

## Standing size classes

These are **soft budgets**, not sacred caps.
They exist to create pressure for compression, not to forbid the occasional justified exception.

### 1. Front-door files should stay short

`README.md`, `START_HERE.md`, and other top-level routing files should mostly **route and compress**, not restate the full archive.
When they start behaving like parallel theory notes, trim them.

Working target:
- `README.md`: usually **3-7 KB**
- `START_HERE.md`: usually **8-14 KB**
- top-level routing additions: usually **one route in, one route out**, not another mini-index

### 2. Stable theory and program notes may be medium, but should justify it

Core notes can be longer because they carry durable doctrine.
But they should still prefer a clean minimum rule, a few repeated-use distinctions, and a fast use rule over a literature-tour shape.

Working target:
- most stable framework or program notes: usually **6-16 KB**
- a small number of anchor notes may exceed that when they are genuinely central
- once a note is long because it contains several reusable sub-rules, consider splitting the reusable bridge rather than letting the anchor swell indefinitely

### 3. Operator and bridge notes should stay small

Case-work bridges, routing notes, tie-break rules, watch notes, and similar operator files should usually stay visibly smaller than anchor notes.
If they become long, they are often trying to become a second anchor.

Working target:
- most operator / bridge notes: usually **2-8 KB**

### 4. Ledgers may grow, but must compress old detail

`CHANGELOG.md`, `ARCHIVE_INDEX.md`, and other ledgers are allowed to accumulate.
But once they become some of the archive's largest objects, older detail should be compressed.
The archive should not spend more bytes narrating itself than explaining immoral wealth inequality.

## Refactor triggers

Treat these as standing triggers to **merge, split, trim, or compress**.

### 1. Merge trigger

Merge when two notes:
- are almost always read together,
- share the same user and decision point,
- or differ mostly by examples, caveats, or repeated setup rather than by a real judgment rule.

### 2. Split trigger

Split when one file now contains:
- two reusable rules that future revisions will keep citing separately,
- one stable anchor plus one compact bridge that keeps interrupting it,
- or one section that is mainly routing glue and would make future case work shorter as its own note.

### 3. Route-trim trigger

Trim routes when top-level files start pointing to too many neighboring notes for the same question.
A route should normally move a reader **forward**, not sideways across every nearby distinction.

### 4. Duplicate-language trigger

If a new revision would add repeated explanation that is already present in two or more current files, stop and either:
- tighten one anchor,
- add one bridge,
- or cut the repetition.

### 5. Ledger-compression trigger

Compress old revision notes, old route descriptions, or old index prose when those files start becoming among the archive's biggest recurring objects.
Older entries should usually become one-line summaries once their local novelty is no longer live.

## Case-work growth rule

Case work is where archive bloat most easily hides.
A real-case memo should usually stay within the reusable headings already established in [`../20-program/case-application-protocol.md`](../20-program/case-application-protocol.md).
If a case cannot be written cleanly that way, the first answer is usually **better diagnosis or better evidence**, not a new permanent doctrine note.

A local case wrinkle should become a permanent archive file only when it clearly survives the repeated-use test across many future cases.
Otherwise it belongs in temporary scratch, a one-line open question, or an edit to an existing note.

## Temporary scratch rule

Temporary scratch is allowed while producing a revision.
But scratch that does not earn repeated use should be removed before the long-run bundle is written.
The archive should keep conclusions, not a warehouse of intermediate debris.

## Exceptions rule

A note may exceed its soft budget when at least one of these is true:
- it is a core anchor that many later notes genuinely depend on,
- keeping it whole is clearer than splitting it,
- or the extra length removes future duplication elsewhere.

When that happens, the revision should usually trim something nearby so the archive's overall waist does not keep widening. If the extra length mostly protects old route memory, prefer supersession or redirect status using [`note-status-and-supersession-discipline.md`](note-status-and-supersession-discipline.md).

## Five questions before shipping a revision

Before a revision is bundled, ask:

1. **What decision gets easier because of this change?**
2. **Why was tightening not enough?**
3. **What future repetition does this cut?**
4. **What nearby route, note, or ledger can now be shortened?**
5. **If this were the tenth note of its kind, would the archive still feel governable?**

If those questions do not have crisp answers, the default move should usually be to cut rather than add.

## Fast use rule

Use this note whenever a revision is about to add a new file or grow a current one.
The archive should not only ask **is this true?** or **is this useful?**
It should also ask **is this the right size, in the right place, with the right permanence?**
