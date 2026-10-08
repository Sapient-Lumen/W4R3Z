# Non-empty target divergence review page — compared classes, overwrite risk, and authority posture interface spec

## Purpose

This page owns the next question after reconnect proof:

> if the target is populated, what exactly is in agreement, what merely coexists, what genuinely diverges at the same path, and what overwrite or delete risk remains?

This page exists so `Folder not empty` never substitutes for a real comparison grammar.

## Core decision

Any non-empty-target bind that is not already blocked must create one first-class **Non-empty target divergence review**.

The review is required whenever local existing material could plausibly be:

- same-lineage continuation
- harmless local-only residue
- remote-only additions waiting to land
- same-path divergence with overwrite risk
- conflicting material that should block merge

## Fixed review order

1. **Comparison verdict strip**
2. **Compared material classes**
3. **Same-path divergent candidates**
4. **Authority and chronology posture**
5. **Admissible outcomes**
6. **Receipt promise**

### 1) Comparison verdict strip

Show:

- target path
- comparison freshness
- strongest divergence verdict
- strongest safe sentence

Example verdicts:

- `Non-empty target is mostly identical; no same-path divergence found`
- `Local-only and remote-only material can merge; no overwrite candidates`
- `Same-path divergence exists; guarded review required before adopt`
- `Conflicting material blocks merge`

### 2) Compared material classes

Always show counts or reviewed summaries for:

- `identical`
- `local-only`
- `remote-only`
- `same-path divergent`
- `path collisions / name collisions`
- `unreadable / unknown`

The operator should be able to answer: **what simply merges, and what actually disagrees?**

### 3) Same-path divergent candidates

For each reviewed candidate or bucket, show:

- path
- local candidate summary
- remote candidate summary
- strongest known source/lineage clue
- current overwrite/delete risk

Risk classes may include:

- `low`
- `guarded`
- `high`
- `blocked`

### 4) Authority and chronology posture

If ranking or overwrite recommendations depend on chronology, say so explicitly.

Show:

- chronology confidence (`high`, `guarded`, `low`, `unknown`)
- whether a winner recommendation is coming from timestamp only
- whether stronger authority proof exists
- whether no honest winner can yet be named

The product must not let `latest timestamp wins` hide as a silent default.

### 5) Admissible outcomes

Good actions include:

- `Adopt identical + merge non-overlapping material`
- `Preserve local-only material then adopt`
- `Choose explicit winner for divergent paths`
- `Quarantine losing candidates first`
- `Stop and choose another target`

Poor actions include:

- `OK`
- `Merge`
- `Add anyway`

when they hide compared classes and overwrite risk.

### 6) Receipt promise

The page must say which receipt will preserve:

- compared classes
- divergence verdict
- chronology/authority posture
- preservation decision
- stronger rejected sentence

## Public object

### `non_empty_target_divergence_review`

Fields:

- `non_empty_target_divergence_review_id`
- `subject_ref`
- `target_path`
- `comparison_freshness_at`
- `class_counts`
- `divergent_candidates[]`
- `authority_posture`
- `chronology_confidence`
- `recommended_outcomes[]`
- `generated_at`

## Result

A good divergence review prevents five failures:

- `folder not empty` standing in for real compared classes
- local-only residue being mistaken for safe overwrite
- same-path disagreement being flattened into generic merge language
- timestamp-only ranking masquerading as strong authority
- later operators losing the evidence that a guarded merge was performed
