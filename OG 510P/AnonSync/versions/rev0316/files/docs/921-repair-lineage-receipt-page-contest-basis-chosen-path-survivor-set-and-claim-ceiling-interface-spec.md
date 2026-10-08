# Repair lineage receipt page: contest basis, chosen path, survivor set, and claim ceiling interface spec

## Purpose

After any serious contested repair, later operators need durable proof that answers:

> what was contested, which repair path was chosen, what survived, what changed in the live line, and what stronger claim stayed forbidden?

## Core decision

Every serious contested repair emits one first-class **Repair lineage receipt**.

The receipt owns:

- contest basis
- chosen repair path
- live mutation scope
- survivor set
- runtime / proof posture
- strongest safe sentence
- stronger rejected sentence
- reopen triggers

## Receipt sections

1. identity strip
2. contest basis section
3. chosen path section
4. survivor set section
5. claim ceiling section
6. reopen triggers section

### 1) Identity strip

Show:

- receipt id
- contested object reference
- acting seat
- approval or non-live path class
- timestamp

### 2) Contest basis section

Show:

- contest class
- evidence basis used
- chronology or permission verdict if relevant
- source freshness

### 3) Chosen path section

Show:

- chosen repair path
- whether the live line mutated
- runtime prerequisites satisfied at apply time
- any preserved export or side survivor created first

### 4) Survivor set section

Show:

- live winner ref
- side survivors
- archived losers
- local-only residue
- deleted or intentionally sacrificed participants

### 5) Claim ceiling section

Show:

- strongest safe sentence
- stronger rejected sentence
- whether the receipt proves repair, preservation-only, or only inspection

### 6) Reopen triggers section

Show:

- returning offline source
- restart or replay failure
- delete of protected survivor
- new evidence changing contest class
- path or authority drift

## Compact summary line

A trustworthy summary line should preserve this order:

1. contested object
2. contest class
3. chosen path
4. live mutation verdict
5. survivor set summary
6. strongest safe sentence

Example:

```text
notes.txt · blocked-ro-edit · overwrite-local-edits after export · live line reverted to RW source · one local-only extra preserved and one archive loser retained · proves resumed intake, not full historical reconciliation
```

## Acceptance criteria

A later operator can:

- reconstruct why repair happened
- tell whether the live line changed
- tell what survived and where
- tell what proof ceiling the receipt actually grants
- know what events reopen the receipt
