# Destructive-assumption proof page: archive-reviewed, overwrite-risk, and successor-epoch commit

This page exists so a destructive step based on human review stops looking like an ordinary repair click.
The canonical cases are:

- recreating a subject after `Service files missing`
- deleting hidden continuity state after checking Archive
- accepting overwrite / delete risk on a pre-populated target
- proceeding when the product cannot prove continuity preservation

## Operator question

> if I commit this destructive step on the strength of my own review, what exactly did I review, what survives, what becomes a successor epoch, and what stronger preservation claim remains blocked?

## When this page must appear

Render whenever the operator is about to:

- delete `.sync`-class continuity state or equivalent service capsule
- recreate a subject after checking Archive / history manually
- accept merge semantics that may overwrite existing local material
- commit a repair where preserved continuity is not machine-proved
- approve a successor epoch because the old one is no longer trusted

## Fixed page order

1. **Destructive step summary**
2. **Human review checklist with attested results**
3. **Survivor map**
4. **Successor-epoch verdict**
5. **Proof ceiling after commit**

## 1) Destructive step summary

Show:

- destructive step class (`delete-service-capsule`, `recreate-subject`, `merge-into-occupied-tree`, `overwrite-acceptance`, `other`)
- current reason
- whether the step is reversible
- strongest safe sentence
- stronger blocked sentence

The operator must be able to answer: **what destructive boundary am I crossing?**

## 2) Human review checklist with attested results

Require explicit reviewed answers for:

- Archive / history inspected? with result
- unsynced local-only material inspected? with result
- path-lineage inspected? with result
- overwrite targets inspected? with result
- peer / chronology uncertainty acknowledged? with result

Each checklist row must force one of:

- `reviewed and clear`
- `reviewed and still risky`
- `not reviewed`
- `not applicable`

The operator must be able to answer: **what did I personally check before destroying state?**

## 3) Survivor map

Show survivor expectations for:

- payload bytes
- Archive / history bytes
- continuity spine / subject identity
- local path binding
- peer expectations
- receipts and audit trail

The map must explicitly separate:

- `survives in place`
- `survives only as residue`
- `recreated successor`
- `lost if assumption is wrong`
- `unknown`

## 4) Successor-epoch verdict

Show one verdict:

- `preserved continuity still proved`
- `successor epoch intentionally created`
- `destructive repair without continuity proof`
- `unknown`

If the verdict is not `preserved continuity still proved`, the page must state that the product is moving forward on reviewed necessity, not preserved identity proof.

The operator must be able to answer: **am I fixing the same subject, or creating a reviewed successor?**

## 5) Proof ceiling after commit

Show what the product will and will not be able to say afterwards.

Allowed examples:

- `A new subject instance was created after reviewed archive check.`
- `Overwrite-capable merge proceeded on operator attestation.`
- `Continuity preservation remains unproved.`

Blocked examples:

- `Nothing important was lost.`
- `This was the same subject all along.`
- `Every overwritten file was expendable.`
- `Archive contained nothing valuable everywhere.`

## Primary actions

Examples:

- `Commit reviewed successor epoch`
- `Back out and inspect Archive again`
- `Export destructive-assumption receipt`
- `Open survivor map in detail`

## Receipt / audit consequence

Committing this page must emit one receipt preserving:

- destructive step class
- attested checklist results
- survivor map
- successor-epoch verdict
- blocked stronger sentence
- expiry / reopen conditions
