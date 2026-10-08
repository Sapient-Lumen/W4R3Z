# Upgrade gate page — target line, config survival, and rollback honesty interface spec

## Purpose

The archive already had release posture and successor planning language.
What it still lacked was one ordinary page for the simpler question:

> if I cross this update boundary, what exactly survives, what may be lost, and is this really an upgrade, a cutover, or a reinstall with byte preservation?

Current official Resilio docs make this seam concrete.
They still say some unsupported crossings may keep files on disk while losing access to share configuration, and that supported procedures differ by installation lane.
That is useful truth.
It should not remain embedded in update instructions and FAQs.

## Core decision

AnonSync must expose one first-class **Upgrade gate** page before any boundary-crossing install or update is applied.

The page exists to answer five things in one place:

1. what current line and target line are involved
2. whether the move is supported, redirected, or blocked
3. what continuity is promised: bytes, config, identity, cohort cohesion
4. what rollback truth still survives
5. what exact cutover plan is required

## Fixed page order

1. **Boundary verdict**
2. **Current vs target comparison**
3. **Continuity survival matrix**
4. **Rollback and fallback honesty**
5. **Apply or stop actions**

### 1) Boundary verdict

Show:

- `upgrade_gate_page_id`
- source and target lines
- current `boundary_verdict` (`safe-update`, `safe-with-review`, `supported-cutover`, `blocked`, `redirect-required`, `unsupported-but-byte-preserving`, `unknown`)
- strongest honest summary
- review timestamp

The operator must be able to answer:

> what kind of boundary is this really?

### 2) Current vs target comparison

Show rows for:

- edition / family
- host-role support
- usage-class support
- linked-cohort implications
- install-lane implications
- required runtime stop / restart / reinstall behavior

This section must prevent `newer version available` from impersonating `safe same-line upgrade`.

### 3) Continuity survival matrix

Show one row each for:

- storage bytes
- subject configuration
- linked identity
- cohort uniformity
- listener / control surface continuity
- maintenance ownership

Each row must declare `preserved`, `preserved-with-revalidation`, `recreated`, `not-preserved`, or `unknown`.

### 4) Rollback and fallback honesty

Show:

- whether rollback is supported
- whether rollback preserves config or only bytes
- whether a fallback destination line exists
- what data or configuration export should happen first
- whether later reinstall is required regardless

The page must answer:

> if this goes badly or is simply unsupported, what is the least deceptive fallback?

### 5) Apply or stop actions

Actions may include:

- `Apply supported update`
- `Create cutover plan`
- `Export continuity bundle`
- `Move cohort together`
- `Stay on current line`
- `Stop — unsupported boundary`

Each action must preview continuity deltas and non-effects.

## Public object

### Upgrade gate page

Fields:

- `upgrade_gate_page_id`
- `subject_refs[]`
- `from_line`
- `to_line`
- `boundary_verdict`
- `comparison_rows[]`
- `continuity_survival_rows[]`
- `rollback_posture`
- `fallback_options[]`
- `apply_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. subject or cohort
2. from→to line
3. boundary verdict
4. strongest non-preserved truth
5. next honest action

Example:

```text
home-server cohort     v2-business → v3-personal     blocked     config not preserved     Stop — unsupported boundary
```

## Non-goals

This page does **not** replace package download choice or fine-grained post-upgrade feature diff.
It proves only **what continuity and risk truth attaches to this boundary crossing**.
