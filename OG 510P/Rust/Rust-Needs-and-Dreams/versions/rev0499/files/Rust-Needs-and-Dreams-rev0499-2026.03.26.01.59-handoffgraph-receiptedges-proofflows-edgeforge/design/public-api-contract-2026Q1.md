## Execution addendum (rev0451)
For questions about what the archive's **public-boundary / exposure / semver-evidence seam** should actually ship, read `design/public-api-execution-blueprint-2026Q1.md` immediately after this note.

Interpretation rule:
- keep **Public API Contract** as the boundary contract;
- keep **Migration/Public API** as the broader release / upgrade composition answer;
- do **not** promote a new frontier here;
- and treat the new blueprint as the **execution layer** that carries subject, exposure, diff, witness, bounded-verification, and handoff truth without collapsing into one semver verdict.

## Execution addendum (rev0421)
For questions about what the archive's **release / upgrade portfolio seam** should actually ship, read `design/migration-public-api-execution-blueprint-2026Q1.md` immediately after this note.

Interpretation rule:
- keep **Public API Contract** as the release-boundary contract;
- do **not** promote a new frontier here;
- and treat the new blueprint as the **composition layer** that carries imported Public API evidence into bounded upgrade-program truth.

# Design: Public API Contract 2026Q1

## Goal
Promote the archive's existing **Public API Kit** into a first-class **Public API Contract**: a reviewable boundary for **what exact Rust public boundary is being claimed, which dependencies are deliberately or accidentally exposed through it, what changed structurally between two releases, what type-sensitive or witness-backed compatibility evidence was actually imported, what MSRV / feature / cfg / target posture bounded the claim, and what later publish / policy / distro / migration / assistant consumers may honestly conclude**.

This contract should sit:
- **above** raw rustdoc JSON files, one-off CLI diffs, ad hoc semver check screenshots, release prose, and maintainer memory;
- **below** broader distribution, publisher identity, trust, migration, and support-policy narratives; and
- **beside** Semantic Context, Compatibility Claims, Migration Truth, Publisher & Source Identity, and Distribution rather than replacing any of them.

The point is not to invent one more semver linter.
The point is to stop losing truth whenever a Rust team says “this release is semver-safe” and nobody can later tell whether that meant a public-surface diff, a public/private dependency exposure check, a witness-backed type proof, an MSRV run, or just a hopeful changelog.

## Why this seam matters now
The case for a first-class public-API contract is much stronger in 2026 than it was even a year ago:
- Rust's 2026 flagship slate keeps **public/private dependencies** and **SBOM support** in the top supply-chain band, which means API-boundary truth is now explicitly a project-level strategic surface;
- the accepted public/private-dependencies goal says the feature should help users catch unexpected exposure of implementation details and help tooling identify what constitutes an API;
- Cargo still keeps `public-dependency` and `sbom` in unstable/features space, which means the ecosystem still lacks a boring shared handoff above these lower layers;
- Cargo's changelog shows the `-Zpublic-dependency` lane is still actively evolving in `cargo add`, `cargo tree`, and manifest diagnostics;
- the 2025H2 cargo-semver-checks goal says accidental SemVer violations remain common, that Cargo wants eventual `cargo publish` integration, and that the hardest blockers are still **cross-crate items** and **type-sensitive checking**;
- that same goal says `cargo-semver-checks` only sees the target package's rustdoc JSON today, which causes many real false positives/negatives when the public API exposes foreign items;
- the GSoC 2025 witness-generation work established a concrete compiler-backed proof path for type-related SemVer breakages and is described as key to the roadmap ahead;
- docs.rs now builds and hosts rustdoc JSON directly, but its own documentation warns that `format_version` must be checked and that older releases may not yet have uniform coverage;
- Cargo's SemVer chapter still frames its rules as guidelines with major/minor/possibly-breaking classes rather than a single mechanically final verdict; and
- the existing `cargo-public-api` / `public_api` tools prove the lane is real, but they still rely on rustdoc JSON and recent nightly production of that JSON, which means the ecosystem still lacks a more portable release-boundary contract than “run a helpful tool in CI and inspect the output”.

