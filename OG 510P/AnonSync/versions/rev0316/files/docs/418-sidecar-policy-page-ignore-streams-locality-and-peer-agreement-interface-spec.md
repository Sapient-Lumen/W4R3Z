# Sidecar policy page — ignore, streams, locality, and peer-agreement interface spec

## Purpose

The archive already had exclusion, metadata-stream, and policy-lineage work.
What it still lacked was one ordinary page for the simpler question:

> which hidden sidecar files currently shape what this subject indexes, counts, or preserves for metadata carriage, and are those sidecars local-only, aligned across peers, or drifting dangerously?

Current official Resilio docs make this seam concrete.
They still say IgnoreList lives in hidden `.sync`, that ignored files are not indexed or counted, that matching is case-sensitive, that peers may differ, that troubleshooting later treats ignore disagreement as a real cause of divergence, that StreamsList separately whitelists xattrs, and that xattrs cannot be ignored through IgnoreList.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Sidecar policy** page for every subject that supports hidden policy sidecars or carriage sidecars.

The page exists to answer five things in one place:

1. which sidecar families are active now
2. whether each sidecar is seat-local, subject-wide, imported, or temporary
3. what indexing, accounting, and fidelity consequences follow from the current entries
4. whether peer agreement is aligned, intentionally divergent, or risky
5. what reviewed edit would change the effective policy without forcing filesystem spelunking

## Fixed page order

1. **Current sidecar verdict**
2. **Active sidecar families**
3. **Rule locality and agreement**
4. **Accounting and fidelity effects**
5. **Reviewed mutation draft**

### 1) Current sidecar verdict

Show:

- `sidecar_policy_page_id`
- subject scope
- current `sidecar_verdict` (`baseline-only`, `custom-local`, `custom-shared`, `intentional-divergence`, `unsafe-drift`, `unknown`)
- strongest honest summary
- last materially sidecar-shaping event time

The operator must be able to answer:

> which hidden sidecars currently matter here?

### 2) Active sidecar families

Show rows such as:

- ignore / exclusion sidecar
- metadata carriage whitelist sidecar
- imported subject policy sidecar
- retired sidecar pending cleanup

Each row must show:

- source of truth
- dominant scope
- current entry count
- whether defaults were modified
- whether direct filesystem editing is disabled / discouraged / imported-only

### 3) Rule locality and agreement

Show:

- seat-local vs subject-wide classification
- peer-agreement state (`aligned`, `tolerated-divergence`, `unsafe-drift`, `unknown`)
- path / case / platform sensitivity warnings
- whether a rule affects future discovery only or also current accounting views

The page must answer:

> are peers actually agreeing on what counts and what carries metadata?

### 4) Accounting and fidelity effects

Show:

- excluded candidate count and bytes
- counted-size delta
- metadata-carriage delta
- xattr / alternate-stream portability warnings
- whether unsupported xattr storage is being carried through managed stubs instead

This section must make `not indexed`, `not counted`, and `metadata not carried` visibly different.

### 5) Reviewed mutation draft

Actions may include:

- `Edit ignore rules`
- `Edit metadata carriage whitelist`
- `Adopt shared baseline`
- `Preserve deliberate local divergence`
- `Open managed hidden bytes page`
- `Export sidecar receipt`

Each action must preview the policy delta, accounting delta, and non-effects.

## Public object

### Sidecar policy page

Fields:

- `sidecar_policy_page_id`
- `subject_ref`
- `sidecar_verdict`
- `sidecar_family_rows[]`
- `agreement_state`
- `accounting_delta`
- `metadata_carriage_delta`
- `unsupported_storage_fallback_rows[]`
- `draft_mutation_rows[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. subject
2. sidecar verdict
3. agreement state
4. dominant consequence
5. next least-widening action

Example:

```text
Project Alpha     intentional-divergence     ignore aligned / streams local     counted bytes differ, payload bytes unchanged     Open sidecar policy
```

## Non-goals

This page does **not** prove subject continuity, cleanup safety, or history restore results.
It proves only the live **sidecar policy** and the consequences of changing it.
