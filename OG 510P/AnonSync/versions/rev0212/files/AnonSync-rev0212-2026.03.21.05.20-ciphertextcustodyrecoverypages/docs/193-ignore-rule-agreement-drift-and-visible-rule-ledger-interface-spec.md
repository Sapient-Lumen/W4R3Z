# Ignore-rule agreement, drift, and visible rule-ledger interface spec

## Purpose

The archive already had hidden-service-state, route, and value-provenance language.
What it still lacked was one explicit interface contract for a quieter but extremely common source of divergence:

> when some names are *not supposed to sync at all*, what page proves which ignore rules are in force, where they came from, whether peers agree, and whether old material still remains because the rule changed after the files were already indexed?

Current official Resilio docs make this seam much sharper than a generic `ignore patterns exist` statement would.
They still describe `IgnoreList` as a UTF-8 text file in the hidden `.sync` directory, note that ignored files are not indexed and do not count toward the main-view size total, warn that the file is case-sensitive and path-separator-sensitive, say the rule set can be edited by commenting out defaults or adding new rules, and separately admit in troubleshooting guidance that peers really need matching ignore behavior to agree on what should sync.
They also still say the ignore list does not retroactively affect files that already synced.

That is candid operational guidance.
It is still not a good public contract.

## Core decision

AnonSync should make **exclusion policy** first-class.

Every subject needs one visible rule ledger that declares:

- which include/exclude rules are active now
- where each rule came from
- whether the rule is inherited, local-only, temporary, or subject-wide
- whether peers are in policy agreement, tolerated drift, or unsafe disagreement
- whether the rule affects only future indexing or also triggers an explicit reclassify / purge / retain review for already-known material

If an operator still has to infer policy truth from a hidden sidecar file and peer-size mismatch, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal seven truths AnonSync should not clone:

- exclusion policy can still live as an editable hidden text file inside the subject tree
- the effective policy still depends on syntax details such as case sensitivity and OS-dependent delimiters
- size and index counts can diverge because exclusion is also an accounting decision
- troubleshooting guidance can still shift from `same list is advisable` to `peers must agree` without one visible contract that reconciles those statements
- rule changes can still be non-retroactive, which means the operator needs a second decision about already-known bytes
- default ignores are still product behavior even when the operator never consciously reviewed them
- drift can look like missing files, wrong size totals, or quiet disagreement rather than a typed policy incident

AnonSync should therefore keep one stronger rule:

> exclusion policy must be inspectable as policy, agreement state, and reclassification effect, not merely as a hidden parser input.

## Fixed review order

Every non-trivial ignore-policy action should render the same sections in the same order:

1. **Effective rule ledger now**
2. **Agreement and drift across members**
3. **Impact on already-known material**
4. **Receipt and replay promise**

### 1) Effective rule ledger now

This section should show:

- each active include/exclude rule in canonical normalized syntax
- provenance for each rule: product default, imported artifact, subject policy, local overlay, temporary override
- whether matching is case-sensitive, normalized, or target-profile dependent
- the namespace scope affected by the rule
- current estimate of objects and bytes hidden by the rule

The operator must be able to answer: **what is being excluded right now, and why?**

### 2) Agreement and drift across members

This section should show:

- which members apply the same rule ledger
- which members diverge
- whether divergence is tolerated because of local-only view policy or unsafe because it changes shared expectations
- any syntax portability issues that would make a rule behave differently on another target profile
- whether a rule mismatch currently explains size, count, or availability differences

The operator must be able to answer: **do all participants mean the same thing by "ignored"?**

### 3) Impact on already-known material

This section should show:

- whether the proposed rule touches only future indexing
- whether previously indexed material would remain present, become retained residue, become newly hidden, or require a separate cleanup review
- whether peer-visible deletes are implied or forbidden
- whether reindexing, reconciliation, or no-op is the honest next step

The operator must be able to answer: **what happens to bytes that are already known if I change this rule?**

### 4) Receipt and replay promise

This section should show:

- the canonical post-change rule ledger
- the members that accepted it
- the predicted and actual reindex / reclassify effects
- any unresolved drift that still requires review
- a replayable command/event representation for CLI and API parity

The operator must be able to answer: **what rule set actually took effect, and what did it change?**

## States

The surface should use a small stable vocabulary:

- `agreed` — all required members apply equivalent rule meaning
- `local variance` — divergence exists but is explicitly scoped to local view only
- `unsafe drift` — members disagree about what should sync or count
- `retroactive review required` — a rule edit affects previously known material and needs a second decision

## Main surface

The subject workspace should expose a **Rule ledger** card with:

- active rule count
- hidden object count and byte estimate
- agreement state badge
- a short sentence for the strongest provenance fact, e.g. `3 product defaults, 2 subject rules, 1 local temporary rule`
- a drill-in action: `Inspect rule ledger`

## Detailed surface

The detailed page should have five panes.

### Pane A — Rule table

Columns:

- rule
- type (`include`, `exclude`, `metadata only`, `local-only visibility`)
- provenance
- scope
- syntax profile
- matched objects

### Pane B — Agreement map

Per member:

- ledger version
- drift class
- last confirmed time
- any syntax warning

### Pane C — Impact simulator

Shows:

- future-only effect
- already-indexed effect
- count/size delta
- whether cleanup review is needed

### Pane D — Proposed edits

Supports:

- add rule
- disable inherited default
- narrow local-only overlay
- normalize syntax for target portability
- request full agreement repair

### Pane E — Receipts

Shows prior rule-ledger commits and their effects.

## CLI parity

Minimum commands:

- `anonsync rules show <subject>`
- `anonsync rules diff <subject> --member <id>`
- `anonsync rules simulate <subject> --add '<pattern>'`
- `anonsync rules apply <subject> --review <review-id>`

The CLI must show the same drift classes and retroactive-effect truth as the graphical surface.

## Non-goals

This spec does **not** define:

- rich content-classification policy for DLP or malware
- transport filtering
- archive/restore semantics for excluded files

It only defines how ordinary include/exclude policy becomes visible and reviewable.

## Acceptance criteria

A user can:

- inspect every active exclusion rule without touching hidden service files
- prove whether peers agree about exclusion semantics
- tell whether a rule change is future-only or requires retroactive review
- explain why share size/count differs because of policy instead of transport failure
- apply rule edits from GUI or CLI and get the same receipt