That combination means the missing contribution is no longer “an API diff tool exists somewhere”.
It is a **portable public-boundary contract**.

## References (signals)
- Rust in 2026 / flagship themes:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Stabilize public/private dependencies:
  https://rust-lang.github.io/rust-project-goals/2025h1/pub-priv.html
- Continue resolving `cargo-semver-checks` blockers for merging into Cargo:
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- Cargo unstable features (`public-dependency`, `sbom`):
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo changelog (`-Zpublic-dependency` updates):
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- docs.rs rustdoc JSON hosting:
  https://docs.rs/about/rustdoc-json
- Cargo SemVer compatibility chapter:
  https://doc.rust-lang.org/cargo/reference/semver.html
- GSoC 2025 witness generation work:
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- `cargo-public-api` crate docs:
  https://docs.rs/crate/cargo-public-api/latest
- `public_api` crate docs:
  https://docs.rs/public-api
- Existing substrate in this repo:
  `design/public-api-kit.md`
  `design/public-api-pilot-program.md`
  `proposals/epic-public-api-kit.md`

## Working thesis
A worthy contribution here should make it easy to answer all of these without opening release PRs, CI artifacts, changelog prose, and raw rustdoc JSON side by side:
1. What exact **public boundary subject** was examined?
2. Which **declared or inferred public dependencies / exposed foreign items** mattered?
3. What **structural public-surface diff** actually occurred?
4. Which changes were only **heuristically suspicious** and which were **compiler-backed witness-proven**?
5. What **feature / cfg / target / toolchain / MSRV posture** bounded the claim?
6. What **waivers or unsupported residue** remained?
7. What later consumers may **honestly conclude** from the resulting pack?

If the design cannot answer those questions, then Rust still lacks the boring handoff that serious library evolution needs.

## Contract shape
Read the existing public-API substrate as a contract with six visibly separate layers:

### 1) Public-boundary subject truth
The contract must preserve what boundary is actually being examined:
- crate / package / workspace-member identity;
- version / baseline / comparison target identity;
- feature, cfg, target, edition, and toolchain posture;
- generator or adapter identity.

### 2) Exposure truth
The contract must preserve how the public boundary depends on other crates:
- declared public/private dependency posture when available;
- inferred exposure through reexports, signatures, trait bounds, associated types, or foreign items;
- unresolved provenance and confidence markers.

### 3) Structural-diff truth
The contract must preserve what changed structurally:
- item additions, removals, moves, renames, and signature changes;
- provenance and feature/cfg scope;
- additive vs breaking vs structurally ambiguous classification.

### 4) Witness / type-proof truth
The contract must preserve which changes were escalated to stronger proof:
- reason codes that triggered type-sensitive checking;
- witness program generation strategy;
- compiler-backed pass/fail / unsupported results;
- explicit statement that witness evidence supplements, rather than replaces, structural diffing.

### 5) Bounded verification truth
The contract must preserve how the claim was bounded:
- MSRV posture and toolchains tested;
- selected feature/cfg/target matrix policy;
- docs / rustdoc-json format compatibility posture;
- waivers and unsupported lanes.

### 6) Consumer-handoff truth
The contract must tell later consumers what they may honestly import:
- publish / release review may import the pack without scraping bespoke logs;
- migration and distro consumers may import semver/MSRV evidence without re-running every internal tool;
- policy and trust consumers may correlate to other evidence without erasing provenance;
- assistants may summarize the pack, but must not claim more authority than the pack carries.

## What the MVP should look like in theory
A realistic v0 is not “solve SemVer automatically for all Rust”.
It is:
- one subject schema for crate/workspace comparison identity;
- one exposure report that keeps declared-vs-inferred exposure visible;
- one structural API diff report;
- one semver report with stable reason codes;
- one witness/type-proof report for selected ambiguous changes;
- one MSRV / verification report; and
- one bundle that later consumers can ingest.

