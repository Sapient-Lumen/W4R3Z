## Execution note (rev0402)
This proposal now sits under the explicit framing in `design/semantic-context-contract-2026Q1.md`.

Interpretation rule:
- the worthy contribution is a thin **semantic context contract**, not a universal index;
- the first proof point is honest **subject + lane + completeness** capture that multiple consumers can reuse;
- the ranked rollout should keep **local authoritative capture**, **public docs.rs cache**, **compiler-backed augmentation**, and **derived consumer slices** visibly distinct.


# Epic Proposal: Semantic Context Kit (`cargo semctx`)

## One-sentence pitch
Create a portable semantic data plane for Rust tooling: capture the exact build subject, record semantic input provenance across Cargo/rustdoc/compiler lanes, preserve merge/completeness truth, and let many downstream tools consume one reviewable `semctx-pack/v0` instead of rebuilding incompatible workspace indexes.

## Deliverables
- `cargo-semctx` reference implementation
- Schemas:
  - `semctx-subject/v0`
  - `resolution-context/v0`
  - `semantic-input-catalog/v0`
  - `semantic-merge-report/v0`
  - `semantic-query-report/v0`
  - `semctx-diff-report/v0`
  - `semctx-pack/v0`
- Adapters / integrations:
  - Cargo plumbing outputs (`resolve-features`, `plan-build`, related machine-facing phases)
  - `cargo metadata` / lockfile fallback lanes
  - docs.rs rustdoc JSON fetch/use lane
  - local rustdoc JSON build lane
  - optional compiler-backed lanes (`rmeta`, `rustc_public`, StableMIR attachments)
- Docs:
  - semantic-lane authority map guide
  - semantic-subject identity guide
  - merge/completeness and confidence guide
  - cache/freshness guide
  - redaction guidance for private registries and paths
  - query-catalog reference for downstream consumers

## Why now (signals)
- Cargo’s accepted plumbing goal explicitly says the current machine-facing surface is too thin and that `cargo metadata` excludes feature resolution.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- The GSoC plumbing prototype implemented `resolve-features` and `plan-build`, proving this decomposition is concrete enough to build against.
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- The July 2025 `cargo-semver-checks` update says cross-crate correctness still needs recursive active dependency features and `rmeta`-based combination, while docs.rs-hosted rustdoc JSON now makes cache reuse plausible.
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- docs.rs now hosts rustdoc JSON directly and warns consumers to check `format_version`, which makes version-aware semantic caching both possible and necessary.
  https://docs.rs/about/rustdoc-json
- StableMIR publication and `rustc_public` refactoring were explicitly undertaken so tool developers can build robust analysis/development tooling without compiler internals.
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo is actively considering schema unification to support a better `cargo fix` architecture, which is a strong signal that structured tool-consumable context is becoming a first-class Cargo concern.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- The 2025 State of Rust survey says official online docs remain the preferred canonical reference while LLM tooling and agentic/editor workflows are becoming a bigger part of how people learn and navigate Rust. That increases the value of a portable semantic context layer instead of weakening it.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## Non-goals
- Replacing rustdoc, docs.rs, Cargo, or `rustc_public`
- Building one universal global Rust code index for everyone
- Guaranteeing every query can be answered from rustdoc JSON alone
- Solving all cross-crate semantic correctness in v0
- Hiding uncertainty behind a “best effort” answer with no provenance

Execution anchors: use [`design/semantic-context-execution-blueprint-2026Q1.md`](../design/semantic-context-execution-blueprint-2026Q1.md) for the concrete artifact/command shape, [`design/semantic-context-lane-map.md`](../design/semantic-context-lane-map.md) for authority/freshness lane discipline, and [`design/semantic-context-pilot-program.md`](../design/semantic-context-pilot-program.md) for the ranked rollout so subject identity, lane provenance, query budgets, consumer handoffs, public-cache posture, and weaker assistant/editor slices remain distinct.

## Strategic value
This kit is high leverage because it converts a growing pile of promising but fragmented inputs into one reusable substrate.

The strategic point is not “build an AI thing for Rust.” It is almost the opposite: give human review, CI, docs/search fronts, IDEs, and assistant consumers **one honest semantic evidence layer** so newer machine-facing workflows stay attached to canonical Rust truth instead of drifting into hidden tool-local caches and folklore.

That helps:
- **Public API / semver tooling** stop reinventing feature-resolution and cross-crate semantic glue
- **docs/search/frontends** reuse docs.rs and local builds without hiding source/freshness/version differences
- **lint/fix/migration tools** ask questions over an explicit build subject rather than implicit tool-local caches
- **IDEs and assistants** consume bounded, attachable semantic context instead of scraping manifests, docs, and ad hoc caches separately
- **CI/review systems** diff semantic context changes directly

## Initial pilots
1. **Cross-crate semver pilot**
   - prove that one captured pack can answer “which dependency features were active?” and “which foreign item did this come from?”
2. **Docs/frontend pilot**
   - reuse docs.rs rustdoc JSON when valid, but keep local-build and format-version truth explicit
3. **Fix/lint pilot**
   - provide candidate fix/lint context from a captured semantic subject without requiring a bespoke workspace index
4. **Assistant-context pilot**
   - derive one bounded semantic context slice from the same pack, proving the data plane can serve both human review and machine consumers

## Milestones
1. **v0 subject + inputs**
   - publish `semctx-subject`, `resolution-context`, `semantic-input-catalog`
   - support local Cargo/plumbing + rustdoc JSON lanes
2. **v0.2 merge + query**
   - publish `semantic-merge-report` and an initial bounded query catalog
   - include explicit incompleteness/confidence markers
3. **v0.3 cache + diff**
   - add docs.rs cache lane, freshness rules, and `semctx-diff-report`
4. **v1 ecosystem consumers**
   - at least three materially different consumers (e.g. semver tool, docs tool, fix/lint tool) use the same pack family without sharing one bespoke hidden index

## What success looks like
- A maintainer can attach one `semctx-pack/v0` to an issue, PR, or release note and downstream tools can consume it.
- Tools can say “this answer is authoritative”, “best-effort”, or “incomplete” with structured reasons.
- local authoritative, docs.rs/public-cache, derived-slice, and compiler-backed semantic lanes can coexist without pretending they are the same thing.
- Cross-crate semantic tooling becomes easier to build without pinning everything to one exact internal Cargo or compiler architecture.

## Archive fit
This fills a real gap between existing archive kits:
- **Resolution Doctor Kit** explains why packages/features were selected.
- **MIR Analysis Kit** handles lower-level compiler export and MIR-aware analysis.
- **Public API Kit** owns semver and API verdicts.
- **Compile Guidance Kit** owns diagnostics, lint catalogs, and fix/help surfaces.
- **Ecosystem Atlas Kit** owns curated reference stacks and derived guides.

But none of those owns the portable, queryable **cross-crate semantic context** that many of them increasingly need.
That is the missing substrate this epic is meant to supply.
