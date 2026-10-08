---
id: P-0344
title: netCDF + CF Conventions + OPeNDAP Interop & Evidence Kit — profile-pinned dataset validation, subset replay, and science-data compatibility bundles
status: idea
domains: [science-data, climate, geospatial, netcdf, cf, opendap, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://cfconventions.org/cf-conventions/cf-conventions.html
  - https://cfconventions.org/conventions.html
  - https://opendap.github.io/dap4-specification/DAP4.html
  - https://crates.io/crates/netcdf
  - https://crates.io/crates/readap
---

# Problem

Rust can increasingly read and write scientific arrays, but the real operational failures in Earth/climate/ocean data systems happen at the seam between **file metadata conventions and remote subset/query semantics**:

- netCDF files that open fine but violate CF assumptions in ways downstream tools cannot explain,
- OPeNDAP subset requests that return surprising shapes or metadata behavior,
- servers and clients that mostly agree until coordinate semantics, masks, or missing values get involved,
- and bug reports that still ship giant datasets rather than compact, reproducible subset bundles.

The worthy crate contribution is an **interop and evidence kit** that pins CF expectations, normalizes remote-access semantics, and makes science-data incompatibilities reproducible.

# What it provides

- `scidata-ir` — canonical IR for dimensions, coordinates, variables, attributes, masks/fill values, projections, and subset requests/responses.
- `scidata-profile` — lockfiles pinning CF version, required conventions, coordinate expectations, and DAP server/client assumptions.
- `scidata-verify` — normalized checks for CF metadata, coordinate behavior, missing-value semantics, and structural consistency.
- `scidata-replay` — deterministic replay for OPeNDAP subset requests and dataset snapshots.
- `scidata-diff` — semantic diffs such as “time coordinate no longer monotonic”, “fill value semantics changed”, or “subset response shape drifted”.
- `cargo scidata-evidence` — emit `*.scidatabundle.zip` for CI, data-provider debugging, and client/server interop issues.

# What the crate should provide other people

1. **A boring default for CF-aware validation** in Rust data pipelines.
2. **Remote-subset replay artifacts** that make OPeNDAP bugs reproducible.
3. **Semantic diffs** for dataset compatibility rather than raw file diffs.
4. **Profile pinning** for conventions that otherwise drift silently.
5. **A bridge between file-based and service-based workflows**.

# Persona / who it’s for

- Climate/ocean/earth-science platform engineers
- netCDF and OPeNDAP client authors
- Data-publishing teams
- QA teams maintaining interoperability suites

# Users & user stories

- **Data publisher**: “Tell me whether this dataset is syntactically fine but CF-incompatible in ways that will break clients.”
- **Client author**: “Replay the exact OPeNDAP subset bug without downloading the full dataset.”
- **Research platform engineer**: “Diff two releases semantically, not just by bytes.”
- **QA lead**: “Pin the exact CF and DAP expectations for this integration test.”

# Prior art (and why it’s insufficient)

- The CF Conventions project publishes the conventions and a conformance/checker surface.
- OPeNDAP publishes DAP documentation and current DAP4 specifications.
- Rust has real substrate in `netcdf`, `netcdf-src`, `readap`, and adjacent ecosystem tools.
- But Rust still lacks a shared **CF-aware validation + subset replay + semantic diff + evidence bundle** layer.

# Design goals

1. **Convention-first** — arrays are not enough; metadata semantics must be first-class.
2. **Subset reproducibility** — remote bugs should become small bundles, not full-data transfers.
3. **Semantic diagnostics** — explain compatibility failures in coordinate/metadata terms.
4. **File/service continuity** — the same IR should describe local netCDF and remote OPeNDAP flows.
5. **Implementation neutrality** — useful across Rust, Python, Java, and legacy science stacks.

# MVP surface

- Minimal types: `DatasetSnapshot`, `SubsetRequest`, `SubsetResponse`, `SciDataProfile`, `SciDataReport`
- Minimal functions:
  - `load_netcdf()`
  - `verify_cf()`
  - `fetch_subset()`
  - `replay_subset()`
  - `diff_datasets()`
  - `write_bundle()`
- Feature flags:
  - `netcdf`
  - `cf`
  - `opendap`
  - `serde`

# Compatibility story

- MVP targets CF-aware local netCDF validation plus OPeNDAP replay for small subset queries.
- It should complement `netcdf` and `readap`, not replace them.
- It intentionally avoids becoming a full visualization or large-scale catalog platform.

# Conformance & fixtures

- Tiny public-domain climate/ocean fixtures with clear CF metadata.
- Known-invalid metadata cases for coordinates, standard names, bounds, and fill values.
- OPeNDAP subset replay fixtures with expected shapes/attributes.
- Golden diff cases for variable renames, coordinate drift, and missing-value behavior.

# Path to boring stability

- Stabilize the metadata/coordinate IR before adding complex service behaviors.
- Keep remote replay small and deterministic.
- Hash profile packs and checker versions into every bundle.
- Treat semantic findings vocabulary as the core compatibility API.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A CLI and library that open a small netCDF dataset, run CF checks under a pinned profile, replay one or two OPeNDAP subset requests, and emit a compact `*.scidatabundle.zip` with normalized findings and semantic diffs.

# De-risk plan

1. Start with tiny public fixtures and synthetic subset cases.
2. Reuse existing CF checker semantics where possible instead of inventing new rules.
3. Keep remote replay metadata-first at first.
4. Add more science-domain overlays only after the CF core is boring.

# Non-goals

- Not a plotting or dashboard library.
- Not a full catalog/search platform.
- Not a high-performance distributed array engine.

# Architecture & API sketch

```rust
pub struct SciDataReport {
    pub profile_id: String,
    pub cf_findings: Vec<Finding>,
    pub subset_findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn verify_cf(profile: &SciDataProfile, dataset: &DatasetSnapshot) -> SciDataReport;
pub fn replay_subset(profile: &SciDataProfile, request: &SubsetRequest) -> Result<SubsetResponse>;
```

Bundle draft: `profile.toml`, `dataset-metadata.json`, `subset-requests/`, `subset-responses/`, `findings.json`, `semantic-diff.json`, `notes.md`.

# Security / safety model

- Default to metadata and tiny subset capture rather than full-data duplication.
- Record exact checker/profile/server versions when known.
- Guard remote replay against unbounded fetches.
- Hash any embedded sample data and keep samples small.

# Maintenance & governance plan

- Keep the core limited to IRs, profiles, and normalized findings.
- Version CF profile packs and remote adapter packs separately.
- Prefer public-domain or license-clear fixtures.
- Add domain-specific conventions only as optional overlays.

# Milestones

## 0.1
- local netCDF snapshot loader
- CF profile and findings vocabulary
- tiny bundle format

## 0.2
- OPeNDAP subset replay
- semantic diffs
- checker adapters

## 1.0
- stable `*.scidatabundle.zip`
- public fixture corpus
- CI-ready profile packs

# Open questions

- How much of CF checking should be delegated to external validators versus native Rust checks?
- Should OPeNDAP replay stay metadata/shape-first forever, or eventually support sampled payload evidence?
- Which optional conventions belong in core versus add-on packs?

# Sources

- CF Conventions: https://cfconventions.org/cf-conventions/cf-conventions.html
- CF conformance/checker surface: https://cfconventions.org/conventions.html
- DAP4 specification: https://opendap.github.io/dap4-specification/DAP4.html
- `netcdf`: https://crates.io/crates/netcdf
- `readap`: https://crates.io/crates/readap
