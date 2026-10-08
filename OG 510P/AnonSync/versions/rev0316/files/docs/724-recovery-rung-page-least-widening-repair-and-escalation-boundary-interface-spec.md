# Recovery rung page: least-widening repair and escalation boundary interface spec

## Purpose

Answer the ordinary question:

> what is the least-strong honest next move for this warning, what would a stronger move buy me, and what damage or widening comes with skipping ahead?

This page exists because troubleshooting lore often presents restart, rescan, reconnect, remove/re-add, restore-source, or rebuild actions as a loose list rather than a typed escalation ladder.

## Core rule

Every repairable warning must map to a **recovery rung ladder**.
The ladder must order actions from least-widening to strongest and must explain:

- what each rung proves
- what it does **not** prove
- what it risks mutating
- what stronger rung becomes justified only if the lower rung fails

## Required sections

### 1) Current least-strong recommended rung

Always publish:

- current recommended rung name
- why this rung is currently least-strong and sufficient
- what proof it may restore
- what evidence would justify escalation

Example rung kinds:

- `wait-and-observe`
- `inspect evidence`
- `refresh probe / rescan`
- `clock repair`
- `restore byte source`
- `disconnect / reconnect`
- `rebuild local database`
- `remove and re-add`
- `branch / preserve before destructive repair`

### 2) Full ladder

Render a compact table:

| Rung | Mutates live bytes? | Mutates continuity state? | Restores which proof? | Escalate when |
| --- | --- | --- | --- | --- |
| Observe | no | no | freshness only | condition persists beyond threshold |
| Rescan | no | no | index/detection proof | rescan contradicts nothing useful |
| Clock repair | no | no | chronology trust | drift remains or files still empty |
| Reconnect | maybe | local continuity state | route/local db proof | subject remains suspended |
| Remove/re-add | maybe | yes | clean local continuity | lower rungs failed and bytes preserved |

### 3) Skip-risk warning

If the operator skips the least-strong rung, show:

- what wider mutation occurs
- what evidence may be destroyed
- what future claims become weaker or stronger
- what preserve-first step is recommended first

### 4) Proof after success

Define the exact success witness for each rung:

- warning cleared with fresh evidence
- chronology trust restored
- source witness restored
- continuity rebuilt on this subject
- still blocked / escalate

### 5) Preserve-first branch

Whenever a stronger rung risks bytes or continuity evidence, offer:

- export witness packet
- preserve retained copy
- create clean branch
- snapshot local state

## Receipt rules

Every applied rung must emit a durable record of:

- requested rung
- rung actually used
- why it was justified
- what stronger rungs remained unused
- success witness or contradiction
- what residue still remains

## Data model

- `recovery_rung_review_id`
- `warning_id`
- `current_recommended_rung`
- `ladder[]`
- `skip_risk_summary`
- `preserve_first_options[]`
- `success_witness_contract`
- `applied_rung_receipt_ref`

## Failure this page prevents

Without this page, products slide from warning row to strong repair without proving why lighter rungs were insufficient.

AnonSync should instead make repair strength, mutation cost, and escalation proof explicit.
