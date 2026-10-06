# Lint reports as first-class artifacts (make “quality” queryable)

DeriveBSD already treats builds, updates, and ops state as typed evidence.
A missing glue layer is: **tooling output**.

If `derive lint` or `derive validate` emits human text, it’s hard to:
- gate promotion
- diff quality across commits
- include “why did this fail?” in incident/support bundles
- feed LLM tooling without brittle scraping

This doc defines a single output object: `lint-report`.

## Stance

1) Lints are **structured outputs** (see `docs/87-structured-output-contract.md`).
2) Lints can be treated as **evidence objects** in the spine.
3) Any subsystem that becomes large enough should have a lint pass.

## The `lint-report` object

Schema: `spec/lint.report.schema.json`  
Example: `spec/examples/lint.report.json`

A `lint-report` is:
- produced by `derive lint --json`
- also produced by specific compilers (svcdb compiler, caproute linter, promise-profile linter)
- attachable to:
  - `change-receipt` (what lints ran during apply)
  - `boot.health.report` (gate inputs)
  - `incident.bundle` (bounded context)

## Lints we should bake-in early

### 1) Schema + closure
- all artifacts validate against schemas
- closure proof is complete, no missing inputs

### 2) Store invariants
- no post-build mutation
- digests match declared layouts

### 3) Capability graph lint
- dangerous edges (egress, observability, activation escrow) require explicit review

See: `docs/189-capability-graph-lint-and-viz.md`.

### 4) Service supervision lint
- `svcdb` graph is acyclic
- restart policies aren’t pathological
- service boundary intent is explicit (jail/microVM/contract)

See: `docs/214-service-supervision-health-as-evidence.md`, `docs/235-process-contracts-and-service-ownership.md`.

### 5) Promise profile lint (pledge/unveil ergonomics)
- promise declarations match dependencies
- escalation to “unsafe” promises is explicit

See: `docs/232-service-promise-profiles.md`.

## Meta: “contract tests” for the archive

A linter isn’t just for user configs.
We should lint the archive itself:

- all referenced files exist (`tools/check_consistency.py`)
- schema examples validate
- docs referenced by index exist

(These are the easiest ways to keep the archive small and sane.)

Last updated: 2026-02-25
