# Byte-plan contract sheet page — reuse basis, hash witness, and redownload ceiling interface spec

## Purpose

This page exists because `will not re-download` sounds stronger than most real evidence.
AnonSync should require one first-class **Byte-plan contract sheet** whenever the product suggests piece-delta transfer, local reuse, archive-assisted reuse, pre-seeded reuse, or resume from local residue.

The page must keep six truths separate:

1. transfer subject
2. current byte-plan class
3. reuse basis
4. witness grade
5. fallback-to-redownload class
6. strongest safe sentence

## Object model

### `byte_plan_contract`

- `byte_plan_contract_id`
- `scope_ref`
- `subject_ref`
- `change_class` (`new-file`, `changed-file`, `renamed`, `moved`, `preseeded-connect`, `resume-after-interrupt`, `unknown`)
- `byte_plan_class` (`piece-delta-transfer`, `local-block-reuse`, `archive-assisted-rename-reuse`, `preseeded-byte-match`, `full-redownload`, `mixed`, `unknown`)
- `reuse_basis` (`changed-pieces-only`, `local-dedup-search`, `archive-same-hash`, `preseeded-local-hash`, `partial-local-residue`, `none`, `unknown`)
- `witness_grade` (`intent-only`, `hashing`, `candidate-match`, `byte-reuse-proven`, `transfer-observed`, `resume-proven`, `unknown`)
- `archive_dependency` (`required`, `helpful`, `none`, `unknown`)
- `partial_residue_state` (`none`, `present-resumable-unproven`, `present-stuck`, `cleaned`, `unknown`)
- `fallback_redownload_class` (`none-expected`, `possible`, `required`, `unknown`)
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `related_review_refs[]`
- `related_receipt_refs[]`

## Required sections

### 1) Transfer subject

Show:

- subject and path handle
- event class that triggered the byte plan
- whether the current claim is about one file, subtree, or reconnect scope

### 2) Current byte-plan class

Show exactly one leading class:

- `Only changed pieces expected to move`
- `Local block reuse being attempted`
- `Archive-assisted rename reuse expected`
- `Pre-seeded local bytes being checked`
- `Full redownload remains required`
- `Mixed / not yet compiled`

### 3) Reuse basis and prerequisites

Show:

- the concrete basis for reuse
- required prerequisites such as Archive or local candidate files
- whether the basis is present, missing, or not yet proven

### 4) Witness grade

Show whether the current evidence is:

- intent only
- hashing/checking
- candidate match
- byte reuse proven
- resume proven

The page may not collapse these into one generic `optimizing` label.

### 5) Fallback-to-redownload class

Show exactly one of:

- `redownload not expected from current witness`
- `redownload still possible`
- `redownload currently required`
- `not enough evidence`

### 6) Safe sentence

Examples:

- `Only changed pieces are expected to move, but this is still weaker than no-redownload proof for the full file.`
- `Local byte candidates are being hashed; reuse is plausible but not yet proven.`
- `Rename reuse depends on Archive hash match; without that match this may redownload.`
- `Partial residue exists, but safe resume is not yet proven.`

## Interaction rules

1. The primary badge may not say `No re-download` unless witness grade is at least `byte-reuse-proven` or equivalent stronger evidence exists.
2. `resume available` may not appear only because residue exists.
3. A rename or move path may not promise reuse unless Archive dependency and hash-match basis are explicitly shown.
4. The page must link directly to hash/pre-seed review and partial-transfer survivor proof when certainty remains below `byte-reuse-proven`.

## CLI projection

Examples:

```text
anonsync byte-plan show --scope subject:ledger/file:Q4.xlsx
anonsync byte-plan show --scope path:/vault/ledger/Q4.xlsx --json
```

## Acceptance bar

The page is good enough when a cautious operator can answer all of the following from one view:

- what byte plan is currently claimed
- what reuse basis exists
- what witness actually supports it
- whether redownload is still possible
- what stronger sentence the product refused to make
