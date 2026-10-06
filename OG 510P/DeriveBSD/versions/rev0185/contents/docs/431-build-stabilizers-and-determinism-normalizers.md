# Build stabilizers and determinism normalizers (optional lane)

**Tier:** C (Optional lane)
**Profiles:** A, B, C, D
**Pillars:** reproducibility, supply-chain, operability
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate, Bundles

Some ecosystems distinguish between:

- **proving** reproducibility (variation testing + deep diffs), and
- **improving** reproducibility by applying **explicit, reviewable normalizations**.

This doc captures a conservative DeriveBSD shape for that second idea: *stabilizers*.

A stabilizer is a deterministic transformation that reduces nondeterminism **without becoming an implicit input**.
If a stabilizer is used, it must be:
- explicitly selected by policy,
- recorded as evidence, and
- bounded by an “equivalence class” contract so it cannot silently hide meaningful drift.

This is **optional** by default: many profiles should prefer “fix the build” over “normalize the output.”

## Why this matters

- **Reproducibility pillar:** reduces “mostly reproducible but flakes on one timestamp/path” tail risk.
- **Supply-chain pillar:** makes normalization steps explicit, reviewable, and attributable (no folklore).
- **Operability pillar:** if a build differs, reviewers can see whether a stabilizer was applied and *what it changed*.

## Tier + profile posture

- **Tier C lane**: `build.stabilizers` (off by default).
- **Profile D (appliance/regulatory)** may choose to require this lane for specific classes (e.g., metadata-only normalization) to keep rebuildability stable over long horizons.
- **Profiles A/B/C** can enable it selectively for high-volume ecosystems where upstream determinism fixes are slow.

## The DeriveBSD shape

### 1) Stabilizers are policy-selected (never ambient)

Policy decides which stabilizers are allowed for a given build, and under what conditions:

- stabilizer id
- allowed stages: `env` / `input` / `output`
- allowed equivalence class (what changes are permitted)
- required evidence hooks (diff reports, witness rebuilds)

This keeps “normalization” from becoming an invisible impurity.

### 2) Every application yields a typed receipt

When the lane runs, it emits a **typed receipt**:

- `build.stabilizer.receipt` (schema: `spec/build.stabilizer.receipt.schema.json`)

The receipt must record:
- which stabilizers were requested vs applied,
- versions/config digests,
- a compact effect summary (and a log digest for deep diffs),
- a policy digest (so reviewers know which rule allowed it).

### 3) Stabilizers are a registry-backed surface (gateable)

Treat stabilizer ids as a small **registry**:
- ids are stable,
- definitions are crisp (what they do; what they must not do),
- adding a new stabilizer is a review event.

This is a direct application of **Registry→Diff→Gate**.

### 4) Wire into drift bundles and support bundles

Receipts should be attachable to:
- drift bundles (promotion review surface)
- deterministic exports / support bundles (forensics UX)

This keeps “why did this build match?” explainable.

## What counts as a stabilizer?

Prefer stabilizers that are:
- narrow (fix one known nondeterminism class),
- deterministic, and
- auditable via diffs.

Examples in other ecosystems:
- a policy-driven `SOURCE_DATE_EPOCH` discipline (time normalization)
- targeted “strip nondeterminism” passes over known metadata fields

Avoid:
- “magic” normalization that changes semantics,
- anything that depends on network/time/randomness,
- large transform pipelines that would be better as upstream fixes.

## References (primary)

- OSS-Rebuild stabilizers (normalization helpers for functional equivalence testing): https://docs.oss-rebuild.dev/stabilizers/
- Reproducible Builds: SOURCE_DATE_EPOCH (time normalization convention): https://reproducible-builds.org/docs/source-date-epoch/
- Debian strip-nondeterminism project (targeted metadata normalization): https://salsa.debian.org/reproducible-builds/strip-nondeterminism

Last updated: 2026-02-27r147
