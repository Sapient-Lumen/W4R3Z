# Deprecation, migration, and removal receipts

Systems don’t fail only by adding risky features; they also fail by **removing** things:
- silent ABI/API breaks
- “temporary compatibility flags” that never die
- undocumented drift where downstreams discover breakage first

DeriveBSD’s greenfield advantage is to bake in a *mechanical* lifecycle:
**introduce → deprecate → dual-run/migrate → remove**, with **diffable artifacts** and **receipts**.

## The stance

- **No silent removals** of:
  - kernel UAPI surfaces
  - contract interfaces
  - policy vocabulary (promise names, profile classes)
  - user-facing CLIs

- Deprecation must be:
  1) **declared** (a deprecation notice object),
  2) **discoverable** (shows in permission/diagnostics surfaces),
  3) **bounded** (time window or release window), and
  4) **actionable** (migration path + replacement ids).

## Deprecation notice as a first-class object

Introduce a small, stable artifact:

- `deprecation.notice`
  - describes what is becoming obsolete
  - declares replacement surface ids
  - encodes the end-of-life window
  - links to migration tooling and compat shims (if any)

Schema: `spec/deprecation.notice.schema.json`
Example: `spec/examples/deprecation.notice.json`

## How deprecation becomes reviewable drift

### 1) Contract/UAPI diffs
Contract and UAPI diffs should be able to link to notices.
Even before schemas include explicit fields, reviewers can:
- include the `deprecation.notice` digest in the change set
- require it in the design review rubric

Related:
- contract registries + diff gates: `docs/370-contract-registries-and-api-diff-gates.md`
- UAPI registry + compat gates: `docs/362-uapi-surface-registry-and-compat-gates.md`

### 2) Blast-radius diffs
Deprecations and removals are operational blast radius:
- “this generation removes X” is not a hidden detail

Greenfield advantage: treat deprecations as an optional section in `blast_radius.diff` so they show up in the same review surface as authority/UAPI/parser drift.

### 3) Receipts (so removals are auditable)
Removal should emit a receipt (usually as part of a change set receipt):
- which notice was satisfied
- which compat shims were removed
- which cohorts/hosts were affected

Related:
- change sets + receipts: `spec/change.set.schema.json`, `spec/change.receipt.schema.json`
- staged rollouts: `docs/258-staged-rollouts-and-cohorts.md`

## Recommended lifecycle patterns

### A) Dual-run / shadow mode (highest confidence)
Run v1 and v2 in parallel and compare outputs before cutover.
- best for policy engines, parsers, or data migrations

### B) Compat shims with strict expiration
If you ship a shim:
- bind it to a deprecation notice
- require a timeboxed expiration
- ensure it appears in authority and parser surfaces if it widens attack surface

### C) “Edition” boundaries (rare but useful)
If a family of breaking changes is large, introduce a named edition.
Treat “edition selection” like other policy decisions (typed, receipted).

## Design review rubric implications

Any change that breaks compatibility must include:
- a `deprecation.notice`
- a migration plan (tooling/tests)
- rollout plan (cohorts + fallback)

See: `docs/348-design-review-rubric-and-feature-intake.md`.

## References

- Kubernetes API Deprecation Policy (clear, explicit lifecycle expectations):
  - https://kubernetes.io/docs/reference/using-api/deprecation-policy/

Last updated: 2026-02-27r109
