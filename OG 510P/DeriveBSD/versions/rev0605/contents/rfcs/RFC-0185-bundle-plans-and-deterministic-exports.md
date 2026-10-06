# RFC-0185: Bundle plans and deterministic exports

Status: Draft

## Problem

Causality graphs and redaction transforms exist, but the **selection + transform** decisions that produce an exported bundle
are not a typed object. That forces operators into scripts and makes sharing hard to audit.

## Goals

- Make `bundle-min` reproducible and reviewable.
- Bind exports to a plan (selection), a policy (what is allowed), and a receipt (what happened).

## Proposal

1) Add `bundle.plan`:
   - causal graph digest(s)
   - include toggles and time bounds
   - chosen redaction transform digest
   - chosen export policy digest

2) Update incident bundle workflows to optionally reference bundle plans.

3) Make `export.receipt` cite the plan digest when exporting a bundle.

References:
- `docs/253-bundle-plans-and-deterministic-exports.md`

