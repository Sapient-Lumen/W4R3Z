# Design: Semantic Context Contract 2026Q1

## Goal
Promote the archive's existing **Semantic Context Kit** into an explicit frontier for **reviewable semantic subject and authority truth**.

The missing contribution is not another universal Rust index, another docs scraper, another editor-local cache, or an assistant-only blob.
It is one honest boundary that keeps these layers separate:
- **subject identity truth** — which workspace/package/target/profile/features/cfg/toolchain/context the claim is about;
- **authority-lane truth** — whether the answer came from local authoritative capture, public docs.rs cache, local rustdoc JSON, `cargo metadata` / lockfile fallback, `rmeta`, `rustc_public`, StableMIR, or another bounded lane;
- **merge/completeness truth** — what was combined, what stayed partial, what remained stale, and what was inferred;
- **query/result truth** — what exact semantic question was answered and with which reason-coded limits;
- **consumer slice truth** — what semver tools, docs frontends, fix workflows, IDEs, CI, or assistants are allowed to import; and
- **comparison/handoff truth** — how one semantic capture is compared, cached, diffed, redacted, and attached to later review.

That is the frontier the archive had already been circling in `design/semantic-context-kit.md` and `design/semantic-context-lane-map.md`.
This note promotes it into an explicit repo-shaping answer.

## Why this is the right frontier now
Current official Rust signals line up unusually well around this seam.

- Cargo's accepted plumbing goal says the current machine-facing surface is too porcelain-oriented, and that `cargo metadata` can include dependency resolution but excludes feature resolution. It also decomposes the build into phases including **resolve features**, **plan build**, and **stage final artifacts**.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- The `cargo-semver-checks` goal says the tool is on the critical path for eventual Cargo integration and still needs better **cross-crate item** handling and **type information**.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-semver-checks.html
- The July 2025 project-goals update says cross-crate linting now benefits from docs.rs-hosted rustdoc JSON, but still lacks recursively active dependency features from Cargo interfaces and still needs `rmeta`-based combination to get the semantics right.
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- docs.rs now builds and hosts rustdoc JSON directly, says it can be used for programmatic inspection of docs and types, and warns consumers to check `format_version` because the producer version matters.
  https://docs.rs/about/rustdoc-json
- The StableMIR publication goal says Rust wants semver-governed compiler-facing crates so tool developers can analyze compiled crates and dependencies without relying directly on compiler internals.
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- The 2025 GSoC results say `rustc_public` now has independent publication/versioning infrastructure for the Rust tooling ecosystem.
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo 1.93 says Cargo can't be everything to everyone, plugins matter, and schema work around structured outputs is being considered in part to unlock a better future fix architecture.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- The 2025 State of Rust survey says online docs remain the canonical reference while LLM/editor-mediated learning rises, which increases the value of a portable semantic context boundary instead of weakening it.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## Why this is strategically worthy
This contribution would unlock several recurring pain points at once.

### 1. Cross-crate semver work becomes honest instead of tool-local
The `cargo-semver-checks` blockers make the problem plain: a semver verdict over only one crate's rustdoc JSON is not enough for cross-crate truth. A semantic context contract would let semver tooling carry subject identity, active-feature posture, lane provenance, and partiality explicitly instead of hiding them in tool-local caches.

### 2. Docs remain canonical while machine consumers gain a bounded import layer
The survey result does not justify replacing docs with machine mediation. It justifies keeping machine mediation attached to canonical docs and code. A semantic context contract would let docs.rs caches, local builds, and compiler-backed augmentation coexist without pretending they are the same evidence.

### 3. Fix, migration, and review workflows stop rebuilding hidden semantic caches
The archive already promoted **Reviewable Edit Contract**. That promotion is stronger if fixes, migrations, and assistants can import one bounded semantic pack instead of each inventing a different workspace index or manifest/doc scrape.

### 4. Compiler-facing tooling gains a product boundary instead of a crate-story only
StableMIR and `rustc_public` are valuable, but their ecosystem impact increases when downstream tools can hand results into one subject-aware, query-aware, consumer-aware context layer instead of each defining its own input story.

### 5. Assistant use can be downgraded into bounded consumers instead of becoming the source of truth
The survey signal supports machine consumers, not machine authority. A semantic context contract is strategically valuable precisely because it gives assistants a weaker, reviewable import lane.

## What the contribution should look like in theory
The theory should stay deliberately thin.
A good v0 is not “the Rust knowledge graph.”
It is a contract family with explicit authority and completeness boundaries.

### Proposed artifact spine
- `semctx-subject/v0`
- `resolution-context/v0`
- `semantic-input-catalog/v0`
- `semantic-merge-report/v0`
- `semantic-query-report/v0`
- `semctx-diff-report/v0`
- `semctx-pack/v0`

### Authority-lane rule
The contribution should explicitly support multiple semantic lanes without flattening them:
- **local authoritative workspace capture**;
- **public docs.rs cache / release-facing lookup**;
- **fallback Cargo / lockfile approximations**;
- **compiler-backed augmentation lanes** (`rmeta`, `rustc_public`, StableMIR);
- **bounded consumer slices** for fix/lint/IDE/assistant imports.

### Layering rule
The contribution should compose **next to** these existing archive seams, not subsume them:
- **Compiler Extensibility Stack** owns compiler attachment and result-family discipline.
- **Reviewable Edit Contract** owns candidate/apply/verify truth for actual mutation.
- **Public API / semver** owns compatibility verdicts.
- **Canonical Learning** owns human-facing docs/guidance truth.
- **Semantic Context Contract** owns the attachable subject/input/merge/query/diff substrate that these consumers share.

## What the contribution should look like in practice
A serious implementation would likely look like a thin companion tool and adapter family, not a monolith:
- `cargo semctx capture` — capture a selected subject and emit `semctx-pack/v0`;
- `cargo semctx explain` — render why a semantic answer is authoritative, mixed, best-effort, or incomplete;
- `cargo semctx query` — run named queries over captured context and emit reason-coded reports;
- `cargo semctx diff` — compare two semantic captures or query results;
- `cargo semctx verify-pack` — validate digests, versions, redactions, and attachment integrity;
- `cargo semctx doctor` — identify stale lanes, mismatched formats, unsupported merges, or fallback-only answers.

Adapters should be ranked, not all built at once:
1. Cargo/plumbing + local rustdoc JSON subject capture;
2. docs.rs rustdoc JSON cache lane;
3. cross-crate semver / public-API consumer lane;
4. fix/lint/edit consumer lane;
5. compiler-backed augmentation lane;
6. IDE / assistant slices only after the earlier lanes are honest.

## Non-goals
- one universal Rust index;
- replacing Cargo, rustdoc, docs.rs, StableMIR, or `rustc_public`;
- hiding fallback inference behind “best effort” prose;
- letting assistant consumers define authority;
- flattening local authoritative capture, public cache, compiler-backed augmentation, and derived consumer slices into one confidence class.

## Ranking and repo consequence
This promotion does **not** rewrite the archive's broad ladder.
It does **not** outrank Build-State Evidence, Adoption Navigation, or Debuggability.
It does **not** replace the current Cargo-facing seams on environment, interop, or artifact handoff.

What it does do is make one under-promoted seam explicit:
**the clearest next context / authority / consumer-shaping move is now Semantic Context Kit, read through an explicit Semantic Context Contract.**

That gives the archive a better answer to a question that is only getting more central:
How should Rust let semver tools, docs fronts, compiler-attached tools, CI, IDEs, and assistants reuse semantic truth **without** smearing subject identity, lane authority, and completeness into one fake universal answer?
