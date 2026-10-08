# Hash-and-preseed review page — local byte candidates, dedup search, and archive dependency interface spec

## Purpose

This page exists because `we found the bytes locally` is a much stronger statement than `we are hashing local files`.
AnonSync should require one **Hash-and-preseed review** whenever a receiving seat is checking local files, deduplication candidates, or pre-seeded content before deciding whether to transfer bytes.

## Core distinctions

The page must keep these truths separate:

- local files are being scanned
- local files are being hashed
- candidate byte matches exist
- deduplication copy is underway
- archive-backed hash reuse is available
- full transfer remains necessary

## Object model

### `hash_preseed_review`

- `hash_preseed_review_id`
- `scope_ref`
- `candidate_pool_class` (`preseeded-target`, `local-dedup-search-space`, `archive`, `mixed`, `unknown`)
- `hash_work_state` (`not-started`, `scanning`, `hashing`, `candidate-match`, `copying-local-blocks`, `complete-no-match`, `unknown`)
- `read_only_ceiling` (`not-applicable`, `local-preseed-check-limited`, `unknown`)
- `archive_hash_reuse` (`available`, `disabled`, `missing-match`, `unknown`)
- `disk_cost_note` (`none`, `elevated-read`, `elevated-write`, `temporary-growth`, `unknown`)
- `resulting_byte_plan_class`
- `proof_ceiling`
- `next_review_ref`

## Required sections

### 1) Candidate pool

Show where local candidate bytes may come from:

- current target path
- other local files searched for deduplication
- Archive contents
- mixed candidate pool

### 2) Current work rung

Show exactly one current rung:

- `Scanning local candidates`
- `Hashing local candidates`
- `Candidate hash match found`
- `Copying local blocks`
- `No usable local byte match`

This rung must be visible because `hashing` is weaker than `match found`.

### 3) Preconditions and ceilings

Show:

- whether the workflow depends on Archive being present and populated
- whether read-only posture changes or limits the check
- whether lazy hashing or delayed indexing means certainty remains deferred

### 4) Cost and side effects

Show:

- local read pressure
- local write pressure
- temporary disk growth risk during local block copy

### 5) Resulting safe sentence

Examples:

- `Local bytes are being hashed for pre-seed verification; reuse remains unproven.`
- `Deduplication has a candidate match and is copying local blocks, which may raise temporary disk usage.`
- `Archive-backed rename reuse is unavailable because Archive is disabled or lacks the required hash.`

## Interaction rules

1. The page may not say `using local copy` while the state is only `scanning` or `hashing`.
2. The page must warn when Archive absence removes one cheap-reuse path.
3. If no usable local bytes are found, the next branch to full transfer must be explicit.
4. The page must link directly to byte-plan contract sheet and lineage receipt.

## Acceptance bar

The page is good enough when a cautious operator can answer:

- where local candidate bytes are coming from
- whether the system is still hashing or has actually found a match
- whether Archive is part of the plan
- what local cost is being incurred
- when full transfer becomes the honest next statement
