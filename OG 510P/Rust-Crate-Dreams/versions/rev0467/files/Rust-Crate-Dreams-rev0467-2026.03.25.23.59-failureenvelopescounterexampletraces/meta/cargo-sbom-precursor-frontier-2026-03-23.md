# Cargo SBOM precursor frontier — 2026-03-23

This note deepens **P-0125 Cargo SBOM Precursor Workbench Kit** around one receiver-facing question:

> when a team says “we captured Cargo SBOM precursor evidence for this build”, what exactly was eligible for coverage, how was it discovered, and where do the honest claim ceilings stop?

## Main judgment

The current Cargo substrate is now strong enough that the next missing layer is **not** another format emitter.
It is a support contract for:

1. **capture route** — direct build, imported target tree, imported artifact-dir copy, imported bundle, or manual reconstruction;
2. **artifact coverage** — which outputs were eligible for precursor generation and which were merely adjacent Cargo artifacts;
3. **claim ceilings** — where copied outputs, imported trees, fresh-cache reuse, or non-linkable outputs fence the strongest honest claim;
4. **portable review bundles** — one handoff another team can inspect later.

## Why now

Current official docs make the seam reviewable instead of folkloric:

- Cargo SBOM precursor files are generated only for executable and linkable outputs uplifted into target/artifact directories.
- `CARGO_SBOM_PATH` creates a direct capture route that should outrank filename scans.
- `compiler-artifact` messages expose filenames, executable paths, and `fresh` status even when rustc was not executed.
- `--artifact-dir` turns copied promoted outputs into an explicit output lane.

These facts are enough to produce false confidence unless the archive insists on route + coverage + ceiling artifacts.

## Product stance

A worthy crate here should be:

- **Cargo-native** rather than metadata-only reconstruction,
- **route-honest** rather than directory-scan-magical,
- **coverage-explicit** rather than “found some sidecars”,
- **ceiling-aware** rather than “SBOM captured successfully”.

## New first-class review objects

### `capture-route.receipt.json`
Records:
- whether the bundle came from one direct invocation, imported target tree, imported artifact-dir copy, imported bundle, or manual reconstruction,
- which discovery sources were used (`compiler_artifact_stream`, `cargo_sbom_path_env`, `target_dir_scan`, `artifact_dir_scan`, `manual_mapping`),
- whether same-invocation capture can be claimed,
- and whether fresh-cache reuse or imported state limits stronger claims.

### `artifact-coverage.report.json`
Records for each relevant output:
- target kind / crate type hints,
- whether Cargo’s documented precursor surface makes it eligible,
- whether a precursor was directly observed,
- whether the observation came from exact stream/env correlation or imported filesystem evidence,
- and whether a missing precursor is a bug, an import gap, or simply out of scope.

### `coverage-ceiling.report.json`
Records the strongest honest limitations such as:
- non-linkable / non-uplifted outputs remaining outside the precursor surface,
- imported output trees not proving same-invocation generation,
- copied artifact-dir exports not by themselves proving complete retention,
- and fresh-cache reuse meaning “artifact was reported” is not equivalent to “precursor was regenerated now”.

### `sbom-workbench-bundle.manifest.json`
Joins the earlier capture lock / ingest / normalized graph / transform reports with the new route, coverage, and ceiling artifacts so downstream tools receive one portable packet.

## Non-goals

- not a replacement for general sidecar attachment contracts,
- not publish identity or registry-protection review,
- not full provenance attestation,
- not VEX adjudication or vulnerability intelligence.

## Sources

- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://doc.rust-lang.org/cargo/reference/unstable.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/CHANGELOG.html
