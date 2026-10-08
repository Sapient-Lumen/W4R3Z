# Rule agreement page — ledger equivalence, shared meaning, and counting scope interface spec

## Purpose

The archive already has ignore-rule and namespace work.
What it still lacked was one ordinary page for the simpler question:

> does this exclusion rule mean the same thing on every relevant peer, and what local accounting changes is it actually responsible for?

Current official Resilio docs make this seam concrete.
They still distinguish local indexing/accounting effects from cross-peer agreement, and still leave matching-rule status under-owned.
That should compile to one stable product page.

## Core decision

AnonSync must expose one first-class **Rule agreement** page for every exclusion or omit rule that can plausibly be mistaken for shared system truth.

The page exists to answer six things in one place:

1. what rule family this is
2. what exact pattern or selector it uses
3. what scope it applies to locally
4. whether the relevant peers are ledger-equivalent
5. what counting/visibility changes it causes locally
6. what strongest safe sentence it earns

## Fixed page order

1. **Rule identity**
2. **Local scope and effects**
3. **Ledger equivalence**
4. **Safe language and forbidden upgrade**
5. **Jump pages and alternatives**

### 1) Rule identity

Show:

- `rule_agreement_page_id`
- display label
- rule family (`ignore`, `exclude`, `omit-from-counting`, `omit-from-publishing`, `mixed`, `unknown`)
- current rendered pattern
- strongest honest one-line summary

### 2) Local scope and effects

Show:

- selector semantics
- case / path / normalization assumptions
- local effects on indexing, counting, visibility, or transfer
- whether the rule is future-only, mixed, or blocked by residue

The operator must be able to answer:

> what does this rule actually do on this seat?

### 3) Ledger equivalence

Show:

- peer set under comparison
- exact equivalence verdict (`equivalent`, `compatible`, `ambiguous`, `drifted`, `unknown`)
- rule rows that differ
- whether OS or selector semantics could still make same-looking text mean different things

### 4) Safe language and forbidden upgrade

Show side by side:

- strongest safe sentence
- stronger forbidden sentence
- the residue or missing proof that blocks the upgrade

Example:

- safe: `this seat ignores matching PDF files for local indexing and size accounting`
- forbidden: `all peers will ignore matching PDF files the same way`

### 5) Jump pages and alternatives

Primary actions may include:

- `Open drift-class review`
- `Open rule retroactivity`
- `Copy safe sentence`
- `Open selector semantics`
- `Export rule receipt`

## Public object

### Rule agreement page

Fields:

- `rule_agreement_page_id`
- `rule_ref`
- `rule_family`
- `selector_snapshot`
- `local_effect_rows[]`
- `comparison_peer_set_ref`
- `ledger_equivalence_verdict`
- `drift_rows[]`
- `safe_sentence`
- `forbidden_sentence`
- `blocking_residue_rows[]`
- `jump_actions[]`
- `generated_at`
