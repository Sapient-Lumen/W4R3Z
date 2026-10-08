# Crate Knowledge Pack intake & materialization plan — 2026-03-24

This note deepens **P-0536 Crate Knowledge Pack Kit** around one product question:

> after a basis lock exists, how does the knowledge-pack crate import the underlying materials, materialize a reviewable bundle, and keep all ceilings visible?

## Main judgment

The sharper missing layer for **P-0536** is no longer “more ways to summarize docs”.
It is a boring, explicit answer to **intake** and **materialization**.

That is what makes the crate useful to:
- pathfinder,
- policy/CI,
- offline reviewers,
- recheck operators,
- and assistants that must stay pinned to a frozen basis.

## Why now

Current upstream substrate is finally rich enough to justify a real intake/materialization module:
- `cargo metadata` gives a versioned workspace/dependency graph surface,
- Cargo JSON messages expose produced artifacts and build-script results,
- the registry index provides immutable-per-version records except for `yanked`,
- `cargo package` gives a packaged-state witness plus `.cargo_vcs_info.json` with explicit provenance caveat,
- docs.rs exposes build metadata and rustdoc JSON,
- docs.rs download archives provide a processing input for offline review even though they are not directly usable offline docs,
- and build-analysis work suggests Cargo itself is becoming friendlier to persisted machine-readable historical data.

## Product shape

`P-0536` should grow five explicit modules:

### 1. `knowledge-intake`
Imports source materials without flattening their route differences.

First adapters:
- `cargo metadata --format-version` output
- Cargo JSON message stream
- registry index entry / sparse record import
- docs.rs metadata import
- docs.rs rustdoc JSON import
- docs.rs download archive import
- `cargo package` / `.cargo_vcs_info.json` import

Core output:
- `intake.receipt.json`

### 2. `knowledge-materialize`
Turns imported materials into reviewable local artifacts without pretending every surface is equally portable.

Core output:
- `materialization-plan.json`

### 3. `knowledge-cite`
Binds materialized artifacts back to stable-enough locators and claim traces.

This should reuse the archive’s existing citation-locator and item-witness discipline.

### 4. `knowledge-pack`
Builds the compact review bundle another team receives.

This is still the main product surface.
The difference is that it now depends on explicit intake/materialization artifacts instead of ad hoc import code.

### 5. `knowledge-recheck`
Reopens prior packs against changed materials while preserving historical basis.

This is the seam where **P-0535** and **P-0536** meet.

## First-class artifacts

### `intake.receipt.json`
Must say:
- source surface (`cargo_metadata`, `registry_index`, `docsrs_rustdoc_json`, `docs_download_archive`, etc.),
- acquisition mode (`local_command`, `pinned_url`, `redirected_url`, `supplied_file`, `downloaded_archive`, `manual_entry`),
- whether the import was pinned before or after resolution,
- which caveats came with the source,
- and whether manual review is required.

### `materialization-plan.json`
Must say:
- which imported materials were transformed,
- intended review use (`citation`, `search`, `offline_reading`, `diff`, `task_fit`),
- what still depends on live remote assets,
- which targets or routes were preserved,
- and which ceilings remain.

## What the crate should provide other people

For another team, this crate should provide:

1. a reviewable import ledger,
2. one honest plan for what was materialized locally,
3. one compact bundle for search/review/assistant use,
4. one visible list of ceilings and manual-review zones,
5. and enough route detail to reopen the same basis later.

That is much more useful than “here is some generated JSON” or “here is a nice summary of the docs”.

## First-release scenarios worth shipping

A worthy `0.1` should handle at least these:

### Scenario A — pinned docs.rs review bundle
Import pinned docs.rs metadata plus rustdoc JSON for a specific version and target, then emit a compact review bundle.

### Scenario B — latest docs.rs route resolved into a frozen basis
Start from a convenient `latest` docs.rs route but emit one intake receipt showing the resolved pinned version.

### Scenario C — docs.rs download archive materialization
Import a docs.rs download archive and emit a materialization plan that keeps target-layout, static-root, and missing toolchain-asset caveats visible.

### Scenario D — registry-index versus cargo-metadata differences
Import both surfaces without silently normalizing alias names, feature map differences, or renamed dependency fields.

### Scenario E — package witness with provenance ceiling
Import `.cargo_vcs_info.json` but keep its “best effort / not verified provenance” limit visible.

## Non-goals

`P-0536` should **not** become:
- a general internet crawler,
- a docs mirror service,
- a provenance verifier,
- a full offline docs portal,
- or a giant data warehouse.

It should stay focused on **compact, replayable, reviewable crate knowledge**.

## First usable release contract

A first usable release counts as successful when a downstream team can:
1. import a frozen basis,
2. materialize a review bundle for another person,
3. keep docs/download/provenance caveats visible,
4. cite the bundle later,
5. and reopen review without rebuilding the world.

If it cannot do that, it is still missing the product core.

## Sources

- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/reference/registry-index.html
- https://doc.rust-lang.org/cargo/commands/cargo-package.html
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/download
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
