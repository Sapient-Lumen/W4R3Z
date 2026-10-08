# Public API readiness product plan — 2026-03-19

This note exists to keep **P-0483 Public API Readiness Bundle Kit** disciplined.
The archive already decided that the missing value is a **joined release-review artifact** above today’s analyzers.
This pass answers a narrower question:

> If somebody actually started building **P-0483** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps library maintainers publish one reviewable answer to:

- what the public surface actually is,
- how that surface changed,
- which dependencies crossed into that surface,
- what docs/example debt matters for that surface,
- which semver breaks are evidence-backed versus inferred,
- and which waivers or intent declarations are still carrying the release.

It should **not** try to become a replacement semver checker, a new public-API diff engine, or a giant docs platform.
Those are adjacent imports, not the product.

## Why this lane is sharper in 2026

Current Rust substrate is finally strong enough that the missing value is the bundle above it:

- the 2026 Rust flagship goals explicitly group **control over public API dependencies** and **breaking change detection** under supply-chain work,
- the 2025H2 goals still describe ongoing blocker work before `cargo-semver-checks` can merge into Cargo,
- `cargo-public-api` is mature enough to list and diff public items against releases and commits,
- `cargo-semver-checks` now exposes witness-generation vocabulary but still depends on unstable rustdoc JSON,
- Cargo’s `public-dependency` support is real enough that `cargo add --public` / `--no-public` and `cargo tree --edges public` are moving,
- rustc already exposes the `exported_private_dependencies` lint,
- and rustdoc already has machine-readable coverage JSON and experimental JSON output.

That means the missing crate is no longer “one more analyzer.”
The missing crate is the **boring review contract** that joins them.

## What the crate should provide other people

For maintainers and reviewers, the crate should provide:

1. **A boring release bundle** instead of five unrelated tool outputs.
2. **Fact provenance honesty** for what was measured locally, imported from another tool, or inferred conservatively.
3. **Public-surface narrowness** so docs debt or dependency drift only matter when they touch the shipped public contract.
4. **Waiver visibility** so intentional major breaks, temporary docs debt, and accepted ambiguity do not disappear into PR comments.
5. **Diffable release posture** so reviewers can see when a crate’s public contract grew faster than its changelog implies.
6. **Manual-review boundaries** whenever semver, docs, or public-dependency facts remain ambiguous.

For ecosystem tooling, the crate should provide:

1. one compact schema for public-release review,
2. import paths for existing semver/public-API tools,
3. stable bundle objects that can be archived in CI,
4. and a release-gate vocabulary that stays understandable outside the original team.

## Recommended `0.1` command surface

### `cargo api-ready capture`
Capture one release-review bundle.
This should:

- record the crate/workspace subject,
- import or compute a public-surface snapshot,
- import semver verdicts,
- import or compute public-dependency boundary facts,
- import docs/example coverage for the public surface,
- apply waiver policy,
- and emit a bundle.

### `cargo api-ready diff <old> <new>`
Compare two bundles and classify:

- `public_surface_changed`
- `public_dependency_boundary_changed`
- `docs_surface_regressed`
- `semver_verdict_changed`
- `waiver_posture_changed`
- `manual_review_required`

### `cargo api-ready gate`
Render a short verdict for release review:

- `ready`
- `ready_with_waivers`
- `manual_review_required`
- `not_ready`

### `cargo api-ready explain <item-or-dep>`
Explain why an item or dependency matters to the public contract and which evidence classes support that claim.

### `cargo api-ready pack`
Emit one compact archive for PR review, release signoff, or downstream support.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `api_ready_model`
  - Rust types for bundles, reports, waivers, and diffs
- `api_ready_public_surface`
  - imports from `cargo-public-api` and public-item normalization
- `api_ready_semver`
  - imports from `cargo-semver-checks` and witness/verdict normalization
- `api_ready_public_deps`
  - public/private dependency facts and ambiguity reporting
- `api_ready_docs_surface`
  - public-surface docs/example coverage import and normalization
- `api_ready_gate`
  - policy evaluation, waiver handling, and diffing
- `cargo-api-ready`
  - CLI / cargo-subcommand surface

Optional adapters should stay optional until the bundle schema is trusted:

- `api_ready_rustdoc_json`
- `api_ready_docsrs`
- `api_ready_ci`

## `0.1` artifact set

The first trustworthy shape should revolve around these files:

- `public-surface.snapshot.json`
- `semver-verdict.report.json`
- `public-dependency-boundary.report.json`
- `docs-readiness.report.json`
- `waiver-ledger.receipt.json`
- `release-readiness.verdict.json`
- `api-ready.diff.json`
- `api-ready-summary.md`

The key move in this pass is to make six first-class review objects explicit:

1. **public-surface snapshot** — what the crate claims publicly right now,
2. **semver verdict report** — which breakage findings are imported, witnessed, or uncertain,
3. **public-dependency boundary report** — what dependencies are part of the public contract,
4. **docs-readiness report** — what documentation/example debt matters specifically for that surface,
5. **waiver ledger** — what intent/exception posture exists and when it expires,
6. **release-readiness verdict** — the compact joined answer another reviewer can act on.

## Evidence classes

`0.1` should force the crate to keep evidence classes separate.

### Measured
Facts computed directly by the crate or a trusted imported tool on this run.
Examples:

- public-item inventory,
- docs/example coverage numbers,
- imported semver report IDs,
- dependency edges marked public/private.

### Imported
Facts imported from another tool or stored artifact.
Examples:

- `cargo-semver-checks` JSON or witness output,
- `cargo-public-api` output,
- rustdoc coverage JSON,
- historical previous-release bundle.

### Inferred
Conservative glue logic.
Examples:

- a dependency that is likely public because public items expose its types,
- docs debt that is likely release-relevant because it attaches to changed items,
- release readiness that becomes `manual_review_required` because evidence classes conflict.

The bundle should never blur these.

## Proving-ground archetypes

A worthy first implementation should prove itself against at least five archetypes:

1. **Patch release, no public-surface drift**
   - ensure the bundle stays boring
2. **New public dependency leaked through reexport**
   - show boundary expansion clearly
3. **Minor API expansion with docs/example regression**
   - keep docs debt narrow to the public surface
4. **Intended major break with explicit waiver**
   - separate acceptable intent from unreviewed breakage
5. **Conflicting signals across analyzers**
   - escalate honestly to manual review

If `0.1` cannot survive those five, the product vocabulary is still too narrow.

## Adoption staircase

### Stage 1 — import and normalize
- import `cargo-public-api` and `cargo-semver-checks` outputs
- emit joined schema objects

### Stage 2 — public dependency boundary
- import Cargo/rustc public/private dependency facts
- classify ambiguous boundary cases conservatively

### Stage 3 — docs readiness
- join docs/example coverage to public-surface items
- keep unstable/nightly provenance explicit

### Stage 4 — gating and waivers
- apply policy
- emit release verdicts and expiry-aware waiver receipts

### Stage 5 — release diffs and CI adoption
- compare current bundle to prior release
- expose stable CI/archive artifacts

## What should wait until later

Leave these for later unless `0.1` proves cramped without them:

- automatic changelog generation,
- full workspace-wide dashboards,
- synthetic semver reasoning beyond imported tool outputs,
- auto-fixing public/private dependency drift,
- registry-wide crawling,
- and generalized behavioral compatibility testing.

## Working rule

If a future pass tries to make **P-0483** be:

- a replacement for `cargo-semver-checks`,
- a replacement for `cargo-public-api`,
- a generic documentation score,
- or a full API governance platform,

it is drifting away from the sharper product.
