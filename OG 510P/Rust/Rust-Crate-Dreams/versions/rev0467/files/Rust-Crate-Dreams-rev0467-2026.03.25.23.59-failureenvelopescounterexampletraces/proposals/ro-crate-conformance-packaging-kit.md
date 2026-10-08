---
id: P-0321
title: RO-Crate Conformance & Packaging Kit — profile-aware research-object bundles, JSON-LD sanity checks, and reproducible archival diffs
status: idea
domains: [research, metadata, ro-crate, json-ld, packaging]
last_reviewed: 2026-03-06
evidence:
  - https://www.researchobject.org/ro-crate/
  - https://www.researchobject.org/ro-crate/specification/1.2/index.html
  - https://www.researchobject.org/ro-crate/quick-reference
  - https://crates.io/crates/ro-crate-rs
  - https://docs.rs/ro-crate-rs/latest/rocraters/
  - https://www.biorxiv.org/content/10.64898/2026.01.22.701040v1
---

# Problem

RO-Crate is increasingly becoming the “simple, web-native package with metadata” answer for research and data-intensive workflows. Rust now has promising substrate, but the difficult part is not generating one more `ro-crate-metadata.json` file. The pain is in the missing middle:

- profile-specific expectations that drift,
- JSON-LD that is technically present but operationally broken,
- packaging changes that are hard to diff meaningfully,
- partial or stale crate updates during workflow handoff,
- and archival/reproducibility discussions that still rely on giant hand-curated zips.

The worthy Rust crate contribution is a **RO-Crate conformance and packaging kit** that makes crates profile-aware, diffable, and reproducible as long-lived artifacts.

# What it provides

- `rocrate-ir` — canonical IR for root dataset metadata, entities, contextual entities, file inventories, references, and packaging state.
- `rocrate-profile` — lockfiles for RO-Crate core version, profile overlays, required metadata surfaces, and packaging rules.
- `rocrate-verify` — semantic checks for identifier consistency, contextual-entity linkage, profile requirements, and packaging integrity.
- `rocrate-diff` — explainable diffs: “entity removed but still referenced”, “workflow profile fields missing”, “packaged file inventory diverged”, “metadata upgraded from 1.1 assumptions to 1.2”.
- `rocrate-pack` — deterministic packaging, inventory capture, and round-trip validation.
- `cargo rocrate` — emit `*.rocratebundle.zip` for workflow handoff, archival QA, and reproducibility reviews.

# What the crate should provide other people

1. **A boring-default verification and packaging layer** above raw RO-Crate JSON-LD editing.
2. **Profile lockfiles** that pin exact RO-Crate and overlay assumptions.
3. **Semantic archival diffs** that explain what changed in a crate, not just which bytes moved.
4. **Deterministic packaging and inventory capture** for reproducibility workflows.
5. **A bridge from today’s Rust RO-Crate library momentum to conformance-grade research-data tooling**.

# Users & user stories

- **Workflow / lab-automation teams**: “Verify that the packaged output still satisfies the profile we promised downstream consumers.”
- **Repository / archive operators**: “Diff two crates semantically before ingest.”
- **Research software engineers**: “Round-trip a crate through our pipeline and prove nothing important drifted.”
- **Standards/profile authors**: “Publish machine-checkable fixture packs for our RO-Crate profile.”

# Prior art (and why it’s insufficient)

- RO-Crate 1.2 is a stable community recommendation with quick-reference material that makes explicit requirements more machine-checkable.
- Rust now has a real RO-Crate library and a fresh research push around `ro-crate-rs`.
- But there is still no strong boring-default Rust layer for **profile pinning, semantic diffs, deterministic packaging, and shareable conformance bundles**.

# Design goals

1. **Profile-aware** — core RO-Crate and overlay profiles must both be first-class.
2. **Archival and workflow friendly** — fit handoff, publication, and reproducibility use cases.
3. **JSON-LD sane by default** — enough normalization and checking to catch real breakage without inventing a giant linked-data framework.
4. **Deterministic packaging** — package/inventory outputs should be reproducible.
5. **Library-first** — useful to CLIs, repositories, and workflow engines.

# Non-goals

- Not a giant repository platform.
- Not a full linked-data reasoner.
- Not a replacement for every domain-specific profile.

# Architecture & API sketch

```rust
pub struct RoCrateReport {
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub metadata_findings: Vec<MetadataFinding>,
    pub inventory_findings: Vec<InventoryFinding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn verify_crate(profile: &RoCrateProfile, input: &RoCrateInput) -> RoCrateReport;
```

Bundle draft: `profile.toml`, `crate/ro-crate-metadata.json`, `inventory.json`, `verdicts.json`, `diff.json`, `packaging.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Support redaction of sensitive file paths, tokens, PII-like metadata, and internal URLs.
- Keep inventory capture content-addressed where possible.
- Bound recursive traversal and package expansion.
- Record exact profile, verifier, and normalizer versions for long-lived archive evidence.

# Maintenance & governance plan

- Pin exact RO-Crate spec and profile assumptions in fixtures.
- Encourage synthetic/public examples and machine-checkable profile packs.
- Keep IR additive so domain-specific overlays can compose rather than fork the core.
- Prefer deterministic packaging conventions from day one.

# Milestones

## 0.1
- Canonical RO-Crate IR
- Profile lockfiles
- Semantic verification + bundle format

## 0.2
- Deterministic packaging/inventory checks
- Semantic diff engine
- Profile fixture packs

## 1.0
- Stable `*.rocratebundle.zip`
- Adapters for repositories, workflow engines, and Rust RO-Crate tooling
- CI-ready archival and handoff workflows

# Open questions

- How much JSON-LD normalization is enough before complexity explodes?
- Which packaging conventions should become the default versus optional overlays?
- Can profile composition stay simple enough for non-semantic-web users?

# Sources

- RO-Crate home: https://www.researchobject.org/ro-crate/
- RO-Crate 1.2 specification: https://www.researchobject.org/ro-crate/specification/1.2/index.html
- RO-Crate quick reference: https://www.researchobject.org/ro-crate/quick-reference
- `ro-crate-rs` crate: https://crates.io/crates/ro-crate-rs
- `ro-crate-rs` docs: https://docs.rs/ro-crate-rs/latest/rocraters/
- `ro-crate-rs` 2026 paper/preprint: https://www.biorxiv.org/content/10.64898/2026.01.22.701040v1
