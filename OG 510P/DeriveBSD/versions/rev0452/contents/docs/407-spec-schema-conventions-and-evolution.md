# Spec schema conventions + evolution (keep artifacts legible)

**Tier:** A (Core meta-doc)  
**Profiles:** A, B, C, D  
**Pillars:** reproducibility, operability
**Patterns:** Registry→Diff→Gate  

DeriveBSD relies on **typed, digest-bound artifacts** (plans, receipts, registries, diffs).  
If schemas drift into a grab-bag of one-off shapes, tooling becomes bespoke and reviewers lose the ability to reason quickly.

This doc is a *style guide* for JSON schemas under `spec/` so:
- artifacts are mechanically greppable
- generic tooling (lint, diff, receipt chaining, bundle exporters) stays simple
- forward evolution is deliberate rather than accidental

See also:
- Pattern catalog: `docs/397-pattern-catalog.md`
- Surface registry meta-pattern: `docs/379-surface-registry-pattern.md`
- Drift bundles: `docs/395-drift-bundles-and-review-summaries.md`

## A. The “Plan → Receipt → Event” triad (preferred)

For any mutating operation that matters operationally, prefer the trio:
- `*.plan` — the **intent** (all steps explicit, policy decisions referenced)
- `*.receipt` — the **result** (what happened, why, and what was applied)
- `*.event` — the **stream** (structured emissions for monitoring/incident context)

If you only have time for one: define the `*.receipt` first.

## B. Required identity fields

### 1) `kind` is always constant
Every long-lived artifact schema should include a constant discriminator:
- `kind` must be a **single** value (prefer `const`, allow single-value `enum`).
- do not “reuse” a `kind` for a materially different meaning.

This enables:
- generic routers/parsers
- unambiguous storage, indexing, and evidence queries

### 2) Version fields are named after the artifact
Prefer explicit version fields over one generic `version`:
- `plan_version`, `receipt_version`, `event_version`
- `schema_version` for “structural” objects (diffs, registries, proofs)

Use `0.x` during early iteration.

### 3) Stable IDs + timestamps
Prefer:
- `*_id`: stable identifier (UUID recommended)
- `created_at` for plans/receipts
- `at` for events

## C. Common cross-cutting fields (keep them consistent)

These should be *spelled the same way* across artifacts when present:

- `requested_by`: opaque workflow/operator request id
- `target`: `{ host_id, domain }` (or equivalent subject selector)
- `plan_digest`: in receipts/events, a digest pointer to the plan
- `policy_decision_digest`: digest of the policy decision record used

If a subsystem needs extra knobs, prefer a nested `backend` object rather than sprinkling backend-specific fields at top level.

## D. Forward compatibility and “escape hatches”

DeriveBSD often uses `additionalProperties: false` for safety.
That’s fine, but **you still need an extension story**.

Recommended pattern:
- keep strict top-level fields
- add exactly one optional object for future growth, e.g.:
  - `extensions`: `{ "x_vendor": { ... } }` with `additionalProperties: true`

Rules:
- never change meaning of an existing field
- additive evolution: add new optional fields, keep old ones
- breaking evolution: new `kind` or bump major `schema_version` and ship a deprecation notice (`docs/385-deprecation-policies-and-removal-receipts.md`)

## E. Digest pointers (be explicit)

When referencing other evidence/artifacts:
- prefer `*_digest` fields that name **what** is being referenced
- avoid ambiguous `digest` at top level unless the schema is a generic ref

If the same object can be referenced in multiple encodings, include both:
- `digest` (canonical)
- `format` (or `encoding`) for interpretation

## F. Linting / tooling

To keep this from becoming “style by folklore”, the archive includes a lightweight schema linter:

- `python3 tools/lint_spec_schemas.py`

It checks for:
- valid JSON
- `$schema` + `title`
- expected conventions for `*.plan/*.receipt/*.event` schemas

It is intentionally small and mechanical: the goal is to catch copy/paste drift, not to enforce creativity out of the system.

Last updated: 2026-02-27r119
