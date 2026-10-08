# Same-lineage reconnect proof page — remembered path, subject evidence, and target equivalence interface spec

## Purpose

This page answers one narrow but load-bearing question:

> when a target path is non-empty and the operator thinks this is the old tree, what exactly proves that claim strongly enough to treat the action as reconnect rather than risky merge?

This page exists so a product never hides same-lineage proof inside `Add anyway`, same-name coincidence, or operator memory.

## Core decision

Any non-empty-target bind that might be read as `restore the old directory` must pass through one first-class **Same-lineage reconnect proof** page before commit.

The page is required when any of these are true:

- the target is non-empty
- the product remembers an earlier path for this subject on this seat
- reconnect was entered from a disconnected state
- the proposed path differs from the strongest remembered path
- the product could otherwise overclaim `old tree restored`

## Fixed page order

1. **Reconnect claim strip**
2. **Remembered continuity evidence**
3. **Current target equivalence**
4. **Contradictions and missing proof**
5. **Allowed next actions**
6. **Receipt promise**

### 1) Reconnect claim strip

Show:

- subject label and stable handle
- acting seat
- requested target path
- strongest remembered path
- current reconnect claim (`proven`, `guarded`, `not proven`, `blocked`)

The operator should be able to answer: **is the product actually saying this is the old tree, or only that it might be?**

### 2) Remembered continuity evidence

Show evidence families such as:

- prior bind receipt for this seat and subject
- stored last-known bound path
- lineage marker / hidden identifier match
- recent disconnect receipt pointing to the same path
- prior approved repair/adoption receipt
- none

Each row should show strength class:

- `hard`
- `strong`
- `suggestive`
- `missing`

### 3) Current target equivalence

Show what the current target proves:

- same-path exact match to remembered path
- same-lineage marker present
- same-subject hidden state present but path differs
- same-name only, no lineage proof
- non-empty and ambiguous
- conflicting marker or other-subject evidence

The page must say whether equivalence is:

- `confirmed`
- `likely`
- `ambiguous`
- `contradicted`

### 4) Contradictions and missing proof

Show the strongest reasons the reconnect claim is weaker than it sounds:

- target path differs from remembered path
- same-name only
- missing lineage marker
- conflicting local bind already active elsewhere
- duplicate-sibling risk
- existing divergent bytes detected
- comparison freshness stale

The operator should be able to answer: **what would make `restore old tree` too strong a sentence here?**

### 5) Allowed next actions

Good actions include:

- `Reconnect to proven old tree`
- `Open divergence review before reconnect`
- `Choose remembered path instead`
- `Preserve local material before adopt`
- `Abort and inspect existing bind`

Poor actions include:

- `Connect anyway`
- `Use same name`
- `Proceed`

when they hide proof weakness.

### 6) Receipt promise

The page must say which later receipt will exist and what it will prove:

- reconnect claim class
- strongest remembered path
- evidence used
- equivalence verdict
- stronger rejected sentence

## Public object

### `same_lineage_reconnect_review`

Fields:

- `same_lineage_reconnect_review_id`
- `subject_ref`
- `seat_ref`
- `requested_target_path`
- `remembered_target_path`
- `continuity_evidence_rows[]`
- `target_equivalence_verdict`
- `reconnect_claim_class`
- `contradictions[]`
- `next_actions[]`
- `generated_at`

## Result

A good reconnect-proof page prevents five failures:

- same-name coincidence being mistaken for same-lineage proof
- default-root suggestions outrunning remembered-path evidence
- non-empty targets being treated as harmless reconnect without comparison
- reconnect success language outrunning what the product actually proved
- later operators having to guess whether `connected` meant `old tree restored` or merely `target accepted`
