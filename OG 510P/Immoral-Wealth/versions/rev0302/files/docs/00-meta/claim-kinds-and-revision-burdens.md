# Claim kinds and revision burdens

## What this note is for

This archive now has enough live anchors, bridges, governance notes, ledgers, and integrity surfaces that a reviser can make a subtle but costly mistake:
not **changing the wrong wording**, but **treating the wrong kind of claim as if it lived on the same revision burden as the one in front of them**.

A fresher dataset should not by itself overturn a constitutional rule.
A routing failure should not by itself rewrite the archive's moral target.
A bundle-metadata mismatch should not be argued about as if it were a doctrine dispute.

This note gives the archive one compact rule for asking, before any revision:
**what kind of claim is this note mainly carrying, and what kind of pressure is actually strong enough to revise it?**

Use this note with [`archive-policy.md`](archive-policy.md), [`note-status-and-supersession-discipline.md`](note-status-and-supersession-discipline.md), [`doctrine-precedence-and-conflict-repair.md`](doctrine-precedence-and-conflict-repair.md), [`case-to-doctrine-promotion-and-quarantine.md`](case-to-doctrine-promotion-and-quarantine.md), [`doctrine-revision-and-demotion-under-case-pressure.md`](doctrine-revision-and-demotion-under-case-pressure.md), and [`../../ARCHIVE_INDEX.json`](../../ARCHIVE_INDEX.json).

## Default rule

Before revising a note, ask two questions in order:

1. **What is this file mainly for?**
2. **What kind of pressure is strong enough to change that kind of file?**

The archive should not treat every note as if it lived on one flat epistemic plane.
Different notes earn revision under different burdens.
That distinction is part of keeping the archive tight and coherent rather than reactive.

## The archive's seven coarse claim kinds

These are intentionally coarse.
They are for revision discipline, not for perfect philosophical taxonomy.

### 1. Navigation surface

These notes help readers enter or route through the archive.
Examples: `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, `ARCHIVE_INDEX.json`.

They should change when:

- the canonical path changed,
- the route metadata changed,
- a front-door summary became stale,
- or a new release-surface mismatch appeared.

They should not silently introduce new doctrine while pretending to be route help.

### 2. Constitutional doctrine

These notes state the archive's live moral and institutional rules about what counts as immoral wealth inequality and what a tolerable wealth order requires.
Examples mostly live in `docs/10-framework/`.

They should change when:

- argument-level conflict appears,
- repeated case pressure exposes a real boundary failure,
- a bridge has been carrying too much doctrine,
- or the archive explicitly decides to revise, narrow, or demote a rule.

They should not be revised merely because a fresher descriptive source arrived or because one vivid case feels rhetorically forceful.

### 3. Program rule

These notes say how to move from doctrine to action, measurement, routing, package choice, watch posture, comparison, or implementation.
Most of `docs/20-program/` lives here.

They should change when:

- repeated use shows a real routing failure,
- a stable operator gap appears,
- a tie-break rule keeps misfiring,
- or a better decision order clearly reduces rereading or error.

They are usually more revisable than constitutional doctrine, but they still need more than stylistic preference.

### 4. Archive governance

These notes govern byte budgets, note status, supersession, promotion, demotion, source refresh, chronology, release readiness, and similar maintenance decisions.
Most of `docs/00-meta/` lives here.

They should change when:

- the archive itself drifts,
- a release or routing failure recurs,
- a real governance gap shows up,
- or a later compression can replace several ad hoc habits with one tighter rule.

They should not grow into shadow doctrine about wealth orders themselves.

### 5. Source ledger

These surfaces say what external support the archive relies on and what support functions those sources are doing.
Examples: `SOURCES.md` and `SOURCES.json`.

They should change when:

- a source is refreshed,
- a support function is newly covered,
- a weak anchor needs strengthening,
- or a citation map became stale.

They should not be mistaken for live doctrine.
A ledger describes support; it does not by itself settle the moral rule.

### 6. Question ledger

These notes keep track of open research questions and parked uncertainty.
Examples: `docs/00-meta/research-questions.md`, `docs/90-open/open-questions.md`.

They should change when:

- a question is closed enough to demote,
- a genuinely new open question appears,
- or the archive needs to reprioritize active proof work.

They are not themselves arguments for live doctrine.
They are a queue and memory surface.

### 7. Integrity artifact

These files record what bundle exists, what changed, and whether the package is internally coherent.
Examples: `REVISION-RECEIPT.json`, `CHANGELOG.md`, `VERSION`, `MANIFEST.json`, `MANIFEST.sha256`.

They should change when:

- a new revision is built,
- a release-surface mismatch is repaired,
- a manifest rule changes,
- or the archive needs to truthfully record an anomaly.

Their burden is not argumentative subtlety but exact agreement with the shipped bundle.

## Mixed-note rule

Some notes contain more than one kind of material.
For example:

- a program note may open with a short doctrinal summary,
- a front-door note may carry a one-screen normative answer,
- a governance note may cite one real integrity failure.

In those cases, the archive should still name one **dominant claim kind** for routing and revision purposes.
If a secondary kind keeps expanding, spin that material back into the correct anchor instead of letting one note pretend to be several files at once.

## Revision-burden rule by claim kind

Use this quick map.

- **Navigation surface** -> revise for route drift, stale summaries, or release-surface mismatch.
- **Constitutional doctrine** -> revise for argument-level conflict, repeated case pressure, or explicit anchor repair.
- **Program rule** -> revise for repeated operator failure, better tie-break order, or cleaner routing under live use.
- **Archive governance** -> revise for archive drift, recurring maintenance failure, or cleaner compression of archive habits.
- **Source ledger** -> revise for fresher support, coverage gaps, or citation-map cleanup.
- **Question ledger** -> revise for reprioritization, closure, or reopening.
- **Integrity artifact** -> revise for exact bundle truth and package agreement.

## False moves this note is meant to stop

### 1. Treating new data as automatic doctrine overthrow

A fresher data point may pressure doctrine.
It does not automatically rewrite it.
Use [`doctrine-revision-and-demotion-under-case-pressure.md`](doctrine-revision-and-demotion-under-case-pressure.md).

### 2. Treating a route problem as a theory problem

If readers cannot find the right note, the first fix is often routing or claim-kind clarification, not a new substantive branch.

### 3. Treating a source ledger change as if the archive changed its norm

Adding or refreshing support does not itself change the moral rule.
It changes how well the rule is backed or how recently it is evidenced.

### 4. Treating integrity artifacts as deliberative doctrine

When `README.md`, `VERSION`, the receipt, and the bundle disagree, the right response is repair.
It is not an invitation to theory debate.

## Machine-readable rule

`ARCHIVE_INDEX.json` should carry one coarse `claim_kind` field for each file so future revisions and tools can see, before editing, whether a note mainly carries navigation, doctrine, program, governance, ledger, question, or integrity weight.

That field is intentionally coarse.
It exists to stop category mistakes before they widen into archive drift.

## Fast use rule

When touching a file:

1. **name its dominant claim kind,**
2. **ask what burden is strong enough to revise that kind,**
3. **avoid using lower-burden pressure to rewrite higher-burden notes,**
4. **repair routing, ledger, or integrity failures at their own layer,**
5. **and only then decide whether the archive actually needs new retained bytes.**

## Bottom line

The archive should not let every challenge revise every note on the same terms.
First identify what kind of claim a note mainly carries.
Then use the burden that fits that kind.
That is how a dense archive stays coherent instead of reactive.
