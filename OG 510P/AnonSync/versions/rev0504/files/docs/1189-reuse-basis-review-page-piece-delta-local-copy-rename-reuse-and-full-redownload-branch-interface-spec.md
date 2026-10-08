# Reuse-basis review page — piece delta, local copy, rename reuse, and full-redownload branch interface spec

## Purpose

This page exists because several distinct byte-economy paths all sound like `optimized transfer`.
AnonSync should require one **Reuse-basis review** whenever it matters to know *which* cheaper path is being relied on and what breaks that path.

## Supported reuse families

1. **Piece-delta transfer** — only changed pieces move.
2. **Local-block reuse** — matching bytes are copied from local candidates.
3. **Archive-assisted rename reuse** — same-hash bytes are restored/repositioned under a new name.
4. **Pre-seeded byte match** — existing target bytes survive after local hashing.
5. **Full redownload** — no acceptable reuse path remains.

## Object model

### `reuse_basis_review`

- `reuse_basis_review_id`
- `scope_ref`
- `primary_reuse_family`
- `competing_reuse_families[]`
- `failure_triggers[]`
- `required_prerequisites[]`
- `current_blockers[]`
- `final_fallback_branch` (`piece-delta`, `local-copy`, `archive-reuse`, `preseed-preserve`, `full-redownload`, `manual-cleanup-first`, `unknown`)
- `safe_sentence`
- `blocked_sentence`

## Required sections

### 1) Primary reuse family

Show the currently leading family and why it is leading.
Examples:

- `Changed-file delta path because piece alignment remains usable.`
- `Rename reuse path because Archive contains same-hash bytes.`
- `Pre-seeded preserve path because local target bytes are being verified.`

### 2) Required prerequisites

List prerequisites such as:

- piece alignment surviving the change
- local candidate bytes existing
- Archive enabled and populated
- local hashing completed
- partial residue remaining safe to keep

### 3) Failure triggers

List concrete reasons the current cheaper path can collapse into full transfer, such as:

- change shifts all pieces
- no local candidate hash match
- Archive missing or disabled
- stuck partial residue requiring deletion
- explicit cleanup action removing the local basis

### 4) Final fallback branch

Show the honest next branch if the leading family fails.
This must never be hidden in secondary text.

### 5) Safe sentence

Examples:

- `Only changed pieces should move unless piece alignment is lost.`
- `Rename reuse is available only because Archive still holds same-hash bytes.`
- `Pre-seeded local bytes are being evaluated; if no match survives, full redownload follows.`

## Interaction rules

1. The page may not use `optimized` as the only explanation.
2. If Archive is a prerequisite, its absence must show as a blocker, not a footnote.
3. If the honest fallback is full redownload, show it as a first-class branch.
4. If cleanup of partial residue is being proposed, the page must link to survivor proof.

## CLI projection

```text
anonsync reuse review --scope subject:ledger/file:Q4.xlsx
```

## Acceptance bar

The page is good enough when a cautious operator can answer:

- which reuse family is actually in play
- what prerequisites are keeping it alive
- what concrete event would break it
- what the honest fallback branch is
