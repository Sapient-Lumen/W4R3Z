# Frontier salience snapshot — 2026-03-19 (75)

This pass did **not** add another semver checker, another public-API diff engine, or another generic docs-coverage dashboard.
It sharpened a neglected but highly leverageable release-support lane:

- **P-0483 Public API Readiness Bundle Kit** — because Rust now has real semver/public-surface/public-dependency substrate, but still lacks one boring release-review contract for public-surface truth, boundary drift, docs readiness, and waiver posture.

## Main judgment

The next worthy move here was **not** another analyzer.
That substrate already exists.

The sharper missing layer is the **joined public-release review contract** above today’s substrate, especially once four facts are kept explicit:

- **public-surface truth** — what the crate actually exports publicly,
- **boundary truth** — which dependencies crossed into that surface,
- **docs-readiness truth** — what docs/example debt matters to that surface rather than to the whole repository,
- **waiver truth** — what intentional breaks or accepted debt still carry the release.

That move is better grounded now because:

- the 2026 Rust flagship goals explicitly group **control over public API dependencies** and **breaking change detection** in one supply-chain track;
- the 2025H2 semver-checks goal still describes unresolved blocker work before Cargo integration;
- `cargo-public-api` is now mature enough to list and diff public items against releases and commits;
- `cargo-semver-checks` now has witness-generation vocabulary, but still rides unstable rustdoc JSON;
- Cargo’s `public-dependency` work has real CLI and metadata surfaces (`cargo add --public`, `cargo tree --edges public`, `cargo metadata` inclusion);
- rustc already explains the `exported_private_dependencies` contract;
- and rustdoc already exposes machine-readable JSON and coverage JSON, though still on unstable footing.

So the gap is no longer “Rust lacks API analyzers.”
The gap is that teams still rarely get a **reviewable public-release promise** above those analyzers.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually use?”
2. **P-0525 Crate Diagnosis Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0524 Crate Example Surface Pack Kit** — still one of the highest-leverage first-success lanes.
4. **P-0520 Crate Lifecycle Surface Pack Kit** — still a strong product-level support surface.
5. **P-0484 Toolchain & Target Support Contract Kit** — still crucial for real machines and real targets.
6. **P-0483 Public API Readiness Bundle Kit** — now promoted because the analyzers beneath it are real, but the joined release-decision artifact is still weak.
7. **P-0472 Docs.rs Build Parity & Evidence Kit** — still a sharp hosted-build support lane.
8. **P-0027 text-input-kit** — still one of the clearest end-user product-engineering opportunities.
9. **P-0087 UI Accessibility Doctor Kit** — still a strong authoring-side semantic-quality lane.
10. **P-0515 Crate Off-Ramp Pack Kit** — still one of the clearest survivability / supportiveness follow-ons.
11. **P-0071 MCP Guard Kit** — still a strong modern protocol/deployment-support lane.
12. **P-0012 Desktop ShipKit** — still a strong desktop release/adoption lane.
13. **P-0197 Text Layout & Shaping Conformance Kit** — still a strong cross-stack correctness lab.
14. **P-0466 Python Wheel ABI & Free-Threading ShipKit** — still one of the clearest foreign-package shipping-contract opportunities.
15. **P-0168 Rust Android Mobile Kit** — still a strong mobile/library-shipping lane.
16. **P-0206 Wasm Component Contract & Conformance ShipKit** — still one of the clearest Wasm contract opportunities.

## Why this won over adjacent candidates right now

- It beat a deeper **P-0244** pass because semver evidence is necessary but still narrower than the full release-review bundle.
- It beat a deeper **P-0431** pass because public/private dependency boundary work is necessary but still narrower than release readiness.
- It beat another **generic docs-quality** pass because docs debt only becomes strategically important here when it is joined to the shipped public contract.
- It beat another **foreign-package shipping** pass because the archive needed a stronger core library/release-support candidate in the top band.

## What changed in the archive

Added:
- `entries/2026-03-19-255.md`
- `meta/frontier-salience-2026-03-19-75.md`
- `meta/public-api-readiness-product-plan-2026-03-19.md`
- `meta/public-api-readiness-lanes-2026-03-19.md`
- `fixtures/public-api-readiness-bundle-kit/public-surface.snapshot.schema.json`
- `fixtures/public-api-readiness-bundle-kit/semver-verdict.report.schema.json`
- `fixtures/public-api-readiness-bundle-kit/public-dependency-boundary.report.schema.json`
- `fixtures/public-api-readiness-bundle-kit/docs-readiness.report.schema.json`
- `fixtures/public-api-readiness-bundle-kit/waiver-ledger.receipt.schema.json`
- `fixtures/public-api-readiness-bundle-kit/release-readiness.verdict.schema.json`
- `fixtures/public-api-readiness-bundle-kit/scenarios/patch_release_accidental_public_dependency_leak/`
- `fixtures/public-api-readiness-bundle-kit/scenarios/minor_release_public_docs_regression/`
- `fixtures/public-api-readiness-bundle-kit/scenarios/intended_major_break_with_stale_waiver/`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/public-api-readiness-bundle-kit.md`
- `meta/known-existing.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `fixtures/public-api-readiness-bundle-kit/README.md`
- `meta/frontier-salience-2026-03-18-60.md`
- `meta/frontier-salience-2026-03-18-61.md`
- `meta/frontier-salience-2026-03-18-62.md`
- `meta/frontier-salience-2026-03-18-63.md`
- `meta/frontier-salience-2026-03-18-64.md`
- `meta/frontier-salience-2026-03-18-65.md`
- `meta/frontier-salience-2026-03-18-66.md`
- `meta/frontier-salience-2026-03-18-67.md`
- `meta/frontier-salience-2026-03-18-68.md`
- `meta/frontier-salience-2026-03-19-69.md`
- `meta/frontier-salience-2026-03-19-70.md`
- `meta/frontier-salience-2026-03-19-71.md`
- `meta/frontier-salience-2026-03-19-72.md`
- `meta/frontier-salience-2026-03-19-73.md`
- `meta/frontier-salience-2026-03-19-74.md`

## What this pass deliberately did not do

It did **not** collapse:

- semver-break evidence,
- public/private dependency boundaries,
- docs/example readiness,
- item-level cfg availability,
- and release-waiver posture

into one fake “API quality score.”
