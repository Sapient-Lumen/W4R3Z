# The surface registry pattern: keep drift gateable as the system grows

DeriveBSD needs to scale without turning review into archaeology.
A recurring lesson across OS ecosystems: the things that hurt later are **surfaces**:
- APIs (contracts)
- kernel UAPI
- parsers / decoders
- authority-bearing handles and brokers

Greenfield advantage: treat each important surface as a *first-class derived artifact*.

## The pattern

For any surface class we care about:

1) **Registry**: a canonical, typed inventory
   - stable ids
   - owners
   - risk tags
   - enforcement/fuzz/proof hooks

2) **Diff**: a machine-checkable delta between two registries
   - classification (new / removed / broadened / narrowed)
   - links to evidence (tests, fuzz receipts, proofs)

3) **Gate**: policy rules that decide if the diff is acceptable
   - can be strict in CI
   - can be looser for dev

4) **Receipt**: a durable explanation that the gate ran
   - what was evaluated
   - what rule allowed/denied
   - what evidence was attached

## Current instantiations

DeriveBSD already uses this pattern in multiple places:

- **Contracts (userland APIs)**
  - `spec/contract.registry.schema.json`
  - `spec/contract.diff.schema.json`
  - doc: `docs/370-contract-registries-and-api-diff-gates.md`

- **Kernel UAPI (syscalls/ioctls/sysctls/devnodes/pseudofs)**
  - `spec/uapi.registry.schema.json`
  - `spec/uapi.diff.schema.json`
  - doc: `docs/362-uapi-surface-registry-and-compat-gates.md`

- **Parsers (untrusted bytes → structured objects)**
  - `spec/parser.registry.schema.json`
  - `spec/parser.diff.schema.json`
  - doc: `docs/376-parser-surface-registry-and-fuzz-gates.md`

- **Crypto surfaces (protocols/suites/blessed libraries/key policies)**
  - `spec/crypto.registry.schema.json`
  - `spec/crypto.diff.schema.json`
  - doc: `docs/391-crypto-surface-registry-and-agility-gates.md`


- **Trust boundary drift (threat boundary changes)**
  - `spec/trust.boundary.graph.schema.json`
  - `spec/trust.boundary.diff.schema.json`
  - doc: `docs/380-trust-boundary-graphs-and-threat-diff.md`

- **Authority drift**
  - schema: `spec/authority.diff.schema.json`
  - doc: `docs/374-authority-diff-schema-and-review-workflows.md`

Blast-radius diffs are the “umbrella report” that can incorporate multiple surface diffs.
See: `docs/106-blast-radius-diff.md`, `spec/blast_radius.diff.schema.json`.

As the number of surfaces grows, review needs a *single attachment*.
DeriveBSD uses **drift bundles** (`drift.bundle`) to summarize and link all relevant diffs (including blast-radius).
See: `docs/395-drift-bundles-and-review-summaries.md`, `spec/drift.bundle.schema.json`.

Not everything is best represented as a registry: some diffs compare *whole sets* (e.g. closures).
`closure.diff` makes “new code ingestion” reviewable and can be included in drift bundles.
See: `docs/396-closure-diffs-and-new-code-surfaces.md`, `spec/closure.diff.schema.json`.

## When to mint a new registry

Use the pattern whenever a new feature introduces a surface that:
- can expand attack surface (new parser, new interpreter)
- can expand authority (new broker/handle kind)
- can break compatibility (new API, new kernel edge)
- is likely to accumulate “just one more knob” over time

## Suggested minimal fields (by convention)

These are not mandates, but they keep registries actionable:

- `id` (stable)
- `owner` (team/person)
- `risk` tags (eg. `untrusted-bytes`, `crypto`, `kernel-crossing`, `remote-input`)
- `evidence_hooks`
  - tests
  - fuzz targets
  - proof bundles (optional)
- `compat_policy` (if applicable)

## Meta-engineering rule

If a feature adds a new surface class, it must say:
- whether it fits an existing registry
- or why it needs a new registry/diff

This keeps “surface drift” from becoming a surprise.

See: `docs/348-design-review-rubric-and-feature-intake.md`.

Last updated: 2026-02-27r111