Required artifacts:
- `api-subject/v0`
- `api-exposure-report/v0`
- `api-diff-report/v0`
- `semver-report/v0`
- optional `api-witness-report/v0`
- optional `msrv-report/v0`
- `api-pack/v0`
- `api-handoff/v0`

Required rules:
- keep **public-boundary subject truth** distinct from **exposure truth**;
- keep **exposure truth** distinct from **structural-diff truth**;
- keep **structural-diff truth** distinct from **witness/type-proof truth**;
- keep **bounded verification truth** distinct from **consumer summaries**;
- keep **public API truth** distinct from **Migration Truth**, **Compatibility Claims**, **Publisher & Source Identity**, and **Distribution**.

## What the MVP should look like in practice
### Pilot 1 — single-crate publish/release gate
Show one pack that records the crate identity, structural diff, reason codes, selected witness checks, and MSRV result for an ordinary published library.

### Pilot 2 — workspace release group
Show one pack family that preserves per-crate truth, cross-crate exposure, and unresolved provenance for a workspace release group.

### Pilot 3 — downstream / distro intake
Show one pack that a downstream consumer can inspect for API drift, exposure drift, waivers, and matrix bounds without rerunning bespoke CI.

### Pilot 4 — migration / policy / trust import lane
Show that Migration Truth, trust/policy decisions, and release review can import API evidence without pretending they created it.

### Pilot 5 — Cargo-facing publish-check lane
Show one bounded publish-check story that could compose with eventual Cargo integration without requiring Cargo to monopolize every schema.

## Why this should be promoted instead of “just improving compatibility claims”
The archive already had strong notes on Compatibility Claims, Semantic Context, Migration Truth, public/private dependencies, and release discipline.
Those are still right, but the next sharpening move here is **not** another support matrix, another semantic cache, or another generic migration checklist.

Why this promotion is stronger than those alternatives right now:
- **Compatibility Claims** is about support-envelope truth; Public API Contract is about what library surface is actually promised across releases.
- **Semantic Context** is about acquiring/querying authority-bearing Rust semantics; Public API Contract is about packaging one bounded public-boundary verdict and its evidence.
- **Migration Truth** is about source→destination change programs; Public API Contract is one import that migration should consume, not replace.
- **Publisher & Source Identity** is about who published and by what route; Public API Contract is about what boundary they changed.
- **Distribution Contract** is about how consumers acquire/install releases; Public API Contract is about what those releases claim at the API layer.

## What would count as a worthy contribution
A worthy contribution here would look like a thin, boring, reviewable layer above the existing tool fragments:
- a reference `cargo api` / `api-pack` flow or equivalent schema-first reference implementation;
- stable reason codes that survive beyond one terminal UI;
- declared-vs-inferred exposure reporting;
- witness-backed escalation for type-sensitive changes;
- explicit matrix and waiver posture;
- and a bundle that can be attached to release, publish, distro-intake, migration, and policy workflows without pretending all consumers want the same verdict model.

That would count as genuinely ecosystem-shaping because it would:
- lower the cost of honest semver discipline for library maintainers;
- make future Cargo publish-time integration more reviewable instead of more magical;
- let downstreams consume API evidence without reverse-engineering bespoke CI;
- compose with migration, supply-chain, and support surfaces already being sharpened in this archive; and
- reduce the amount of tacit knowledge required to answer “what changed publicly, and how sure are we?”

## What should not be mistaken for the contribution
The contribution is **not**:
- one more API diff snapshot format with no portable handoff;
- one giant semver score or “safe to upgrade” badge;
- a Cargo-only monopoly that erases per-tool provenance;
- a docs.rs JSON mirror mistaken for the whole public-boundary story;
- or an assistant summary that silently claims more than the underlying evidence warrants.

## Immediate archive decision
Treat `design/public-api-kit.md` and `design/public-api-pilot-program.md` as the implementation and rollout substrate.
Treat this file as the current frontier answer for why the archive should now read that substrate as a first-class **Public API Contract**.
