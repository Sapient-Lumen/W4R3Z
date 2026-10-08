# Artifact normalization review page — member shape, pruning, and provenance interface spec

## Purpose

Review how raw sources become normalized evidence members without losing provenance or over-disclosing unrelated material.

This page exists so `clean it up`, `zip it`, `leave only logs`, and `move the dump to a public folder` become explicit review decisions instead of irreversible cleanup folklore.

## Inputs

- raw evidence intake object
- evidence plan and capture-matrix bindings
- proposed keep/prune/extract/rename actions
- duplicate and rotation heuristics
- sensitivity findings
- expected manifest/member targets

## Primary questions this page must answer

1. Which raw sources should be kept whole, narrowed, extracted, split, renamed, or discarded?
2. Which normalized members will each raw source produce?
3. Does the proposed cleanup preserve enough provenance for later review?
4. Does pruning reduce oversharing without silently dropping a required signal?
5. What stronger sentence about package clarity is still unsupported after normalization?

## Sections

### 1. Transformation ledger

Per raw source show:

- proposed action (`keep-as-is`, `extract-member`, `split-folder`, `prune-subset`, `rename-for-clarity`, `recompress`, `discard`, `hold`)
- expected normalized member(s)
- provenance effect
- evidence-plan row(s) affected

### 2. Duplicate / rotation grouping card

Show:

- same-class log rotations
- probable duplicates
- compressed/uncompressed equivalents
- contradiction candidates that should remain separate

### 3. Oversharing and pruning card

Show:

- unrelated internal files likely present
- path / identity / secret exposure risk
- safer narrowed alternative
- what diagnostic question may weaken if pruning proceeds

### 4. Provenance preservation card

Show:

- lineage fields that will survive normalization
- lineage fields at risk of being lost
- whether a rename or repack needs an attached origin note
- strongest supported provenance sentence now
- one stronger forbidden sentence

### 5. Normalization verdict card

Show one approved verdict, for example:

- `raw NAS folder narrowed to reviewed log and journal members with provenance preserved`
- `mobile hidden-folder harvest normalized into one reviewed log set`
- `core dump retained as original gz member; no rename allowed`
- `cannot normalize safely because source/witness binding is still weak`

## Required interactions

- `Approve transform`
- `Reject transform`
- `Keep contradiction separate`
- `Group rotation members`
- `Attach origin note`
- `Open packet assembly review`
- `Issue intake receipt draft`

## Guardrails

- Never discard a raw source silently once it entered intake.
- Never rename or recompress a member without retaining origin lineage.
- Never collapse contradiction candidates into one cleaned member.
- Never let privacy pruning silently break required-row coverage.
- Never present normalization as complete while provenance is materially degraded.

## Output

A reviewed normalization decision preserving raw-to-normalized lineage, duplicate/rotation handling, pruning rationale, and strongest supported provenance language.

