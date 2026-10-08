# Read-only divergence review page: suspension, heal, and local survivor fate interface spec

## Purpose

This review exists for the most common but still most confusing non-authority case:
local edits or deletions happened on a Read Only seat and the operator now needs one page that answers:

> will these local differences suspend future updates, be healed from source, or remain as local-only survivors — and what proof still separates `option visible` from `healing is really governing runtime behavior`?

## When this review must appear

Trigger this review when:

- local edits are detected on a Read Only seat
- the operator enables or disables `Overwrite any changed files`
- a default posture implies overwrite on a new RO subject
- a troubleshooting path depends on destructive source heal

## Fixed page order

1. divergence summary header
2. affected-class fate table
3. survivor rail
4. proof rail
5. approval footer

### 1) Divergence summary header

Show:

- subject / seat / runtime
- current posture (`suspend-only`, `source-heal-available`, `source-heal-active`, `unknown`)
- strongest safe sentence after apply
- stronger rejected sentence after apply

### 2) Affected-class fate table

Rows:

- edited file
- deleted file
- renamed file
- added file

Columns:

- current observed fate
- predicted fate under current posture
- shared-line effect
- local survivor effect
- archive / salvage note

Plain-language examples must be included, such as:

- `Edited files revert to the most recent authoritative version when source-heal is active.`
- `Deleted files are restored from source state rather than published as deletes.`
- `Renamed files can leave the renamed local survivor while the old authoritative path returns.`
- `Added files remain local-only and unsynced even while other divergence classes heal.`

### 3) Survivor rail

Show clearly:

- which additions remain stranded locally
- whether local rename residue remains after old-path re-download
- whether the operator should branch/export before turning on destructive heal

### 4) Proof rail

Possible rungs:

- `read-only posture documented`
- `overwrite option visible`
- `subject currently marked overwrite`
- `seat-class hardwire documented`
- `behavior witnessed on affected object`

The page must say directly when proof is weaker than the operator hopes.

### 5) Approval footer

Require acknowledgment whenever the predicted state mixes destructive heal with survivor residue.

## Rules

### Rule 1 — suspension and heal are different verdicts

The page must never treat them as one boolean.

### Rule 2 — mixed outcomes must stay visible

The operator must see that some divergence classes heal while others remain local-only.

### Rule 3 — proof must remain separate from documentation

`The docs say encrypted seats overwrite` is weaker than `this runtime has already demonstrated the behavior on this subject`.
